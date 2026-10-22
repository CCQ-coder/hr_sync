"""Safety checks for the explicit full rebuild."""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import qms_erp_sync as sync


class SourceIdentityTests(unittest.TestCase):
    def test_existing_legacy_database_keys_require_rebuild(self):
        class Cursor:
            def execute(self, *_args):
                pass

            def fetchone(self):
                return (1,)

        client = sync.QmsDatabaseClient({
            "database_host": "localhost", "database_port": "3306",
            "database_name": "qms", "database_username": "qms", "tenant_code": "t",
        })
        record = sync.RawSourceRecord(
            "a.xls", "Sheet1", 2, "A", "ERP4:new", "hash", {},
            "qms_material", {},
        )
        with patch.object(client, "_ensure_source_table_schema"):
            with self.assertRaisesRegex(sync.SyncError, "旧版来源键"):
                client._upsert_source_records(Cursor(), "qms_material", [record])

    def test_business_number_updates_across_header_aliases_and_keeps_detail_lines(self):
        def record(file_name, headers, values):
            definitions = tuple(sync.ErpFieldDefinition(
                "qms_material_receipt", file_name, "Sheet1", header, header, column,
                column, header, index,
            ) for index, (header, column) in enumerate(zip(
                headers, ("erp_receipt_no", "erp_material_no", "erp_quantity"),
            ), 1))
            raw_data = dict(zip(headers, values))
            return next(iter(sync._source_record_pair(
                file_name, "Sheet1", 2, raw_data, raw_data, 0, False,
                sync.SourceScanStats(), "qms_material_receipt", definitions, file_name,
            )))[0]

        first = record("baseline.xls", ("入库单号", "原料编号", "数量"), ("R1", "M1", 5))
        changed = record("daily.xls", ("ylr_bh", "yuanl_bh", "shul_mq"), ("R1", "M1", 9))
        other_line = record("daily.xls", ("ylr_bh", "yuanl_bh", "shul_mq"), ("R1", "M2", 9))
        self.assertEqual(first.source_key, changed.source_key)
        self.assertNotEqual(first.row_hash, changed.row_hash)
        self.assertNotEqual(first.source_key, other_line.source_key)


class InitializationTests(unittest.TestCase):
    def test_missing_local_state_requires_rebuild(self):
        with patch.object(sync, "load_state", return_value={}):
            with self.assertRaisesRegex(sync.SyncError, "清空并重新初始化"):
                sync.synchronize_database_directory({}, False, lambda _: None)

    def test_rebuild_reads_unchanged_baseline_files(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "原料资料明细.xls"
            source.write_bytes(b"export")
            config = {"initialization_directory": str(root), "skip_initialization": False}
            _, previous = sync.build_source_scan_plan(config, {})
            groups, _ = sync.build_source_scan_plan(config, previous, force_all=True)
            self.assertEqual([source], list(groups[0].files))

    def test_clear_deletes_all_tenants_in_target_tables(self):
        statements = []

        class Cursor:
            def execute(self, statement):
                statements.append(statement)

        client = object.__new__(sync.QmsDatabaseClient)
        with patch.object(client, "_existing_source_tables", return_value={"qms_material"}):
            client._clear_target_tables(Cursor())
        self.assertEqual([
            "DELETE FROM `qms_production_batch`",
            "DELETE FROM `qms_work_order`",
            "DELETE FROM `qms_material`",
        ], statements)

    def test_old_location_key_state_requires_rebuild(self):
        with patch.object(sync, "load_state", return_value={
            sync.SOURCE_IDENTITY_VERSION_STATE_KEY: "2", "raw:old-key": "old-hash",
        }):
            with self.assertRaisesRegex(sync.SyncError, "清空并重新初始化"):
                sync.synchronize_database_directory({}, False, lambda _: None)

    def test_failed_rebuild_rolls_back_clear_and_does_not_save_progress(self):
        events = []

        class Connection:
            def cursor(self):
                return self

            def __enter__(self):
                return self

            def __exit__(self, *_args):
                return False

            def commit(self):
                events.append("commit")

            def rollback(self):
                events.append("rollback")

            def close(self):
                pass

        class Client:
            def __init__(self, _config):
                pass

            def _connect(self):
                return Connection()

            def _ensure_source_table_schema(self, *_args):
                events.append("schema")

            def _clear_target_tables(self, _cursor):
                events.append("clear")

            def _existing_source_tables(self, _cursor):
                return {"qms_material"}

            def _upsert_source_records(self, *_args, **_kwargs):
                raise sync.SyncError("write failed")

        def records(_config, _callback, stats, *, source_directory, selected_files):
            stats.files_scanned += 1
            stats.raw_records += 1
            yield sync.RawSourceRecord(
                source_file=selected_files[0].name, sheet_name="Sheet1", source_row_no=2,
                business_key="A", source_key="key", row_hash="hash", field_values={},
                source_table="qms_material", field_definitions={},
            ), None

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "baseline"
            source.mkdir()
            (source / "原料资料明细.xls").write_bytes(b"export")
            config = {"initialization_directory": str(source), "skip_initialization": False}
            with patch.object(sync, "state_path", return_value=root / "state.json"), \
                    patch.object(sync, "QmsDatabaseClient", Client), \
                    patch.object(sync, "iter_all_source_records", side_effect=records), \
                    patch.object(sync, "save_state") as save_state, \
                    patch.object(sync, "save_file_progress") as save_progress:
                with self.assertRaisesRegex(sync.SyncError, "write failed"):
                    sync.synchronize_database_directory(config, False, lambda _: None, initialize=True)
            self.assertEqual(["schema", "commit", "clear", "rollback"], events)
            save_state.assert_not_called()
            save_progress.assert_not_called()


if __name__ == "__main__":
    unittest.main()
