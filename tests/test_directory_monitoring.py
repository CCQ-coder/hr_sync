"""Behavioral coverage for the desktop directory monitor configuration."""

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import qms_erp_sync as sync


class DirectoryFingerprintTests(unittest.TestCase):
    def test_daily_folders_are_processed_in_calendar_order(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            expected = []
            for folder in ("2026-9-17", "2026-10-1", "2027-1-2"):
                target = root / folder / "采购订单资料.XLS"
                target.parent.mkdir(parents=True)
                target.write_bytes(folder.encode("ascii"))
                expected.append(target)
            self.assertEqual(expected, sync.candidate_files(root))

    def test_scan_plan_separates_baseline_and_date_folder_deltas(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            initialization = root / "initial"
            incremental = root / "incremental"
            initialization.mkdir()
            (incremental / "2026-9-17").mkdir(parents=True)
            baseline = initialization / "客户订单资料.xls"
            delta = incremental / "2026-9-17" / "客户订单资料.XLS"
            baseline.write_bytes(b"baseline")
            delta.write_bytes(b"delta")
            config = {
                "initialization_directory": str(initialization),
                "incremental_directory": str(incremental),
                "skip_initialization": False,
            }

            groups, checkpoints = sync.build_source_scan_plan(config, {})
            self.assertEqual(["initialization", "incremental"], [group.role for group in groups])
            self.assertEqual([baseline], list(groups[0].files))
            self.assertEqual([delta], list(groups[1].files))

            groups, _ = sync.build_source_scan_plan(config, checkpoints)
            self.assertEqual([], groups)

            delta.write_bytes(b"changed-delta")
            stat = delta.stat()
            os.utime(delta, ns=(stat.st_atime_ns, stat.st_mtime_ns + 1_000_000))
            groups, current_checkpoints = sync.build_source_scan_plan(config, checkpoints)
            self.assertEqual(["incremental"], [group.role for group in groups])
            self.assertEqual([delta], list(groups[0].files))
            checkpoints.update(current_checkpoints)

            baseline.write_bytes(b"changed-baseline")
            stat = baseline.stat()
            os.utime(baseline, ns=(stat.st_atime_ns, stat.st_mtime_ns + 1_000_000))
            groups, _ = sync.build_source_scan_plan(config, checkpoints)
            self.assertEqual(["initialization", "incremental"], [group.role for group in groups])
            self.assertEqual([delta], list(groups[1].files))

    def test_skip_initialization_does_not_require_or_scan_the_baseline(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            incremental = Path(temporary) / "incremental"
            date_folder = incremental / "2026-9-17"
            date_folder.mkdir(parents=True)
            delta = date_folder / "生产指示资料.XLS"
            delta.write_bytes(b"delta")
            groups, _ = sync.build_source_scan_plan({
                "initialization_directory": "Z:/missing-baseline",
                "incremental_directory": str(incremental),
                "skip_initialization": True,
            }, {})
            self.assertEqual(["incremental"], [group.role for group in groups])
            self.assertEqual([delta], list(groups[0].files))

    def test_successful_checkpoints_make_an_unchanged_run_a_database_free_noop(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            initialization = Path(temporary) / "initial"
            initialization.mkdir()
            workbook = initialization / "客户订单资料.xls"
            workbook.write_bytes(b"checkpoint-only")
            config = {
                "initialization_directory": str(initialization),
                "incremental_directory": "",
                "skip_initialization": False,
            }
            _, checkpoints = sync.build_source_scan_plan(config, {})
            checkpoints[sync.SOURCE_IDENTITY_VERSION_STATE_KEY] = "5"
            with patch.object(sync, "load_state", return_value=checkpoints), \
                    patch.object(sync, "QmsDatabaseClient", side_effect=AssertionError("database should not open")):
                summary = sync.synchronize_database_directory(config, False, lambda _: None)
            self.assertEqual(0, summary.source_files)
            self.assertEqual(0, summary.rows_read)

    def test_excel_file_change_and_delete_change_the_directory_fingerprint(self) -> None:
        """Changing an ERP Excel file must make the monitor request a sync."""
        fingerprint = getattr(sync, "directory_fingerprint", None)
        self.assertTrue(callable(fingerprint), "directory monitor fingerprint is missing")

        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            workbook = directory / "采购订单资料.xls"
            workbook.write_bytes(b"one")
            baseline = fingerprint(directory)

            (directory / "忽略.txt").write_text("not an Excel source", encoding="utf-8")
            self.assertEqual(baseline, fingerprint(directory))

            workbook.write_bytes(b"two")
            stat = workbook.stat()
            os.utime(workbook, ns=(stat.st_atime_ns, stat.st_mtime_ns + 1_000_000))
            self.assertNotEqual(baseline, fingerprint(directory))

            workbook.unlink()
            self.assertNotEqual(baseline, fingerprint(directory))

    def test_same_size_and_mtime_overwrite_changes_checkpoint_and_monitor(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            workbook = root / "采购订单资料.xls"
            workbook.write_bytes(b"before")
            original = workbook.stat()
            config = {"skip_initialization": True, "incremental_directory": str(root)}
            _, previous = sync.build_source_scan_plan(config, {})
            fingerprint = sync.directory_fingerprint(root)

            workbook.write_bytes(b"after!")
            os.utime(workbook, ns=(original.st_atime_ns, original.st_mtime_ns))
            self.assertEqual(original.st_size, workbook.stat().st_size)
            self.assertEqual(original.st_mtime_ns, workbook.stat().st_mtime_ns)

            groups, _ = sync.build_source_scan_plan(config, previous)
            self.assertEqual([workbook], [path for group in groups for path in group.files])
            self.assertNotEqual(fingerprint, sync.directory_fingerprint(root))

    def test_monitor_detects_a_change_after_a_sync_started(self) -> None:
        """A later file edit remains pending after the current sync completes."""
        monitor_class = getattr(sync, "DirectoryChangeMonitor", None)
        self.assertTrue(callable(monitor_class), "directory change monitor is missing")

        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            workbook = directory / "生产指示资料.xls"
            workbook.write_bytes(b"first")
            monitor = monitor_class(directory, "")
            start_fingerprint = monitor.capture_sync_start()
            self.assertFalse(monitor.has_changed())

            workbook.write_bytes(b"second")
            stat = workbook.stat()
            os.utime(workbook, ns=(stat.st_atime_ns, stat.st_mtime_ns + 1_000_000))
            monitor.mark_synchronized(start_fingerprint)
            self.assertTrue(monitor.has_changed())


class DesktopConfigurationTests(unittest.TestCase):
    def test_old_source_directory_config_migrates_to_initialization_directory(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "qms_erp_sync_config.json"
            target.write_text('{"source_directory":"D:/ERP/legacy"}', encoding="utf-8")
            with patch.object(sync, "config_path", return_value=target):
                result = sync.load_config()
            self.assertEqual("D:/ERP/legacy", result["initialization_directory"])
            self.assertEqual("", result["incremental_directory"])
            self.assertFalse(result["skip_initialization"])

    def test_desktop_options_preserve_database_config_but_disable_delete_sync(self) -> None:
        """The hidden database settings remain usable while deletion stays off."""
        build_config = getattr(sync, "build_desktop_config", None)
        self.assertTrue(callable(build_config), "desktop configuration builder is missing")

        result = build_config(
            {
                "database_host": "10.1.2.3",
                "database_port": "3306",
                "database_username": "qms_sync",
                "database_password": "secret",
                "deactivate_missing": True,
            },
            initialization_directory="D:/ERP/初始化",
            incremental_directory="D:/ERP/增量",
            skip_initialization=True,
            auto_sync_enabled=True,
            auto_sync_interval_minutes="0",
        )

        self.assertEqual("10.1.2.3", result["database_host"])
        self.assertEqual("qms_sync", result["database_username"])
        self.assertEqual("D:/ERP/初始化", result["source_directory"])
        self.assertEqual("D:/ERP/初始化", result["initialization_directory"])
        self.assertEqual("D:/ERP/增量", result["incremental_directory"])
        self.assertTrue(result["skip_initialization"])
        self.assertTrue(result["auto_sync_enabled"])
        self.assertEqual(1, result["auto_sync_interval_minutes"])
        self.assertFalse(result["deactivate_missing"])


if __name__ == "__main__":
    unittest.main()
