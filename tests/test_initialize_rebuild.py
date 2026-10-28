"""Full rebuild and cross-export identity for ERP source records."""

import tempfile
import unittest
import json
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

from openpyxl import Workbook
from pymysql.cursors import RE_INSERT_VALUES

import qms_erp_sync as sync


class SourceIdentityTests(unittest.TestCase):
    def test_material_issue_keeps_receipt_details_distinct_across_exports(self):
        columns = (
            ("出库单明细ID", "erp_material_issue_detail_id"),
            ("入库单明细ID编号", "erp_receipt_detail_id_no"),
            ("出库重量", "erp_issue_weight"),
        )

        def record(file_name, row_no, receipt_detail, weight):
            definitions = tuple(sync.ErpFieldDefinition(
                "qms_material_issue", file_name, "Test", header, header, column,
                column, header, index,
            ) for index, (header, column) in enumerate(columns, 1))
            raw_data = dict(zip((header for header, _ in columns),
                                ("ISSUE-1", receipt_detail, weight)))
            return next(iter(sync._source_record_pair(
                file_name, "Test", row_no, raw_data, raw_data, 0, False,
                sync.SourceScanStats(), "qms_material_issue", definitions,
                lambda _: None,
            )))[0]

        first = record("baseline/原料出库单资料.xls", 2, "RECEIPT-1", 10)
        second = record("baseline/原料出库单资料.xls", 3, "RECEIPT-2", 10)
        changed = record("daily/原料出库单资料.xls", 25, "RECEIPT-1", 20)
        self.assertNotEqual(first.source_key, second.source_key)
        self.assertEqual(first.source_key, changed.source_key)
        self.assertNotEqual(first.row_hash, changed.row_hash)

    def test_material_issue_without_receipt_detail_keeps_existing_fallback(self):
        first = {"erp_material_issue_detail_id": "ISSUE-1", "erp_issue_weight": "10"}
        changed = {**first, "erp_issue_weight": "20"}
        self.assertEqual(
            sync.erp_row_identity("qms_material_issue", first),
            sync.erp_row_identity("qms_material_issue", changed),
        )

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
        self.assertIn("FORCE INDEX (`uq_427354425f7dfe1e_source`)", cursor.calls[0][0])
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
    def test_single_excel_rebuild_does_not_scan_incremental_directory(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            selected = root / "原料出库单资料.xls"
            selected.write_bytes(b"selected")
            daily = root / "daily"
            daily.mkdir()
            (daily / "客户订单资料.xls").write_bytes(b"unrelated")
            groups, _ = sync.build_source_scan_plan(
                {"initialization_directory": str(selected), "incremental_directory": str(daily)},
                {}, force_all=True, initialization_only=True,
            )
            self.assertEqual([("initialization", root, (selected,))], [
                (group.role, group.directory, group.files) for group in groups
            ])

    def test_single_excel_clear_does_not_touch_other_tables(self):
        statements = []

        class Cursor:
            rowcount = 1

            def execute(self, statement, _parameters=()):
                statements.append(statement)

            def fetchall(self):
                return [("row-1",)] if len(statements) == 1 else []

        client = object.__new__(sync.QmsDatabaseClient)
        with patch.object(client, "_assert_safe_clear"):
            client._clear_target_tables(
                Cursor(), lambda _: None, target_tables={"qms_material"},
            )
        self.assertTrue(any("DELETE FROM `qms_material`" in sql for sql in statements))
        self.assertFalse(any("qms_work_order" in sql or "qms_customer_order" in sql
                             for sql in statements))

    def test_single_excel_clear_preserves_other_files_in_shared_table(self):
        calls = []

        class Cursor:
            rowcount = 1

            def execute(self, statement, parameters=()):
                calls.append((statement, parameters))

            def fetchall(self):
                statement, parameters = calls[-1]
                if "SELECT DISTINCT `tenant_code`" in statement:
                    return [("tenant-a",), ("tenant-b",)]
                if "SELECT `id`" in statement and parameters[0] == "tenant-b" and len(parameters) == 2:
                    return [("selected-row",)]
                return []

        selected = Path("/tmp/原料出库单资料.xls")
        client = object.__new__(sync.QmsDatabaseClient)
        with patch.object(client, "_assert_safe_clear"):
            client._clear_target_tables(
                Cursor(), lambda _: None,
                target_tables={"qms_material_issue"}, selected_file=selected,
            )
        selects = [(sql, args) for sql, args in calls if "SELECT `id`" in sql]
        self.assertEqual({"tenant-a", "tenant-b"}, {args[0] for _, args in selects})
        self.assertTrue(all("WHERE `tenant_code` = %s AND `source_file` = %s" in sql
                            and args[1] == selected.resolve().as_posix() for sql, args in selects))
        self.assertEqual([("selected-row",)], [args for sql, args in calls if "DELETE FROM" in sql])

    def test_initialization_file_picker_accepts_excel(self):
        app = Mock()
        app.initialization_var.get.return_value = "/tmp"
        with patch.object(sync.filedialog, "askopenfilename", return_value="/tmp/报废.xls"):
            sync.SyncApplication._choose_initialization_file(app)
        app.initialization_var.set.assert_called_once_with("/tmp/报废.xls")

    def test_single_excel_rebuild_preserves_other_file_state_and_clears_its_table(self):
        class Connection:
            def cursor(self):
                return self

            def __enter__(self):
                return self

            def __exit__(self, *_args):
                return False

            def execute(self, _statement):
                pass

            def commit(self):
                pass

            def close(self):
                pass

        class Client:
            def __init__(self):
                self.cleared = []

            def _connect(self):
                return Connection()

            def _ensure_source_table_schema(self, *_args):
                pass

            def _clear_target_tables(self, _cursor, _callback, **scope):
                self.cleared.append(scope)

            def _upsert_source_records(self, *_args, **_kwargs):
                pass

        def records(_config, _callback, stats, *, selected_files, on_sheet=None, **_kwargs):
            self.assertEqual(selected, selected_files[0])
            if on_sheet:
                on_sheet("qms_scrap", {})
            stats.files_scanned += 1
            stats.raw_records += 1
            yield sync.RawSourceRecord(
                str(selected), "Test", 2, "A", "ERP5:A", "hash", {}, "qms_scrap", {},
            ), None

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            selected = root / "报废.xls"
            selected.write_bytes(b"selected")
            daily = root / "daily"
            daily.mkdir()
            other = daily / "客户订单资料.xls"
            other.write_bytes(b"other")
            other_key = sync.source_file_state_key("incremental", daily, other)
            client = Client()
            with patch.object(sync, "state_path", return_value=root / "state.json"), \
                    patch.object(sync, "QmsDatabaseClient", return_value=client), \
                    patch.object(sync, "iter_all_source_records", side_effect=records):
                sync.save_state({other_key: sync.source_file_checkpoint(other), "raw:other": "old"})
                summary = sync.synchronize_database_directory(
                    {"initialization_directory": str(selected), "incremental_directory": str(daily)},
                    False, lambda _: None, initialize=True,
                )
                state = sync.load_state()
            self.assertEqual(1, summary.source_files)
            self.assertEqual([{"target_tables": {"qms_scrap"}, "selected_file": selected}], client.cleared)
            self.assertEqual("old", state["raw:other"])
            self.assertEqual(sync.source_file_checkpoint(other), state[other_key])

    def test_empty_single_excel_never_clears_database(self):
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "报废.xls"
            source.write_bytes(b"empty")
            client = Mock()
            with patch.object(sync, "load_state", return_value={}), \
                    patch.object(sync, "QmsDatabaseClient", return_value=client), \
                    patch.object(sync, "iter_all_source_records", return_value=iter(())):
                with self.assertRaisesRegex(sync.SyncError, "没有有效数据.*尚未清空"):
                    sync.synchronize_database_directory(
                        {"initialization_directory": str(source)}, False,
                        lambda _: None, initialize=True,
                    )
            client._connect.assert_not_called()

    def test_single_production_excel_targets_work_orders_and_batches(self):
        connection = MagicMock()
        connection.cursor.return_value.__enter__.return_value = connection
        client = Mock()
        client._connect.return_value = connection
        client._upsert_work_order.return_value = "work-order-id"

        def records(_config, _callback, stats, *, on_sheet=None, **_kwargs):
            if on_sheet:
                on_sheet("qms_work_order", {})
            stats.files_scanned += 1
            stats.raw_records += 1
            stats.work_order_records += 1
            yield sync.RawSourceRecord(
                "生产指示资料.xls", "Test", 2, "WO1", "ERP5:WO1", "hash", {}, None, {},
            ), {"sourceKey": "ERP-EXCEL:WO1", "workOrderNo": "WO1", "batchNo": "B1"}

        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "生产指示资料.xls"
            source.write_bytes(b"work-order")
            with patch.object(sync, "load_state", return_value={}), \
                    patch.object(sync, "save_state"), \
                    patch.object(sync, "clear_file_progress"), \
                    patch.object(sync, "QmsDatabaseClient", return_value=client), \
                    patch.object(sync, "iter_all_source_records", side_effect=records):
                sync.synchronize_database_directory(
                    {"initialization_directory": str(source)}, False,
                    lambda _: None, initialize=True,
                )
        self.assertEqual(
            {"qms_work_order", "qms_production_batch"},
            client._clear_target_tables.call_args.kwargs["target_tables"],
        )

    def test_xls_reader_uses_staged_file(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "原料入库单资料.XLS"
            staged = root / "staged.XLS"
            source.write_bytes(b"source")
            staged.write_bytes(b"snapshot")
            with patch.object(sync, "load_erp_field_registry", return_value=Mock()), \
                    patch.object(sync, "open_legacy_compatible_xls", side_effect=ValueError("stop")) as opener:
                with self.assertRaisesRegex(sync.SyncError, "无法打开 Excel"):
                    list(sync.iter_all_source_records(
                        {}, lambda _: None, sync.SourceScanStats(),
                        source_directory=root, selected_files=(source,), read_path=staged,
                    ))
            opener.assert_called_once_with(staged)

    def test_snapshot_rejects_export_replaced_during_copy(self):
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "export.xls"
            staged = Path(temporary) / "staged.xls"
            source.write_bytes(b"before")
            real_copy = sync.shutil.copyfile

            def overwrite_after_copy(original, target):
                real_copy(original, target)
                source.write_bytes(b"after")

            with patch.object(sync.shutil, "copyfile", side_effect=overwrite_after_copy):
                with self.assertRaisesRegex(sync.SyncError, "复制期间发生覆盖.*数据库尚未清空"):
                    sync.snapshot_source_file(source, staged)

    def test_rebuild_imports_fixed_copy_when_export_changes_after_clear(self):
        class Connection:
            def cursor(self):
                return self

            def __enter__(self):
                return self

            def __exit__(self, *_args):
                return False

            def execute(self, _statement):
                pass

            def commit(self):
                pass

            def rollback(self):
                pass

            def close(self):
                pass

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source_dir = root / "baseline"
            source_dir.mkdir()
            source = source_dir / "其他资料.xlsx"

            def write_export(value):
                workbook = Workbook()
                workbook.active.title = "Test"
                workbook.active.append(["编号"])
                workbook.active.append([value])
                workbook.save(source)
                workbook.close()

            write_export("A")
            first_checkpoint = sync.source_file_checkpoint(source)
            field = sync.ErpFieldDefinition(
                "qms_erp_unclassified", source.name, "Test", "编号", "编号",
                "erp_no", "erp_no", "Excel列名：编号", 1,
            )
            schema = sync.ResolvedSourceSchema(
                (sync.normalize_header("编号"),), False, "qms_erp_unclassified", (field,),
            )

            class Client:
                rows = []
                clear_calls = 0

                def _connect(self):
                    return Connection()

                def _ensure_source_table_schema(self, *_args):
                    pass

                def _clear_target_tables(self, _cursor, _callback):
                    self.clear_calls += 1
                    write_export("B")

                def _upsert_source_records(self, _cursor, _table, records, **_kwargs):
                    self.rows.extend(records)

            client = Client()
            opened = []
            actual_load_workbook = sync.load_workbook

            def track_workbook(path, **kwargs):
                opened.append(Path(path))
                return actual_load_workbook(path, **kwargs)

            with patch.object(sync, "state_path", return_value=root / "state.json"), \
                    patch.object(sync, "QmsDatabaseClient", return_value=client), \
                    patch.object(sync, "load_erp_field_registry", return_value=Mock()), \
                    patch.object(sync, "resolve_source_schema", return_value=schema), \
                    patch.object(sync, "load_workbook", side_effect=track_workbook):
                sync.synchronize_database_directory(
                    {"initialization_directory": str(source_dir)}, False,
                    lambda _: None, initialize=True,
                )
                saved = sync.load_state()

            file_key = sync.source_file_state_key("initialization", source_dir, source)
            self.assertEqual(1, client.clear_calls)
            self.assertEqual("A", client.rows[0].field_values["erp_no"])
            self.assertEqual(source.resolve().as_posix(), client.rows[0].source_file)
            self.assertEqual(first_checkpoint, saved[file_key])
            self.assertNotEqual(first_checkpoint, sync.source_file_checkpoint(source))
            self.assertEqual(2, len(opened))
            self.assertEqual(opened[0], opened[1])
            self.assertNotEqual(source, opened[0])
            self.assertFalse(opened[0].exists())

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

    def test_clear_rejects_tables_without_a_single_nonnull_id_primary_key(self):
        class Cursor:
            def __init__(self, primary_columns):
                self.answers = iter(([("qms_material", "InnoDB")], [], primary_columns))
                self.statements = []
                self.rowcount = 0

            def execute(self, statement, *_args):
                self.statements.append(statement)

            def fetchall(self):
                return next(self.answers)

        client = object.__new__(sync.QmsDatabaseClient)
        for primary_columns in ([], [("qms_material", "other")],
                                [("qms_material", "id"), ("qms_material", "other")]):
            with self.subTest(primary_columns=primary_columns):
                cursor = Cursor(primary_columns)
                with self.assertRaisesRegex(sync.SyncError, "id.*主键"):
                    client._clear_target_tables(cursor, lambda _: None)
                self.assertFalse(any("DELETE FROM" in sql for sql in cursor.statements))

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
        rows = {
            "`qms_production_batch`": [f"{number:04d}" for number in range(5)],
            "`qms_work_order`": [f"{number:04d}" for number in range(12)],
            "`qms_customer_order`": [],
            "`qms_material`": [f"{number:04d}" for number in range(2002)],
        }

        class Cursor:
            def execute(self, statement, parameters=()):
                statements.append((statement, parameters))
                table = statement.split("FROM ")[1].split()[0]
                if statement.startswith("SELECT"):
                    lower = parameters[0] if parameters else None
                    self.selected = [row for row in rows[table] if lower is None or row > lower][:2000]
                    return
                if not parameters:
                    raise AssertionError("unbounded DELETE")
                if "WHERE `id` IN" not in statement or statement.count("%s") != len(parameters):
                    raise AssertionError("DELETE must target the selected primary keys")
                selected = set(parameters)
                remaining = [row for row in rows[table] if row not in selected]
                self.rowcount = len(rows[table]) - len(remaining)
                rows[table] = remaining

            def fetchall(self):
                return [(row,) for row in self.selected]

        client = object.__new__(sync.QmsDatabaseClient)
        with patch.object(client, "_existing_source_tables", return_value={"qms_material", "qms_customer_order"}), \
                patch.object(client, "_assert_safe_clear"):
            client._clear_target_tables(Cursor(), progress.append)
        self.assertTrue(all(not table_rows for table_rows in rows.values()))
        material_calls = [call for call in statements if "`qms_material`" in call[0]]
        self.assertEqual(5, len(material_calls))
        self.assertEqual(
            ("SELECT `id` FROM `qms_material` ORDER BY `id` LIMIT 2000 FOR UPDATE", ()),
            material_calls[0],
        )
        self.assertEqual(("0000", "1999"), (material_calls[1][1][0], material_calls[1][1][-1]))
        self.assertEqual(2000, len(material_calls[1][1]))
        self.assertEqual(
            ("SELECT `id` FROM `qms_material` WHERE `id` > %s ORDER BY `id` LIMIT 2000 FOR UPDATE", ("1999",)),
            material_calls[2],
        )
        self.assertEqual(("2000", "2001"), material_calls[3][1])
        self.assertEqual(
            ("SELECT `id` FROM `qms_material` WHERE `id` > %s ORDER BY `id` LIMIT 2000 FOR UPDATE", ("2001",)),
            material_calls[4],
        )
        self.assertEqual([
            "正在清空目标表 qms_production_batch…",
            "目标表 qms_production_batch 已删除 5 行（待初始化完成后提交）。",
            "正在清空目标表 qms_work_order…",
            "目标表 qms_work_order 已删除 12 行（待初始化完成后提交）。",
            "正在清空目标表 qms_customer_order…",
            "目标表 qms_customer_order 已删除 0 行（待初始化完成后提交）。",
            "正在清空目标表 qms_material…",
            "目标表 qms_material 已删除 2,000 行（待初始化完成后提交）…",
            "目标表 qms_material 已删除 2,002 行（待初始化完成后提交）。",
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

            def execute(self, statement):
                events.append(statement)

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
                    headers_only=False, on_sheet=None, read_path=None):
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
            self.assertEqual([
                "schema", "commit", "SET TRANSACTION ISOLATION LEVEL REPEATABLE READ",
                "clear", "rollback",
            ], events)
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

            def execute(self, _statement):
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
