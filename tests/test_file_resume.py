"""Resume and replay complete ERP files without losing committed work."""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import pymysql

import qms_erp_sync as sync


class FileResumeTests(unittest.TestCase):
    def test_legacy_recovery_replays_files_after_interruption_without_clearing(self):
        class Connection:
            def cursor(self):
                return self

            def __enter__(self):
                return self

            def __exit__(self, *_args):
                return False

            def commit(self):
                pass

            def rollback(self):
                pass

            def close(self):
                pass

        class Client:
            def __init__(self, _config):
                self.fail_second = True
                self.deactivated = []

            def _connect(self):
                return Connection()

            def _clear_target_tables(self, _cursor):
                raise AssertionError("recovery must not clear tables")

            def _existing_source_tables(self, _cursor):
                return {"qms_material_issue"}

            def _upsert_source_records(self, _cursor, _table, records):
                if records[0].source_file.endswith("second.xls") and self.fail_second:
                    self.fail_second = False
                    raise sync.SyncError("simulated interruption")

            def _deactivate_legacy_rows_for_file(self, _cursor, table, absolute, relative):
                self.deactivated.append((table, absolute, relative))
                return 1

        def records(_config, _callback, stats, *, source_directory, selected_files):
            path = selected_files[0]
            stats.files_scanned += 1
            stats.raw_records += 1
            yield sync.RawSourceRecord(
                source_file=path.resolve().as_posix(), sheet_name="Test", source_row_no=2,
                business_key=path.stem, source_key="ERP5:" + path.stem,
                row_hash=path.stem, field_values={}, source_table="qms_material_issue",
                field_definitions={},
            ), None

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "daily"
            source.mkdir()
            first, second = source / "first.xls", source / "second.xls"
            first.write_bytes(b"first")
            second.write_bytes(b"second")
            config = {"skip_initialization": True, "incremental_directory": str(source)}
            old_state = {
                sync.source_file_state_key("incremental", source, path): sync.source_file_checkpoint(path)
                for path in (first, second)
            }
            client = Client(config)
            with patch.object(sync, "state_path", return_value=root / "state.json"), \
                    patch.object(sync, "iter_all_source_records", side_effect=records), \
                    patch.object(sync, "QmsDatabaseClient", return_value=client):
                sync.save_state(old_state)
                with self.assertRaisesRegex(sync.SyncError, "simulated interruption"):
                    sync.synchronize_database_directory(config, False, lambda _: None)
                self.assertEqual("1", sync.load_state()[sync.LEGACY_RECOVERY_PENDING_STATE_KEY])
                sync.synchronize_database_directory(config, False, lambda _: None)
                self.assertEqual("0", sync.load_state()[sync.LEGACY_RECOVERY_PENDING_STATE_KEY])
            self.assertEqual(["first.xls", "second.xls"], [
                relative for _, _, relative in client.deactivated
            ])

    def test_removed_record_updates_are_tenant_scoped(self):
        class Cursor:
            rowcount = 1

            def __init__(self):
                self.calls = []

            def execute(self, statement, parameters):
                self.calls.append((statement, parameters))

        client = object.__new__(sync.QmsDatabaseClient)
        client.tenant = "customer-zsh"
        cursor = Cursor()
        count = client._deactivate_removed_file_records(cursor, {
            "raw": {"qms_customer_part": ["old"]},
            "work_orders": ["ERP-EXCEL:old"],
            "batches": ["old-batch"],
        })
        self.assertEqual(3, count)
        self.assertEqual(3, len(cursor.calls))
        self.assertIn("`tenant_code` = %s", cursor.calls[0][0])
        self.assertEqual(("customer-zsh", "old"), cursor.calls[0][1])
        self.assertIn("`source_system` = 'ERP_EXCEL'", cursor.calls[1][0])
        self.assertIn("work_order.`source_system` = 'ERP_EXCEL'", cursor.calls[2][0])

    def test_complete_material_overwrite_deletes_missing_rows(self):
        class Connection:
            def cursor(self):
                return self

            def __enter__(self):
                return self

            def __exit__(self, *_args):
                return False

            def commit(self):
                pass

            def rollback(self):
                pass

            def close(self):
                pass

        class Client:
            def __init__(self, _config):
                self.deactivated = []
                self.rows = {"A", "B"}

            def _connect(self):
                return Connection()

            def _upsert_source_records(self, *_args, **_kwargs):
                pass

            def _deactivate_source_keys(self, _cursor, removed):
                self.deactivated.append(removed)
                return sum(map(len, removed.values()))

            def _deactivate_removed_file_records(self, _cursor, removed):
                self.deactivated.append(removed)
                return sum(map(len, removed["raw"].values()))

            def _delete_missing_snapshot_rows(self, _cursor, _table, current_keys):
                missing = self.rows - set(current_keys)
                self.rows.difference_update(missing)
                return len(missing), missing

        def records(_config, _callback, stats, *, source_directory, selected_files):
            path = selected_files[0]
            stats.files_scanned += 1
            for material in ("A", "B") if path.read_bytes() == b"full" else ("A",):
                stats.raw_records += 1
                yield sync.RawSourceRecord(
                    source_file=path.as_posix(), sheet_name="Test", source_row_no=2,
                    business_key=material, source_key=material, row_hash=material,
                    field_values={}, source_table="qms_material", field_definitions={},
                ), None

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "daily"
            source.mkdir()
            file = source / "原料资料明细.xls"
            file.write_bytes(b"full")
            config = {"skip_initialization": True, "incremental_directory": str(source)}
            client = Client(config)
            with patch.object(sync, "state_path", return_value=root / "state.json"), \
                    patch.object(sync, "iter_all_source_records", side_effect=records), \
                    patch.object(sync, "QmsDatabaseClient", return_value=client):
                sync.save_state({sync.SOURCE_IDENTITY_VERSION_STATE_KEY: "5"})
                sync.synchronize_database_directory(config, False, lambda _: None)
                file.write_bytes(b"part")
                summary = sync.synchronize_database_directory(config, False, lambda _: None)
            self.assertEqual({"A"}, client.rows)
            self.assertEqual(1, summary.deleted)
            self.assertTrue(all("qms_material" not in removed.get("raw", {})
                                for removed in client.deactivated))

    def test_overwritten_exports_only_deactivate_missing_rows_when_authoritative(self):
        class Connection:
            def cursor(self):
                return self

            def __enter__(self):
                return self

            def __exit__(self, *_args):
                return False

            def commit(self):
                pass

            def rollback(self):
                pass

            def close(self):
                pass

        class Client:
            def __init__(self, _config):
                self.removed = []

            def _connect(self):
                return Connection()

            def _upsert_source_records(self, *_args, **_kwargs):
                pass

            def _deactivate_removed_file_records(self, _cursor, removed):
                self.removed.append(removed)
                return sum(map(len, removed["raw"].values()))

        def records(_config, _callback, stats, *, source_directory, selected_files):
            path = selected_files[0]
            stats.files_scanned += 1
            for part in ("A", "B") if path.read_bytes() == b"full" else ("A",):
                stats.raw_records += 1
                yield sync.RawSourceRecord(
                    source_file=path.as_posix(), sheet_name="Test", source_row_no=2,
                    business_key=part, source_key=part, row_hash=part,
                    field_values={}, source_table=table_name, field_definitions={},
                ), None

        for filename, table_name, expected in (
            ("采购订单资料.xls", "qms_purchase_order", {"qms_purchase_order": ["B"]}),
            ("完成数量资料.xls", "qms_completion_quantity", {}),
            ("报废.xls", "qms_scrap", {}),
        ):
            with self.subTest(file=filename), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                source = root / "daily"
                source.mkdir()
                file = source / filename
                file.write_bytes(b"full")
                config = {"skip_initialization": True, "incremental_directory": str(source)}
                client = Client(config)
                with patch.object(sync, "state_path", return_value=root / "state.json"), \
                        patch.object(sync, "iter_all_source_records", side_effect=records), \
                        patch.object(sync, "QmsDatabaseClient", return_value=client):
                    sync.save_state({sync.SOURCE_IDENTITY_VERSION_STATE_KEY: "5"})
                    sync.synchronize_database_directory(config, False, lambda _: None)
                    file.write_bytes(b"part")
                    sync.synchronize_database_directory(config, False, lambda _: None)
                self.assertEqual(expected, client.removed[-1]["raw"] if client.removed else {})

    def test_same_named_files_in_different_daily_roots_have_separate_checkpoints(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            yesterday = root / "10-22"
            today = root / "10-23"
            yesterday.mkdir()
            today.mkdir()
            old = yesterday / "原料资料明细.xls"
            new = today / "原料资料明细.xls"
            old.write_bytes(b"old")
            new.write_bytes(b"new")
            self.assertNotEqual(
                sync.source_file_state_key("incremental", yesterday, old),
                sync.source_file_state_key("incremental", today, new),
            )

    def test_changed_earlier_daily_export_replays_later_exports(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            first = root / "2026-10-22" / "客户订单资料.xls"
            last = root / "2026-10-23" / "客户订单资料.xls"
            first.parent.mkdir()
            last.parent.mkdir()
            first.write_bytes(b"old")
            last.write_bytes(b"latest")
            config = {"skip_initialization": True, "incremental_directory": str(root)}
            _, state = sync.build_source_scan_plan(config, {})
            first.write_bytes(b"changed")
            groups, _ = sync.build_source_scan_plan(config, state)
            self.assertEqual([first, last], list(groups[0].files))

    def test_second_file_failure_keeps_first_file_checkpoint(self):
        class Connection:
            def __init__(self):
                self.commits = 0
                self.rollbacks = 0

            def cursor(self):
                return self

            def __enter__(self):
                return self

            def __exit__(self, *_args):
                return False

            def commit(self):
                self.commits += 1

            def rollback(self):
                self.rollbacks += 1

            def close(self):
                pass

        class Client:
            def __init__(self, _config):
                self.connections = []

            def _connect(self):
                connection = Connection()
                self.connections.append(connection)
                return connection

            def _upsert_source_records(self, _cursor, _table, records):
                if any(record.source_file.endswith("second.xls") for record in records):
                    raise pymysql.OperationalError(2013, "connection lost")

            def _deactivate_source_keys(self, *_args):
                return 0

        def records(_config, _callback, stats, *, source_directory, selected_files):
            for path in selected_files:
                stats.files_scanned += 1
                stats.raw_records += 1
                yield sync.RawSourceRecord(
                    source_file=path.as_posix(), sheet_name="Test", source_row_no=2,
                    business_key=path.name, source_key=path.name, row_hash=path.name,
                    field_values={}, source_table="qms_material", field_definitions={},
                ), None

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "daily"
            source.mkdir()
            first = source / "first.xls"
            second = source / "second.xls"
            first.write_bytes(b"first")
            second.write_bytes(b"second")
            config = {"skip_initialization": True, "incremental_directory": str(source)}
            client = Client(config)
            with patch.object(sync, "state_path", return_value=root / "state.json"), \
                    patch.object(sync, "iter_all_source_records", side_effect=records), \
                    patch.object(sync, "QmsDatabaseClient", return_value=client):
                sync.save_state({sync.SOURCE_IDENTITY_VERSION_STATE_KEY: "5"})
                with self.assertRaises(sync.SyncError):
                    sync.synchronize_database_directory(config, False, lambda _: None)
                first_key = sync.source_file_state_key("incremental", source, first)
                second_key = sync.source_file_state_key("incremental", source, second)
                state = sync.load_state()
            self.assertIn(first_key, state)
            self.assertNotIn(second_key, state)
            self.assertEqual(1, client.connections[0].commits)


if __name__ == "__main__":
    unittest.main()
