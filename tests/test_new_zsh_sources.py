"""The new zsh exports keep every detail and ignore non-record rows."""

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


class NewZshSourcesTests(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
