"""Completion and scrap exports keep every detail and ignore non-record rows."""

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from openpyxl import Workbook

import qms_erp_sync as sync


COMPLETION_HEADERS = (
    "客户名称", "投料日期", "生产指令", "批号", "条形码", "厂内编号", "完成数量", "过数单位",
    "流程工序", "工序(收板)", "操作员", "完成日期(含时分)", "生产停留小时", "客户交期",
    "确认", "确认人", "当前板长", "当前板宽", "厂内1/厂外2", "阻焊型号1", "阻焊型号2",
    "文字型号1", "文字型号2", "成型方式", "订单编号", "客户PO", "结余<半成品仓>",
    "文字颜色2", "当前尺寸", "文字颜色1", "阻焊颜色1", "阻焊颜色2", "电镀镍厚",
    "CS电镀%", "电镀金厚", "SS电镀%", "干膜尺寸", "一铜厚度", "一铜孔铜厚",
    "二铜厚度", "二铜孔铜厚", "PCS长", "PCS宽", "连片数", "合拼厂内编号",
    "工序单价\r工序目标成本", "工序金额",
)
SCRAP_HEADERS = (
    "完成编号", "客户编号", "客户名称", "完成日期", "厂内编号", "流程工序", "生产指令",
    "总面积 (成品面积)", "部门名称", "原因", "层数", "累计报废\r(出货单位)", "报废数量",
    "生产类别", "合拼厂内编号", "<因打X板>\r多报废数量", "当前板长",
    "金额2(本位币)\r层数比例", "当前尺寸", "当前板宽", "原生产指令", "责任厂商", "检查数量",
)
COMPLETION_DAILY_HEADERS = Path(__file__).with_name("fixtures") / "gy_completion_20261028_headers.json"


class NewGySourcesTests(unittest.TestCase):
    def scan(self, root, folder, file_name, table, headers, key_columns, rows):
        path = root / folder / file_name
        path.parent.mkdir(parents=True)
        workbook = Workbook()
        workbook.active.title = "Test"
        workbook.active.append(headers)
        for values in rows:
            workbook.active.append([values.get(header) for header in headers])
        workbook.save(path)
        workbook.close()
        registry = sync.ErpFieldRegistry(
            sync.ErpFieldDefinition(
                table, file_name, "Test", header.replace("\r", "\n"), header.replace("\r", "\n"),
                key_columns.get(header, f"erp_test_{index}"),
                sync.legacy_database_column_name(header.replace("\r", "\n")),
                sync.erp_column_comment(header.replace("\r", "\n")), index,
            )
            for index, header in enumerate(headers, 1)
        )
        with patch.object(sync, "load_erp_field_registry", return_value=registry):
            return [raw for raw, _ in sync.iter_all_source_records(
                {}, lambda _: None, sync.SourceScanStats(),
                source_directory=root, selected_files=[path],
            )]

    def test_completion_keeps_repeated_barcodes_by_occurrence_and_skips_non_records(self):
        columns = {"条形码": "erp_barcode", "完成日期(含时分)": "erp_completion_date_with_time",
                   "完成数量": "erp_completion_quantity"}
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            original = self.scan(root, "original", "完成数量资料.xlsx", "qms_completion_quantity",
                                 COMPLETION_HEADERS, columns, [
                {"条形码": "BC1", "生产指令": "WO1", "完成日期(含时分)": "2026-10-23 10:00", "完成数量": 10},
                {"条形码": "BC1", "生产指令": "WO1", "完成日期(含时分)": "2026-10-23 10:00", "完成数量": 20},
                {"投料日期": "  -  -  : :", "完成数量": 0},
                {"条形码": "BC2", "生产指令": "WO2", "完成数量": 30},
                {"投料日期": "  -  -  : :", "完成数量": 60, "工序金额": 999},
            ])
            updated = self.scan(root, "updated", "完成数量资料.xlsx", "qms_completion_quantity",
                                COMPLETION_HEADERS, columns, [
                {"条形码": "BC1", "生产指令": "WO1", "完成日期(含时分)": "2026-10-23 10:00", "完成数量": 11},
                {"条形码": "BC1", "生产指令": "WO1", "完成日期(含时分)": "2026-10-23 10:00", "完成数量": 22},
                {"条形码": "BC2", "生产指令": "WO2", "完成数量": 33},
            ])

        self.assertEqual([2, 3, 5], [row.source_row_no for row in original])
        self.assertTrue(all(row.source_table == "qms_completion_quantity" for row in original))
        self.assertEqual(3, len({row.source_key for row in original}))
        self.assertEqual([row.source_key for row in original], [row.source_key for row in updated])
        self.assertNotEqual(original[0].row_hash, updated[0].row_hash)

    def test_completion_timestamp_keeps_distinct_events_stable_when_order_changes(self):
        columns = {"条形码": "erp_barcode", "完成日期(含时分)": "erp_completion_date_with_time",
                   "完成数量": "erp_completion_quantity"}
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            original = self.scan(root, "original", "完成数量资料.xlsx", "qms_completion_quantity",
                                 COMPLETION_HEADERS, columns, [
                {"条形码": "BC1", "完成日期(含时分)": "2026-10-23 10:00", "完成数量": 10},
                {"条形码": "BC1", "完成日期(含时分)": "2026-10-23 11:00", "完成数量": 20},
            ])
            updated = self.scan(root, "updated", "完成数量资料.xlsx", "qms_completion_quantity",
                                COMPLETION_HEADERS, columns, [
                {"条形码": "BC1", "完成日期(含时分)": "2026-10-23 11:00", "完成数量": 22},
                {"条形码": "BC1", "完成日期(含时分)": "2026-10-23 10:00", "完成数量": 11},
            ])

        self.assertEqual([original[1].source_key, original[0].source_key],
                         [row.source_key for row in updated])
        self.assertNotEqual(original[0].row_hash, updated[1].row_hash)

    def test_scrap_uses_completion_and_internal_product_identity_and_skips_footer(self):
        columns = {
            "完成编号": "erp_completion_no", "厂内编号": "erp_internal_product_no",
            "报废数量": "erp_scrap_quantity",
        }
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            original = self.scan(root, "original", "报废.xlsx", "qms_scrap",
                                 SCRAP_HEADERS, columns, [
                {"完成编号": "FN1", "厂内编号": "P1", "报废数量": 3},
                {"完成编号": "FN1", "厂内编号": "P2", "报废数量": 4},
                {"总面积 (成品面积)": 44.75, "报废数量": 4328},
            ])
            updated = self.scan(root, "updated", "报废.xlsx", "qms_scrap",
                                SCRAP_HEADERS, columns, [
                {"完成编号": "FN1", "厂内编号": "P2", "报废数量": 40},
                {"完成编号": "FN1", "厂内编号": "P1", "报废数量": 30},
            ])

        self.assertEqual([2, 3], [row.source_row_no for row in original])
        self.assertTrue(all(row.source_table == "qms_scrap" for row in original))
        self.assertEqual(2, len({row.source_key for row in original}))
        self.assertEqual(
            [original[1].source_key, original[0].source_key],
            [row.source_key for row in updated],
        )
        self.assertNotEqual(original[0].row_hash, updated[1].row_hash)

    def test_reviewed_registry_covers_every_attached_header(self):
        registry = sync.load_erp_field_registry()
        for table, name, headers in (
            ("qms_completion_quantity", "完成数量资料.xls.xls", COMPLETION_HEADERS),
            ("qms_scrap", "报废.xls.xls", SCRAP_HEADERS),
        ):
            with self.subTest(file=name):
                fields = sorted((field for field in registry.fields
                                 if field.table_name == table
                                 and sync.canonical_source_file_name(field.source_file)
                                 == sync.canonical_source_file_name(name)
                                 and field.sheet_name == "Test"),
                                key=lambda field: field.column_index)
                self.assertEqual(list(headers), [field.excel_source_header for field in fields])
                self.assertEqual(list(range(1, len(headers) + 1)),
                                 [field.column_index for field in fields])
                self.assertFalse(any(
                    field.table_name == "qms_erp_unclassified"
                    and sync.canonical_source_file_name(field.source_file)
                    == sync.canonical_source_file_name(name)
                    for field in registry.fields
                ))

    def test_new_completion_export_maps_all_columns(self):
        fixture = json.loads(COMPLETION_DAILY_HEADERS.read_text(encoding="utf-8"))
        headers = fixture["headers"]
        registry = sync.load_erp_field_registry()
        definitions = registry.resolve_sheet(
            "qms_completion_quantity", "2026-10-28/完成数量资料.XLS", "Test", headers,
        )
        self.assertEqual(104, len(definitions))
        self.assertEqual(104, len({field.database_column for field in definitions}))
        self.assertEqual("erp_barcode", definitions[21].database_column)
        self.assertEqual("erp_completion_date_with_time", definitions[37].database_column)
        self.assertEqual("erp_completion_detail_id", definitions[41].database_column)
        self.assertEqual("erp_customer_part_no_duplicate_2", definitions[96].database_column)
        self.assertEqual("客户料号", definitions[5].excel_source_header)
        self.assertEqual("客户料号", definitions[96].excel_source_header)
        with self.assertRaisesRegex(sync.SyncError, "表头已变化"):
            registry.resolve_sheet(
                "qms_completion_quantity", "2026-10-28/完成数量资料.XLS", "Test",
                ["未审核新列", *headers[1:]],
            )

    def test_missing_business_id_on_detail_is_an_error(self):
        for name, table, headers, columns, row, message in (
            ("完成数量资料.xlsx", "qms_completion_quantity", COMPLETION_HEADERS,
             {"条形码": "erp_barcode", "生产指令": "erp_production_order"},
             {"生产指令": "WO1", "完成数量": 10}, "缺少条形码"),
            ("报废.xlsx", "qms_scrap", SCRAP_HEADERS,
             {"完成编号": "erp_completion_no", "厂内编号": "erp_internal_product_no"},
             {"厂内编号": "P1", "报废数量": 3}, "缺少完成编号"),
        ):
            with self.subTest(file=name), tempfile.TemporaryDirectory() as temporary:
                with self.assertRaisesRegex(sync.SyncError, message):
                    self.scan(Path(temporary), "source", name, table, headers, columns, [row])

    def test_partial_export_overwrite_preserves_omitted_rows(self):
        class Connection:
            def cursor(self):
                return self

            def __enter__(self):
                return self

            def __exit__(self, *_args):
                return False

            def commit(self):
                pass

            def close(self):
                pass

        class Client:
            def __init__(self):
                self.removed = []

            def _connect(self):
                return Connection()

            def _upsert_source_records(self, *_args, **_kwargs):
                pass

            def _delete_missing_snapshot_rows(self, *_args):
                raise AssertionError("partial export must not delete missing rows")

            def _deactivate_removed_file_records(self, _cursor, removed):
                self.removed.append(removed)
                return sum(map(len, removed["raw"].values()))

        def records(_config, _callback, stats, *, selected_files, **_kwargs):
            path = selected_files[0]
            stats.files_scanned += 1
            for part in ("A", "B") if path.read_bytes() == b"full" else ("A",):
                stats.raw_records += 1
                yield sync.RawSourceRecord(
                    source_file=path.as_posix(), sheet_name="Test", source_row_no=2,
                    business_key=part, source_key=part, row_hash=part,
                    field_values={}, source_table=table_name, field_definitions={},
                ), None

        for name, table_name, expected in (
            ("采购订单资料.xls", "qms_purchase_order", {"qms_purchase_order": ["B"]}),
            ("成品入库单资料.xls", "qms_finished_goods_receipt", {}),
            ("完成数量资料.xls", "qms_completion_quantity", {}),
            ("报废.xls", "qms_scrap", {}),
        ):
            with self.subTest(file=name), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                source = root / "daily"
                source.mkdir()
                path = source / name
                path.write_bytes(b"full")
                config = {"skip_initialization": True, "incremental_directory": str(source)}
                client = Client()
                with patch.object(sync, "state_path", return_value=root / "state.json"), \
                        patch.object(sync, "iter_all_source_records", side_effect=records), \
                        patch.object(sync, "QmsDatabaseClient", return_value=client):
                    sync.save_state({sync.SOURCE_IDENTITY_VERSION_STATE_KEY: "5"})
                    sync.synchronize_database_directory(config, False, lambda _: None)
                    path.write_bytes(b"part")
                    sync.synchronize_database_directory(config, False, lambda _: None)
                self.assertEqual(expected, client.removed[-1]["raw"])

    def test_dated_receipt_exports_are_all_imported(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            daily = root / "daily"
            for day in ("2026-10-26", "2026-10-27"):
                source = daily / day / "成品入库单资料.xls"
                source.parent.mkdir(parents=True)
                source.write_text(day)

            def records(_config, _callback, stats, *, selected_files, **_kwargs):
                path = selected_files[0]
                stats.files_scanned += 1
                stats.raw_records += 1
                yield sync.RawSourceRecord(
                    source_file=path.as_posix(), sheet_name="Test", source_row_no=2,
                    business_key=path.parent.name, source_key=f"ERP5:{path.parent.name}",
                    row_hash=path.parent.name, field_values={},
                    source_table="qms_finished_goods_receipt", field_definitions={},
                ), None

            config = {"skip_initialization": True, "incremental_directory": str(daily)}
            with patch.object(sync, "state_path", return_value=root / "state.json"), \
                    patch.object(sync, "iter_all_source_records", side_effect=records):
                sync.save_state({sync.SOURCE_IDENTITY_VERSION_STATE_KEY: "5"})
                summary = sync.synchronize_database_directory(config, True, lambda _: None)
            self.assertEqual((2, 2), (summary.source_files, summary.raw_records))


if __name__ == "__main__":
    unittest.main()
