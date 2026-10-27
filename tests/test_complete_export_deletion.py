"""A newer complete export replaces the prior ERP rows in its business table."""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from pymysql.converters import escape_item
from pymysql.cursors import Cursor as MySQLCursor

import qms_erp_sync as sync


COMPLETE_REPORTS = {
    "客户料号资料.XLS": "qms_customer_part",
    "原料资料明细.XLS": "qms_material",
    "成品入库单资料.XLS": "qms_finished_goods_receipt",
}


class MemoryConnection:
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


class MemoryClient:
    def __init__(self):
        self.tables = {table: {"ERP5:A", "ERP5:B"} for table in COMPLETE_REPORTS.values()}
        self.delete_calls = []

    def _connect(self):
        return MemoryConnection()

    def _upsert_source_records(self, _cursor, table, records):
        self.tables[table].update(record.source_key for record in records)

    def _delete_missing_snapshot_rows(self, _cursor, table, current_keys):
        self.delete_calls.append(table)
        removed = self.tables[table] - set(current_keys)
        self.tables[table].difference_update(removed)
        return len(removed), removed


def report_rows(_config, _callback, stats, *, source_directory, selected_files):
    path = selected_files[0]
    table = COMPLETE_REPORTS[path.name]
    stats.files_scanned += 1
    if path.read_bytes() == b"empty":
        return
    for key in (("A", "B") if "10-22" in path.parts or path.read_bytes() == b"restored" else ("A",)):
        stats.raw_records += 1
        yield sync.RawSourceRecord(
            source_file=str(path), sheet_name="Test", source_row_no=2,
            business_key=key, source_key=f"ERP5:{key}", row_hash=key,
            field_values={}, source_table=table, field_definitions={},
        ), None


class CompleteExportDeletionTests(unittest.TestCase):
    def test_legacy_recovery_deactivates_missing_new_keys_without_delete(self):
        class RecoveryClient(MemoryClient):
            def __init__(self):
                super().__init__()
                self.inactivated = []

            def _existing_source_tables(self, _cursor):
                return set()

            def _deactivate_legacy_rows_for_file(self, *_args):
                return 0

            def _deactivate_legacy_rows_for_complete_export(self, *_args):
                return 0

            def _deactivate_missing_snapshot_rows(self, _cursor, table, current_keys):
                self.inactivated.append((table, tuple(current_keys)))
                return 1, ["ERP5:B"]

            def _delete_missing_snapshot_rows(self, *_args):
                raise AssertionError("recovery must retain missing rows")

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "daily"
            source.mkdir()
            (source / "原料资料明细.XLS").write_bytes(b"newer")
            client = RecoveryClient()
            with patch.object(sync, "state_path", return_value=root / "state.json"), \
                    patch.object(sync, "iter_all_source_records", side_effect=report_rows), \
                    patch.object(sync, "QmsDatabaseClient", return_value=client):
                summary = sync.synchronize_database_directory(
                    {"skip_initialization": True, "incremental_directory": str(source)},
                    False, lambda _: None,
                )
            self.assertEqual(0, summary.deleted)
            self.assertEqual(1, summary.deactivated)
            self.assertEqual([("qms_material", ("ERP5:A",))], client.inactivated)

    def test_unchanged_latest_exports_reconcile_old_database_rows_after_upgrade(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "daily"
            previous = {
                sync.SOURCE_IDENTITY_VERSION_STATE_KEY: "5",
                "raw:ERP5:A": "A",
                "raw:ERP5:B": "B",
            }
            for day, content in (("2026-10-22", b"older"), ("2026-10-23", b"newer")):
                folder = source / day
                folder.mkdir(parents=True)
                for name in COMPLETE_REPORTS:
                    path = folder / name
                    path.write_bytes(content)
                    previous[sync.source_file_state_key("incremental", source, path)] = sync.source_file_checkpoint(path)
            client = MemoryClient()
            with patch.object(sync, "state_path", return_value=root / "state.json"), \
                    patch.object(sync, "iter_all_source_records", side_effect=report_rows), \
                    patch.object(sync, "QmsDatabaseClient", return_value=client):
                sync.save_state(previous)
                summary = sync.synchronize_database_directory(
                    {"skip_initialization": True, "incremental_directory": str(source)},
                    False, lambda _: None,
                )
                self.assertNotIn("raw:ERP5:B", sync.load_state())
                (source / "2026-10-23" / "原料资料明细.XLS").write_bytes(b"restored")
                restored = sync.synchronize_database_directory(
                    {"skip_initialization": True, "incremental_directory": str(source)},
                    False, lambda _: None,
                )
            self.assertEqual(3, summary.source_files)
            self.assertEqual(3, summary.deleted)
            self.assertEqual(1, restored.added)
            self.assertEqual({"ERP5:A", "ERP5:B"}, client.tables["qms_material"])
            self.assertTrue(all(keys == {"ERP5:A"} for table, keys in client.tables.items()
                                if table != "qms_material"))

    def test_empty_complete_export_cannot_delete_a_table(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "daily"
            source.mkdir()
            (source / "原料资料明细.XLS").write_bytes(b"empty")
            client = MemoryClient()
            with patch.object(sync, "state_path", return_value=root / "state.json"), \
                    patch.object(sync, "iter_all_source_records", side_effect=report_rows), \
                    patch.object(sync, "QmsDatabaseClient", return_value=client):
                sync.save_state({sync.SOURCE_IDENTITY_VERSION_STATE_KEY: "5"})
                with self.assertRaisesRegex(sync.SyncError, "完整导出.*没有有效数据"):
                    sync.synchronize_database_directory(
                        {"skip_initialization": True, "incremental_directory": str(source)},
                        False, lambda _: None,
                    )
            self.assertEqual({"ERP5:A", "ERP5:B"}, client.tables["qms_material"])

    def test_changed_old_baseline_replays_latest_and_only_deletes_after_latest(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "baseline"
            previous = {
                sync.SOURCE_IDENTITY_VERSION_STATE_KEY: "5",
                sync.FULL_SNAPSHOT_DELETE_STATE_KEY: sync.FULL_SNAPSHOT_DELETE_VERSION,
            }
            paths = []
            for day in ("2026-10-22", "2026-10-23"):
                path = source / day / "原料资料明细.XLS"
                path.parent.mkdir(parents=True)
                path.write_bytes(b"before")
                previous[sync.source_file_state_key("initialization", source, path)] = sync.source_file_checkpoint(path)
                paths.append(path)
            paths[0].write_bytes(b"changed")
            client = MemoryClient()
            with patch.object(sync, "state_path", return_value=root / "state.json"), \
                    patch.object(sync, "iter_all_source_records", side_effect=report_rows), \
                    patch.object(sync, "QmsDatabaseClient", return_value=client):
                sync.save_state(previous)
                summary = sync.synchronize_database_directory(
                    {"initialization_directory": str(source)}, False, lambda _: None,
                )
            self.assertEqual(2, summary.source_files)
            self.assertEqual(["qms_material"], client.delete_calls)
            self.assertEqual({"ERP5:A"}, client.tables["qms_material"])

    def test_retry_after_old_baseline_commits_still_replays_latest(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "baseline"
            previous = {
                sync.SOURCE_IDENTITY_VERSION_STATE_KEY: "5",
                sync.FULL_SNAPSHOT_DELETE_STATE_KEY: sync.FULL_SNAPSHOT_DELETE_VERSION,
            }
            paths = []
            for day in ("2026-10-22", "2026-10-23"):
                path = source / day / "原料资料明细.XLS"
                path.parent.mkdir(parents=True)
                path.write_bytes(b"before")
                previous[sync.source_file_state_key("initialization", source, path)] = sync.source_file_checkpoint(path)
                paths.append(path)
            paths[0].write_bytes(b"changed")
            client = MemoryClient()

            def fail_latest(*args, selected_files, **kwargs):
                if selected_files[0] == paths[1]:
                    raise sync.SyncError("latest unavailable")
                yield from report_rows(*args, selected_files=selected_files, **kwargs)

            with patch.object(sync, "state_path", return_value=root / "state.json"), \
                    patch.object(sync, "QmsDatabaseClient", return_value=client):
                sync.save_state(previous)
                with patch.object(sync, "iter_all_source_records", side_effect=fail_latest):
                    with self.assertRaisesRegex(sync.SyncError, "latest unavailable"):
                        sync.synchronize_database_directory(
                            {"initialization_directory": str(source)}, False, lambda _: None,
                        )
                self.assertEqual("pending", sync.load_state()[sync.FULL_SNAPSHOT_DELETE_STATE_KEY])
                with patch.object(sync, "iter_all_source_records", side_effect=report_rows):
                    summary = sync.synchronize_database_directory(
                        {"initialization_directory": str(source)}, False, lambda _: None,
                    )
            self.assertEqual(1, summary.source_files)
            self.assertEqual(["qms_material"], client.delete_calls)
            self.assertEqual({"ERP5:A"}, client.tables["qms_material"])

    def test_deletion_sql_is_tenant_scoped_and_ignores_non_erp_rows(self):
        class FormatConnection:
            def literal(self, value):
                return escape_item(value, "utf8")

        class Cursor:
            def __init__(self):
                self.calls = []
                self.rowcount = 1
                self.formatter = MySQLCursor(FormatConnection())

            def execute(self, statement, parameters):
                self.calls.append((self.formatter.mogrify(statement, parameters), parameters))

            def fetchall(self):
                return [("ERP5:A",), ("ERP5:B",)]

        client = object.__new__(sync.QmsDatabaseClient)
        client.tenant = "tenant-a"
        cursor = Cursor()
        self.assertTrue(hasattr(client, "_delete_missing_snapshot_rows"))
        deleted = client._delete_missing_snapshot_rows(cursor, "qms_material", {"ERP5:A"})
        self.assertEqual((1, ["ERP5:B"]), deleted)
        self.assertEqual(("tenant-a",), cursor.calls[0][1])
        self.assertIn("source_key` LIKE 'ERP5:%'", cursor.calls[0][0])
        self.assertIn("DELETE FROM `qms_material`", cursor.calls[1][0])
        self.assertIn("`tenant_code` = 'tenant-a'", cursor.calls[1][0])
        self.assertEqual(("tenant-a", "ERP5:B"), cursor.calls[1][1])
        invalid_cursor = Cursor()
        with self.assertRaises(sync.SyncError):
            client._delete_missing_snapshot_rows(invalid_cursor, "qms_material", {"manual-entry"})
        self.assertEqual([], invalid_cursor.calls)


if __name__ == "__main__":
    unittest.main()
