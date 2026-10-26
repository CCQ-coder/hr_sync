"""Safety checks for the explicit full rebuild."""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from openpyxl import Workbook

import qms_erp_sync as sync
from pymysql.cursors import RE_INSERT_VALUES


class SourceIdentityTests(unittest.TestCase):
    def test_finished_goods_receipt_uses_erp_receipt_id_before_shared_receipt_number(self):
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

    def test_raw_upsert_is_compatible_with_pymysql_multirow_insert(self):
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

    def test_existing_legacy_database_keys_require_rebuild(self):
        class Cursor:
            def execute(self, statement, *_args):
                self.statement = statement

            def fetchone(self):
                return (1,) if "NOT LIKE 'ERP5:%'" in self.statement else None

            def executemany(self, *_args):
                pass

        client = sync.QmsDatabaseClient({
            "database_host": "localhost", "database_port": "3306",
            "database_name": "qms", "database_username": "qms", "tenant_code": "t",
        })
        record = sync.RawSourceRecord(
            "a.xls", "Sheet1", 2, "A", "ERP5:new", "hash", {},
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

    def test_customer_order_occurrences_keep_identical_rows_and_match_later_exports(self):
        class Registry:
            def canonical_headers_for(self, _source_file, headers):
                return headers

            def resolve_sheet(self, table, source_file, sheet, headers):
                columns = (
                    "erp_order_no", "erp_internal_product_no",
                    "erp_delivery_date", "erp_order_placed_quantity",
                )
                return [sync.ErpFieldDefinition(
                    table, source_file, sheet, header, header, column,
                    column, header, index,
                ) for index, (header, column) in enumerate(zip(headers, columns), 1)]

        with tempfile.TemporaryDirectory() as temporary:
            exports = []
            for day, quantities in (("baseline", (4000, 7025)), ("daily", (5000, 8000))):
                folder = Path(temporary) / day
                folder.mkdir()
                path = folder / "客户订单资料.xlsx"
                workbook = Workbook()
                first = workbook.active
                first.title = "前两行"
                first.append(["订单编号", "厂内编号", "交期", "下单数量"])
                first.append(["PI1", "L1", "2025-01-17", quantities[0]])
                first.append(["PI1", "L1", "2025-03-30", quantities[1]])
                second = workbook.create_sheet("另一工作表")
                second.append(["订单编号", "厂内编号", "交期", "下单数量"])
                second.append(["PI1", "L1", "2025-03-30", quantities[1]])
                workbook.save(path)
                with patch.object(sync, "load_erp_field_registry", return_value=Registry()):
                    exports.append([record for record, _ in sync.iter_all_source_records(
                        {}, lambda _: None, sync.SourceScanStats(),
                        source_directory=folder, selected_files=(path,),
                    )])

        baseline, daily = exports
        self.assertEqual(3, len({row.source_key for row in baseline}))
        self.assertEqual([row.source_key for row in baseline], [row.source_key for row in daily])
        self.assertNotEqual(baseline[0].row_hash, daily[0].row_hash)
        self.assertTrue(all(row.source_key.startswith("ERP5:") for row in baseline))


class InitializationTests(unittest.TestCase):
    def test_header_preflight_collects_fields_without_converting_data_rows(self):
        field = sync.ErpFieldDefinition(
            "qms_purchase_order", "采购订单资料.xls", "Test", "采购单号", "采购单号",
            "erp_purchase_order_no", sync.legacy_database_column_name("采购单号"),
            sync.erp_column_comment("采购单号"), 1,
        )
        registry = sync.ErpFieldRegistry([field])
        sheet = Mock(nrows=2)
        sheet.row_values.side_effect = lambda row: ["采购单号"] if row == 0 else self.fail("read data row")
        workbook = Mock(encoding="utf-8", biff_version=80, datemode=0)
        workbook.sheet_names.return_value = ["Test"]
        workbook.sheet_by_name.return_value = sheet
        found = []
        stats = sync.SourceScanStats()
        root = Path("/tmp/erp-preflight")
        with patch.object(sync, "open_erp_xls", return_value=workbook), \
                patch.object(sync, "load_erp_field_registry", return_value=registry):
            rows = list(sync.iter_all_source_records(
                {}, lambda _: None, stats, source_directory=root,
                selected_files=[root / "采购订单资料.xls"], headers_only=True,
                on_sheet=lambda table, fields: found.append((table, fields)),
            ))
        self.assertEqual([], rows)
        self.assertEqual([("qms_purchase_order", {field.database_column: field})], found)
        self.assertEqual((1, 1, 0), (stats.files_scanned, stats.sheets_scanned, stats.raw_records))

    def test_header_preflight_skips_xlsx_data_rows(self):
        field = sync.ErpFieldDefinition(
            "qms_purchase_order", "采购订单资料.xls", "Test", "采购单号", "采购单号",
            "erp_purchase_order_no", sync.legacy_database_column_name("采购单号"),
            sync.erp_column_comment("采购单号"), 1,
        )
        registry = sync.ErpFieldRegistry([field])
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            workbook = Workbook()
            workbook.active.title = "Test"
            workbook.active.append(["采购单号"])
            workbook.active.append(["PO-1"])
            path = root / "采购订单资料.xlsx"
            workbook.save(path)
            workbook.close()
            found = []
            stats = sync.SourceScanStats()
            with patch.object(sync, "load_erp_field_registry", return_value=registry):
                rows = list(sync.iter_all_source_records(
                    {}, lambda _: None, stats, source_directory=root,
                    selected_files=[path], headers_only=True,
                    on_sheet=lambda table, fields: found.append((table, fields)),
                ))
        self.assertEqual([], rows)
        self.assertEqual([("qms_purchase_order", {field.database_column: field})], found)
        self.assertEqual(0, stats.raw_records)

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
            client._clear_target_tables(nontransactional)
        self.assertFalse(any("DELETE FROM" in sql for sql in nontransactional.statements))

        external_reference = Cursor([[("qms_material", "InnoDB")], [("other_table",)]])
        with self.assertRaisesRegex(sync.SyncError, "范围外"):
            client._clear_target_tables(external_reference)
        self.assertFalse(any("DELETE FROM" in sql for sql in external_reference.statements))

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
        with patch.object(client, "_existing_source_tables", return_value={"qms_material"}), \
                patch.object(client, "_assert_safe_clear"):
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

    def test_rebuild_replaces_older_complete_export_with_latest_in_one_transaction(self):
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

            def _upsert_source_records(self, _cursor, _table, rows, **_kwargs):
                events.append(("upsert", rows[0].source_key))

            def _delete_missing_snapshot_rows(self, _cursor, table, keys):
                events.append(("delete", table, set(keys)))
                return 0, set()

        def records(_config, _callback, stats, *, source_directory, selected_files,
                    headers_only=False, on_sheet=None):
            stats.files_scanned += 1
            if headers_only:
                on_sheet("qms_material", {})
                return
            stats.raw_records += 1
            key = selected_files[0].read_text()
            yield sync.RawSourceRecord(
                source_file=selected_files[0].as_posix(), sheet_name="Test", source_row_no=2,
                business_key=key, source_key=f"ERP5:{key}", row_hash=key,
                field_values={}, source_table="qms_material", field_definitions={},
            ), None

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            baseline = root / "baseline"
            for day, value in (("2026-10-22", "old"), ("2026-10-23", "new")):
                folder = baseline / day
                folder.mkdir(parents=True)
                (folder / "原料资料明细.xls").write_text(value)
            config = {"initialization_directory": str(baseline)}
            with patch.object(sync, "state_path", return_value=root / "state.json"), \
                    patch.object(sync, "QmsDatabaseClient", Client), \
                    patch.object(sync, "iter_all_source_records", side_effect=records):
                sync.synchronize_database_directory(config, False, lambda _: None, initialize=True)
                state = sync.load_state()
            self.assertEqual([
                "schema", "commit", "clear",
                ("upsert", "ERP5:old"),
                ("upsert", "ERP5:new"), ("delete", "qms_material", {"ERP5:new"}),
                "commit",
            ], events)
            self.assertEqual("1", state["complete-snapshot-version"])


if __name__ == "__main__":
    unittest.main()
