"""Full rebuild and cross-export identity for ERP source records."""

import tempfile
import unittest
import json
from pathlib import Path
from unittest.mock import Mock, patch

from openpyxl import Workbook
from pymysql.cursors import RE_INSERT_VALUES

import qms_erp_sync as sync


class SourceIdentityTests(unittest.TestCase):
    def test_finished_goods_receipt_prefers_detail_id_to_shared_receipt_number(self):
        first = {
            "erp_receipt_id_m": "DG01646538", "erp_receipt_no": "DF01173552",
            "erp_internal_product_no": "02PH02148A01", "erp_current_receipt_quantity": "100",
        }
        other_detail = {**first, "erp_receipt_id_m": "DG01646533"}
        updated = {**first, "erp_current_receipt_quantity": "200"}
        self.assertNotEqual(
            sync.erp_row_identity("qms_finished_goods_receipt", first),
            sync.erp_row_identity("qms_finished_goods_receipt", other_detail),
        )
        self.assertEqual(
            sync.erp_row_identity("qms_finished_goods_receipt", first),
            sync.erp_row_identity("qms_finished_goods_receipt", updated),
        )

    def test_source_upsert_uses_pymysql_multirow_insert(self):
        client = sync.QmsDatabaseClient(sync.DEFAULT_CONFIG)
        cursor = Mock()
        records = [sync.RawSourceRecord(
            "a.xls", "Sheet1", number, str(number), f"ERP5:{number}", "hash", {},
            "qms_material", {},
        ) for number in (2, 3)]
        client._upsert_source_records(cursor, "qms_material", records, ensure_schema=False)
        statement, rows = cursor.executemany.call_args.args
        self.assertEqual(2, len(rows))
        self.assertIsNotNone(RE_INSERT_VALUES.match(statement))

    def test_existing_legacy_database_keys_do_not_block_upsert(self):
        class Cursor:
            def execute(self, statement, *_args):
                self.statement = statement

            def fetchone(self):
                return (1,) if "NOT LIKE 'ERP5:%'" in self.statement else None

            def executemany(self, *_args):
                self.statement = _args[0]

        client = sync.QmsDatabaseClient({
            "database_host": "localhost", "database_port": "3306",
            "database_name": "qms", "database_username": "qms", "tenant_code": "t",
        })
        record = sync.RawSourceRecord(
            "a.xls", "Sheet1", 2, "A", "ERP5:new", "hash", {},
            "qms_material", {},
        )
        cursor = Cursor()
        with patch.object(client, "_ensure_source_table_schema"):
            client._upsert_source_records(cursor, "qms_material", [record])
        self.assertNotIn("NOT LIKE 'ERP5:%'", cursor.statement)

    def test_legacy_file_deactivation_is_tenant_scoped_and_keeps_rows(self):
        class Cursor:
            rowcount = 3

            def __init__(self):
                self.calls = []

            def execute(self, statement, parameters):
                self.calls.append((statement, parameters))

        client = sync.QmsDatabaseClient(sync.DEFAULT_CONFIG)
        cursor = Cursor()
        count = client._deactivate_legacy_rows_for_file(
            cursor, "qms_material", "D:/daily/原料资料明细.xls", "原料资料明细.xls",
        )
        self.assertEqual(3, count)
        statement, parameters = cursor.calls[0]
        self.assertIn("UPDATE `qms_material`", statement)
        self.assertNotIn("DELETE", statement)
        self.assertIn("`tenant_code` = %s", statement)
        self.assertEqual(client.tenant, parameters[0])
        self.assertEqual(("D:/daily/原料资料明细.xls", "原料资料明细.xls"), parameters[1:])

    def test_complete_export_deactivates_legacy_rows_in_small_batches(self):
        class Cursor:
            def __init__(self):
                self.calls = []
                self.rowcount = 0
                self.counts = iter((500, 500, 2))

            def execute(self, statement, parameters):
                self.calls.append((statement, parameters))
                self.rowcount = next(self.counts)

        client = sync.QmsDatabaseClient(sync.DEFAULT_CONFIG)
        cursor = Cursor()
        self.assertEqual(1002, client._deactivate_legacy_rows_for_complete_export(
            cursor, "qms_material",
        ))
        self.assertEqual(3, len(cursor.calls))
        for statement, parameters in cursor.calls:
            self.assertIn("LIMIT 500", statement)
            self.assertNotIn("DELETE", statement)
            self.assertEqual((client.tenant,), parameters)

    def test_recovery_snapshot_inactivates_missing_new_keys_without_delete(self):
        class Cursor:
            def __init__(self):
                self.calls = []
                self.rowcount = 1

            def execute(self, statement, parameters):
                self.calls.append((statement, parameters))

            def fetchall(self):
                return [("ERP5:A",), ("ERP5:B",)]

        client = sync.QmsDatabaseClient(sync.DEFAULT_CONFIG)
        cursor = Cursor()
        changed, missing = client._deactivate_missing_snapshot_rows(
            cursor, "qms_material", ["ERP5:A"],
        )
        self.assertEqual((1, ["ERP5:B"]), (changed, missing))
        self.assertEqual(2, len(cursor.calls))
        statement, parameters = cursor.calls[1]
        self.assertIn("SET `status` = 'INACTIVE'", statement)
        self.assertNotIn("DELETE", statement)
        self.assertEqual((client.tenant, "ERP5:B"), parameters)

    def test_overwritten_file_deactivates_only_keys_without_other_owner(self):
        first = "file-membership:source-file:initialization:a.xls"
        second = "file-membership:source-file:incremental:b.xls"
        old = {first: json.dumps({"qms_material": ["removed", "shared"]}),
               second: json.dumps({"qms_material": ["shared"]})}
        current = {first: {"qms_material": set()}}
        self.assertEqual(
            {"qms_material": {"removed"}},
            sync.removed_source_membership(old, current),
        )

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
                sync.SourceScanStats(), "qms_material_receipt", definitions, lambda _: None,
            )))[0]

        first = record("baseline.xls", ("入库单号", "原料编号", "数量"), ("R1", "M1", 5))
        changed = record("daily.xls", ("ylr_bh", "yuanl_bh", "shul_mq"), ("R1", "M1", 9))
        other_line = record("daily.xls", ("ylr_bh", "yuanl_bh", "shul_mq"), ("R1", "M2", 9))
        self.assertEqual(first.source_key, changed.source_key)
        self.assertNotEqual(first.row_hash, changed.row_hash)
        self.assertNotEqual(first.source_key, other_line.source_key)

    def test_identical_rows_in_two_exports_share_a_key(self):
        def record(file_name, row_no, value):
            return next(iter(sync._source_record_pair(
                file_name, "Sheet1", row_no, {"订单编号": value},
                {"订单编号": value}, 0, False, sync.SourceScanStats(),
                "qms_customer_order", (), lambda _: None,
            )))[0]

        first = record("baseline/客户订单资料.xls", 2, "A")
        duplicate = record("daily/客户订单资料.xls", 25, "A")
        different = record("daily/客户订单资料.xls", 26, "B")
        self.assertEqual(first.source_key, duplicate.source_key)
        self.assertNotEqual(first.source_key, different.source_key)


class InitializationPlanTests(unittest.TestCase):
    def test_source_table_creation_is_cached_across_record_batches(self):
        class Cursor:
            def __init__(self):
                self.statements = []

            def execute(self, statement, _parameters=None):
                self.statements.append(statement)

        client = sync.QmsDatabaseClient(sync.DEFAULT_CONFIG)
        cursor = Cursor()
        with patch.object(client, "_read_table_columns", return_value={}), \
                patch.object(client, "_ensure_erp_columns"):
            client._ensure_source_table_schema(cursor, "qms_material", {})
            client._ensure_source_table_schema(cursor, "qms_material", {})
        self.assertEqual(1, sum("CREATE TABLE" in sql for sql in cursor.statements))

    def test_header_preflight_resolves_fields_without_reading_data_rows(self):
        field = sync.ErpFieldDefinition(
            "qms_material", "原料资料明细.xlsx", "Test", "原料编号", "原料编号",
            "erp_material_no", sync.legacy_database_column_name("原料编号"),
            sync.erp_column_comment("原料编号"), 1,
        )
        schema = sync.ResolvedSourceSchema(
            (sync.normalize_header("原料编号"),), False, "qms_material", (field,),
        )
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            path = root / "原料资料明细.xlsx"
            workbook = Workbook()
            workbook.active.title = "Test"
            workbook.active.append(["原料编号"])
            workbook.active.append(["M1"])
            workbook.save(path)
            workbook.close()
            found = []
            stats = sync.SourceScanStats()
            with patch.object(sync, "load_erp_field_registry", return_value=Mock()), \
                    patch.object(sync, "resolve_source_schema", return_value=schema), \
                    patch.object(sync, "xlsx_safe_cell", side_effect=AssertionError("read data row")):
                rows = list(sync.iter_all_source_records(
                    {}, lambda _: None, stats, source_directory=root,
                    selected_files=(path,), headers_only=True,
                    on_sheet=lambda table, fields: found.append((table, fields)),
                ))
        self.assertEqual([], rows)
        self.assertEqual([("qms_material", {"erp_material_no": field})], found)
        self.assertEqual((1, 1, 0), (stats.files_scanned, stats.sheets_scanned, stats.raw_records))

    def test_clear_rejects_nontransactional_tables_and_external_dependents(self):
        class Cursor:
            def __init__(self, answers):
                self.answers = iter(answers)
                self.statements = []

            def execute(self, statement, *_args):
                self.statements.append(statement)

            def fetchall(self):
                return next(self.answers)

        client = object.__new__(sync.QmsDatabaseClient)
        nontransactional = Cursor([[("qms_material", "MyISAM")]])
        with self.assertRaisesRegex(sync.SyncError, "InnoDB"):
            client._clear_target_tables(nontransactional, lambda _: None)
        self.assertFalse(any("DELETE FROM" in sql for sql in nontransactional.statements))

        external_reference = Cursor([[("qms_material", "InnoDB")], [("other_table",)]])
        with self.assertRaisesRegex(sync.SyncError, "范围外"):
            client._clear_target_tables(external_reference, lambda _: None)
        self.assertFalse(any("DELETE FROM" in sql for sql in external_reference.statements))

    def test_missing_or_legacy_state_enters_recovery_without_clearing(self):
        for old_state in ({}, {"raw:old-key": "old-hash"}):
            with self.subTest(old_state=old_state), \
                    patch.object(sync, "load_state", return_value=old_state), \
                    patch.object(sync, "build_source_scan_plan", return_value=([], {})) as plan:
                sync.synchronize_database_directory({}, False, lambda _: None)
                self.assertFalse(plan.call_args.kwargs["force_all"])

    def test_full_rebuild_reads_every_file_even_if_checkpoint_is_unchanged(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            baseline = root / "baseline"
            baseline.mkdir()
            source = baseline / "客户订单资料.xls"
            source.write_bytes(b"export")
            config = {"initialization_directory": str(baseline), "skip_initialization": False}
            _, previous = sync.build_source_scan_plan(config, {})
            groups, _ = sync.build_source_scan_plan(config, previous, force_all=True)
            self.assertEqual([source], list(groups[0].files))

    def test_clear_deletes_both_qms_tables_and_every_existing_source_table(self):
        statements = []
        progress = []

        class Cursor:
            def execute(self, statement):
                statements.append(statement)
                self.rowcount = {
                    "`qms_production_batch`": 5,
                    "`qms_work_order`": 12,
                    "`qms_customer_order`": 0,
                    "`qms_material`": 200,
                }[statement.split("FROM ")[1]]

        client = object.__new__(sync.QmsDatabaseClient)
        with patch.object(client, "_existing_source_tables", return_value={"qms_material", "qms_customer_order"}), \
                patch.object(client, "_assert_safe_clear"):
            client._clear_target_tables(Cursor(), progress.append)
        self.assertEqual([
            "DELETE FROM `qms_production_batch`",
            "DELETE FROM `qms_work_order`",
            "DELETE FROM `qms_customer_order`",
            "DELETE FROM `qms_material`",
        ], statements)
        self.assertEqual([
            "正在清空目标表 qms_production_batch…",
            "目标表 qms_production_batch 已删除 5 行（待初始化完成后提交）。",
            "正在清空目标表 qms_work_order…",
            "目标表 qms_work_order 已删除 12 行（待初始化完成后提交）。",
            "正在清空目标表 qms_customer_order…",
            "目标表 qms_customer_order 已删除 0 行（待初始化完成后提交）。",
            "正在清空目标表 qms_material…",
            "目标表 qms_material 已删除 200 行（待初始化完成后提交）。",
        ], progress)

    def test_failed_rebuild_rolls_back_the_table_clear(self):
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

            def _clear_target_tables(self, _cursor, _callback):
                events.append("clear")

            def _upsert_source_records(self, *_args, **_kwargs):
                raise sync.SyncError("write failed")

        def records(_config, _callback, stats, *, source_directory, selected_files,
                    headers_only=False, on_sheet=None):
            stats.files_scanned += 1
            if headers_only:
                on_sheet("qms_material", {})
                return
            stats.raw_records += 1
            yield sync.RawSourceRecord(
                source_file=selected_files[0].name, sheet_name="Sheet1", source_row_no=2,
                business_key="A", source_key="key", row_hash="hash", field_values={},
                source_table="qms_material", field_definitions={},
            ), None

        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "baseline"
            source.mkdir()
            (source / "原料资料明细.xls").write_bytes(b"export")
            config = {"initialization_directory": str(source), "skip_initialization": False}
            with patch.object(sync, "QmsDatabaseClient", Client), \
                    patch.object(sync, "iter_all_source_records", side_effect=records), \
                    patch.object(sync, "save_state") as save_state:
                with self.assertRaisesRegex(sync.SyncError, "write failed"):
                    sync.synchronize_database_directory(config, False, lambda _: None, initialize=True)
            self.assertEqual(["schema", "commit", "clear", "rollback"], events)
            save_state.assert_not_called()

    def test_closed_connection_during_rebuild_reports_original_error(self):
        import pymysql

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
                raise pymysql.InterfaceError(0, "")

            def close(self):
                raise pymysql.InterfaceError(0, "")

        class Client:
            def __init__(self, _config):
                pass

            def _connect(self):
                return Connection()

            def _clear_target_tables(self, _cursor, _callback):
                raise pymysql.OperationalError(2013, "connection lost while clearing")

        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "baseline"
            source.mkdir()
            (source / "原料资料明细.xls").write_bytes(b"export")
            config = {"initialization_directory": str(source), "skip_initialization": False}
            with patch.object(sync, "QmsDatabaseClient", Client), \
                    patch.object(sync, "iter_all_source_records", return_value=iter(())), \
                    patch.object(sync, "save_state") as save_state:
                with self.assertRaisesRegex(sync.SyncError, "connection lost while clearing") as raised:
                    sync.synchronize_database_directory(config, False, lambda _: None, initialize=True)
            self.assertIn("数据库结果未确认", str(raised.exception))
            save_state.assert_not_called()


if __name__ == "__main__":
    unittest.main()
