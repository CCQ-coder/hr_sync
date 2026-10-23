import json
import os
from pathlib import Path
import runpy
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from ini_share_sync.config import SyncConfig
from ini_share_sync.discovery import SyncCandidate
from ini_share_sync.main import run_sync
from ini_share_sync.state import candidate_key, load_state, sha256_file
from ini_share_sync.transfer import copy_as_txt


class MainTests(unittest.TestCase):
    def test_packaged_entrypoint_exits_silently_when_import_fails(self):
        """An import failure must not open a PyInstaller error dialog."""
        entry_point = Path(__file__).resolve().parents[1] / "run_ini_share_sync.py"
        original_import = __import__

        def fail_main_import(name, *args, **kwargs):
            if name == "ini_share_sync.main":
                raise ImportError("missing runtime module")
            return original_import(name, *args, **kwargs)

        with patch("builtins.__import__", side_effect=fail_main_import):
            with self.assertRaises(SystemExit) as result:
                runpy.run_path(str(entry_point), run_name="__main__")
        self.assertEqual(1, result.exception.code)

    def test_packaged_entrypoint_exits_silently_when_logging_cannot_start(self):
        """A windowless scheduled task must not show a PyInstaller error dialog."""
        entry_point = Path(__file__).resolve().parents[1] / "run_ini_share_sync.py"
        with patch("ini_share_sync.main.main", side_effect=OSError("log directory unavailable")):
            with self.assertRaises(SystemExit) as result:
                runpy.run_path(str(entry_point), run_name="__main__")
        self.assertEqual(1, result.exception.code)

    def write_config(self, root, target_root=None):
        config_path = root / "sync_config.json"
        config_path.write_text(
            json.dumps(
                {
                    "source_root": str(root / "source"),
                    "target_root": str(target_root or root / "target"),
                    "device_id": "FEIZHEN-01",
                }
            ),
            encoding="utf-8",
        )
        return config_path

    def make_source_file(self, root, job_name, content):
        job_directory = root / "source" / job_name
        job_directory.mkdir(parents=True, exist_ok=True)
        source_path = job_directory / (job_name + ".ini")
        source_path.write_bytes(content)
        return source_path

    def run_sync_with_local_destination(self, config_path, root, target_root=None):
        """Exercise real sync I/O locally while configuration tests enforce UNC separately."""
        config = SyncConfig(
            source_root=root / "source",
            target_root=target_root or root / "target",
            device_id="FEIZHEN-01",
        )
        with patch("ini_share_sync.main.load_config", return_value=config):
            return run_sync(config_path, root)

    def test_first_run_copies_unchanged_run_skips_and_changed_run_recopies(self):
        """Removing hash comparison would overwrite an unchanged target every run."""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = self.make_source_file(root, "p2l046433a", b"one")
            config_path = self.write_config(root)

            self.assertEqual(0, self.run_sync_with_local_destination(config_path, root))
            target = root / "target" / "FEIZHEN-01" / "p2l046433a.txt"
            self.assertEqual(b"one", target.read_bytes())
            first_mtime = target.stat().st_mtime_ns

            self.assertEqual(0, self.run_sync_with_local_destination(config_path, root))
            self.assertEqual(first_mtime, target.stat().st_mtime_ns)

            source.write_bytes(b"two")
            self.assertEqual(0, self.run_sync_with_local_destination(config_path, root))
            self.assertEqual(b"two", target.read_bytes())

    def test_run_log_records_source_root_and_matched_candidate_count(self):
        """A silent no-upload run must reveal whether the source scan found files."""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.make_source_file(root, "A", b"candidate")
            config_path = self.write_config(root)

            self.assertEqual(0, self.run_sync_with_local_destination(config_path, root))

            log_path = next((root / "logs").glob("sync-*.log"))
            log = log_path.read_text(encoding="utf-8")
            self.assertIn("扫描目录：{}；找到 1 个符合规则的 INI".format(root / "source"), log)

    def test_deleted_source_does_not_delete_remote_txt(self):
        """Treating the source as a mirror would violate the keep-remote-history rule."""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = self.make_source_file(root, "job", b"persist")
            config_path = self.write_config(root)
            self.assertEqual(0, self.run_sync_with_local_destination(config_path, root))
            source.unlink()

            self.assertEqual(0, self.run_sync_with_local_destination(config_path, root))

            target = root / "target" / "FEIZHEN-01" / "job.txt"
            self.assertEqual(b"persist", target.read_bytes())

    def test_failed_transfer_is_retried_after_target_becomes_available(self):
        """Writing state before a failed copy would make the job permanently skip."""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.make_source_file(root, "job", b"retry-me")
            blocked_target = root / "blocked-target"
            blocked_target.write_bytes(b"not-a-directory")
            config_path = self.write_config(root, blocked_target)

            self.assertEqual(
                2,
                self.run_sync_with_local_destination(config_path, root, blocked_target),
            )
            state_path = root / "sync_state.json"
            self.assertFalse(state_path.exists())

            blocked_target.unlink()
            self.assertEqual(
                0,
                self.run_sync_with_local_destination(config_path, root, blocked_target),
            )

            target = blocked_target / "FEIZHEN-01" / "job.txt"
            self.assertEqual(b"retry-me", target.read_bytes())

    def test_state_hash_matches_bytes_published_when_source_changes_before_copy(self):
        """Persisting the pre-copy hash could permanently desynchronise source and target."""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = self.make_source_file(root, "job", b"before-copy")
            config_path = self.write_config(root)
            config = SyncConfig(root / "source", root / "target", "FEIZHEN-01")

            def copy_after_source_changes(source_path, destination_path):
                source_path.write_bytes(b"changed-before-copy")
                return copy_as_txt(source_path, destination_path)

            with patch("ini_share_sync.main.load_config", return_value=config):
                with patch(
                    "ini_share_sync.main.copy_as_txt",
                    side_effect=copy_after_source_changes,
                ):
                    self.assertEqual(0, run_sync(config_path, root))

            target = root / "target" / "FEIZHEN-01" / "job.txt"
            state = load_state(root / "sync_state.json")
            entry = state[candidate_key(SyncCandidate("job", source))]
            target_bytes = target.read_bytes()
            target_hash = sha256_file(target)

        self.assertEqual(b"changed-before-copy", target_bytes)
        self.assertEqual(target_hash, entry["sha256"])

    def test_run_returns_overlap_exit_code_while_another_process_holds_lock(self):
        """Without a process lock, scheduled invocations could copy the same job together."""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.make_source_file(root, "job", b"content")
            config_path = self.write_config(root)
            lock_path = root / "ini_share_sync.lock"
            source_root = Path(__file__).resolve().parents[1] / "src"
            child_code = (
                "from pathlib import Path; "
                "from ini_share_sync.locking import SingleRunLock; "
                "import sys, time; "
                "lock = SingleRunLock(Path(sys.argv[1])); "
                "print('locked' if lock.acquire() else 'failed', flush=True); "
                "time.sleep(30)"
            )
            environment = os.environ.copy()
            environment["PYTHONPATH"] = str(source_root)
            process = subprocess.Popen(
                [sys.executable, "-c", child_code, str(lock_path)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=environment,
            )
            try:
                self.assertEqual("locked", process.stdout.readline().strip())
                self.assertEqual(3, self.run_sync_with_local_destination(config_path, root))
            finally:
                if process.poll() is None:
                    process.terminate()
                process.wait(timeout=10)
                process.stdout.close()
                process.stderr.close()

    def test_task_scripts_support_safe_whatif_execution(self):
        """A script encoding or parse error would make task installation/removal unusable."""
        project_root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            schtasks_path = root / "fake-schtasks.cmd"
            marker = root / "scheduler-called.txt"
            schtasks_path.write_text('@echo called> "%CAPTURE_ARGS%"\r\n', encoding="ascii")
            environment = os.environ.copy()
            environment["CAPTURE_ARGS"] = str(marker)
            executable = project_root / "dist" / "IniShareSync.exe"
            created_executable = not executable.exists()
            if created_executable:
                executable.parent.mkdir(parents=True, exist_ok=True)
                executable.write_bytes(b"test placeholder")
            try:
                for script_name in ("install_sync_task.ps1", "remove_sync_task.ps1"):
                    script_path = project_root / script_name
                    result = subprocess.run(
                        [
                            "powershell", "-NoProfile", "-ExecutionPolicy", "Bypass",
                            "-File", str(script_path), "-SchtasksPath", str(schtasks_path),
                            "-WhatIf",
                        ],
                        capture_output=True,
                        env=environment,
                    )
                    self.assertEqual(
                        0, result.returncode,
                        result.stderr.decode("utf-8", errors="replace"),
                    )
                    self.assertFalse(marker.exists(), script_name)
            finally:
                if created_executable:
                    executable.unlink()

    def test_task_scripts_create_and_remove_compatible_schtasks_jobs(self):
        """Windows 7 and XP need different schtasks command formats."""
        project_root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as directory:
            temporary_root = Path(directory)
            schtasks_path = temporary_root / "fake-schtasks.cmd"
            captured_args = temporary_root / "schtasks-args.txt"
            captured_xml = temporary_root / "task.xml"
            captured_status_xml = temporary_root / "status-task.xml"
            schtasks_path.write_text(
                "@echo off\r\n"
                "echo %*>> \"%CAPTURE_ARGS%\"\r\n"
                "if /I \"%~1\"==\"/Create\" if /I \"%~3\"==\"IniShareSync\" copy /Y \"%~5\" \"%CAPTURE_XML%\" >nul\r\n"
                "if /I \"%~1\"==\"/Create\" if /I \"%~3\"==\"IniShareSyncStatus\" copy /Y \"%~5\" \"%CAPTURE_STATUS_XML%\" >nul\r\n"
                "exit /b 0\r\n",
                encoding="ascii",
            )
            environment = os.environ.copy()
            environment["CAPTURE_ARGS"] = str(captured_args)
            environment["CAPTURE_XML"] = str(captured_xml)
            environment["CAPTURE_STATUS_XML"] = str(captured_status_xml)

            install_result = subprocess.run(
                [
                    "powershell",
                    "-NoProfile",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-File",
                    str(project_root / "install_sync_task.ps1"),
                    "-SchtasksPath",
                    str(schtasks_path),
                ],
                cwd=str(project_root),
                capture_output=True,
                env=environment,
            )
            self.assertEqual(
                0,
                install_result.returncode,
                install_result.stderr.decode("utf-8", errors="replace"),
            )
            task_xml = captured_xml.read_text(encoding="utf-8-sig")
            self.assertIn("<Interval>PT5M</Interval>", task_xml)
            self.assertIn("<MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>", task_xml)
            self.assertIn("<LogonType>InteractiveToken</LogonType>", task_xml)
            self.assertIn("<Command>", task_xml)
            self.assertIn("IniShareSync.exe</Command>", task_xml)
            self.assertIn(
                "<WorkingDirectory>{}</WorkingDirectory>".format(project_root / "dist"),
                task_xml,
            )
            status_task_xml = captured_status_xml.read_text(encoding="utf-8-sig")
            self.assertIn("<Interval>PT1M</Interval>", status_task_xml)
            self.assertIn("<Arguments>--status-only</Arguments>", status_task_xml)

            win32_bundle = project_root / "dist-win32" / "IniShareSync"
            win32_executable = win32_bundle / "IniShareSync.exe"
            created_win32_executable = not win32_executable.exists()
            if created_win32_executable:
                win32_bundle.mkdir(parents=True, exist_ok=True)
                win32_executable.write_bytes(b"test placeholder")

            win32_install_result = subprocess.run(
                [
                    "powershell",
                    "-NoProfile",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-File",
                    str(project_root / "install_sync_task.ps1"),
                    "-PackageDirectory",
                    "dist-win32",
                    "-SchtasksPath",
                    str(schtasks_path),
                ],
                cwd=str(project_root),
                capture_output=True,
                env=environment,
            )
            self.assertEqual(
                0,
                win32_install_result.returncode,
                win32_install_result.stderr.decode("utf-8", errors="replace"),
            )
            win32_task_xml = captured_xml.read_text(encoding="utf-8-sig")
            self.assertIn(
                "<Command>{}</Command>".format(win32_bundle / "IniShareSync.exe"),
                win32_task_xml,
            )
            self.assertIn(
                "<WorkingDirectory>{}</WorkingDirectory>".format(win32_bundle),
                win32_task_xml,
            )
            if created_win32_executable:
                win32_executable.unlink()

            xp32_bundle = project_root / "dist-xp32" / "IniShareSync"
            xp32_executable = xp32_bundle / "IniShareSync.exe"
            created_xp32_executable = not xp32_executable.exists()
            if created_xp32_executable:
                xp32_bundle.mkdir(parents=True, exist_ok=True)
                xp32_executable.write_bytes(b"test placeholder")

            xp32_install_result = subprocess.run(
                [
                    "powershell",
                    "-NoProfile",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-File",
                    str(project_root / "install_sync_task.ps1"),
                    "-PackageDirectory",
                    "dist-xp32",
                    "-SchtasksPath",
                    str(schtasks_path),
                ],
                cwd=str(project_root),
                capture_output=True,
                env=environment,
            )
            self.assertEqual(
                0,
                xp32_install_result.returncode,
                xp32_install_result.stderr.decode("utf-8", errors="replace"),
            )
            scheduler_commands = captured_args.read_text(encoding="utf-8")
            self.assertIn("/Create /SC MINUTE /MO 5 /TN IniShareSync /TR", scheduler_commands)
            self.assertIn("/Create /SC MINUTE /MO 1 /TN IniShareSyncStatus /TR", scheduler_commands)
            self.assertIn(
                "/Create /SC ONSTART /TN IniShareSyncStartup /TR",
                scheduler_commands,
            )
            self.assertIn(str(xp32_executable), scheduler_commands)
            self.assertIn("/F", scheduler_commands)
            if created_xp32_executable:
                xp32_executable.unlink()

            remove_result = subprocess.run(
                [
                    "powershell",
                    "-NoProfile",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-File",
                    str(project_root / "remove_sync_task.ps1"),
                    "-SchtasksPath",
                    str(schtasks_path),
                ],
                cwd=str(project_root),
                capture_output=True,
                env=environment,
            )
            self.assertEqual(
                0,
                remove_result.returncode,
                remove_result.stderr.decode("utf-8", errors="replace"),
            )
            scheduler_commands = captured_args.read_text(encoding="utf-8")
            self.assertIn("/Create /TN IniShareSync /XML", scheduler_commands)
            self.assertIn("/Query /TN IniShareSync", scheduler_commands)
            self.assertIn("/Delete /TN IniShareSync /F", scheduler_commands)
            self.assertIn("/Query /TN IniShareSyncStartup", scheduler_commands)
            self.assertIn("/Delete /TN IniShareSyncStartup /F", scheduler_commands)
            self.assertIn("/Query /TN IniShareSyncStatus", scheduler_commands)
            self.assertIn("/Delete /TN IniShareSyncStatus /F", scheduler_commands)

    def test_build_places_runtime_configuration_next_to_packaged_exe(self):
        """If the config is absent from dist, the scheduled EXE cannot find its settings."""
        project_root = Path(__file__).resolve().parents[1]
        result = subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(project_root / "build_exe.ps1"),
            ],
            cwd=str(project_root),
            capture_output=True,
        )

        self.assertEqual(
            0,
            result.returncode,
            result.stderr.decode("utf-8", errors="replace"),
        )
        self.assertTrue((project_root / "dist" / "IniShareSync.exe").is_file())
        self.assertTrue((project_root / "dist" / "sync_config.json").is_file())

    def test_win32_build_creates_x86_exe_and_runtime_configuration(self):
        """A 64-bit EXE would not run on the requested 32-bit Windows 7 host."""
        project_root = Path(__file__).resolve().parents[1]
        result = subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(project_root / "build_exe_win32.ps1"),
            ],
            cwd=str(project_root),
            capture_output=True,
        )

        self.assertEqual(
            0,
            result.returncode,
            result.stderr.decode("utf-8", errors="replace"),
        )
        bundle_directory = project_root / "dist-win32" / "IniShareSync"
        executable = bundle_directory / "IniShareSync.exe"
        self.assertTrue(executable.is_file())
        self.assertFalse((project_root / "dist-win32" / "IniShareSync.exe").exists())
        self.assertTrue((bundle_directory / "sync_config.json").is_file())
        self.assertTrue(
            (bundle_directory / "python38.dll").is_file(),
            "A Win7 bundle must ship its runtime files next to the EXE, not extract them at launch.",
        )
        with executable.open("rb") as handle:
            self.assertEqual(b"MZ", handle.read(2))
            handle.seek(0x3C)
            pe_offset = int.from_bytes(handle.read(4), byteorder="little")
            handle.seek(pe_offset)
            self.assertEqual(b"PE\x00\x00", handle.read(4))
            self.assertEqual(0x014C, int.from_bytes(handle.read(2), byteorder="little"))

    def test_xp32_build_creates_x86_folder_bundle_without_device_configuration(self):
        """An XP host cannot start a Python 3.8 runtime or a modern PyInstaller bootloader."""
        project_root = Path(__file__).resolve().parents[1]
        result = subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(project_root / "build_exe_xp32.ps1"),
            ],
            cwd=str(project_root),
            capture_output=True,
        )

        self.assertEqual(
            0,
            result.returncode,
            result.stderr.decode("utf-8", errors="replace"),
        )
        bundle_directory = project_root / "dist-xp32" / "IniShareSync"
        executable = bundle_directory / "IniShareSync.exe"
        self.assertTrue(executable.is_file())
        self.assertFalse((bundle_directory / "sync_config.json").exists())
        self.assertFalse((bundle_directory / "sync_state.json").exists())
        self.assertFalse((bundle_directory / "ini_share_sync.lock").exists())
        self.assertFalse((bundle_directory / "ini_share_sync_status.lock").exists())
        self.assertFalse((bundle_directory / "logs").exists())
        self.assertTrue((bundle_directory / "sync_config.example.json").is_file())
        self.assertTrue(
            (bundle_directory / "sync_config.example.json").read_bytes().startswith(b"\xef\xbb\xbf")
        )
        self.assertTrue((bundle_directory / "setup_tasks.cmd").is_file())
        self.assertTrue((bundle_directory / "更新说明.txt").is_file())
        self.assertTrue((bundle_directory / "python34.dll").is_file())
        with executable.open("rb") as handle:
            self.assertEqual(b"MZ", handle.read(2))
            handle.seek(0x3C)
            pe_offset = int.from_bytes(handle.read(4), byteorder="little")
            handle.seek(pe_offset)
            self.assertEqual(b"PE\x00\x00", handle.read(4))
            self.assertEqual(0x014C, int.from_bytes(handle.read(2), byteorder="little"))
            handle.seek(pe_offset + 4 + 20 + 68)
            self.assertEqual(2, int.from_bytes(handle.read(2), byteorder="little"))

        with tempfile.TemporaryDirectory() as directory:
            deployed_bundle = Path(directory) / "IniShareSync"
            shutil.copytree(str(bundle_directory), str(deployed_bundle))
            source_root = Path(directory) / "source"
            source_root.mkdir()
            config_path = deployed_bundle / "sync_config.json"
            with (deployed_bundle / "sync_config.example.json").open(encoding="utf-8-sig") as handle:
                config = json.load(handle)
            config["source_root"] = str(source_root)
            config["device_id"] = "XP-SMOKE-CHECK"
            with config_path.open("w", encoding="utf-8") as handle:
                json.dump(config, handle)
            smoke_result = subprocess.run(
                [str(deployed_bundle / "IniShareSync.exe")],
                cwd=str(deployed_bundle),
                capture_output=True,
            )
            self.assertEqual(
                0,
                smoke_result.returncode,
                smoke_result.stderr.decode("utf-8", errors="replace"),
            )
            self.assertTrue(
                list((deployed_bundle / "logs").glob("sync-*.log")),
                "The XP binary must be able to create its run-time log directory.",
            )
