"""Trailing ERP totals are not source records."""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from openpyxl import Workbook

import qms_erp_sync as sync


class TrailingSummaryRowsTests(unittest.TestCase):
    def scan(self, path, root, rows):
        headers = rows[0]
        fields = [
            sync.ErpFieldDefinition(
                "qms_material", path.name, "Test", header, header,
                f"erp_test_{index}", sync.legacy_database_column_name(header),
                sync.erp_column_comment(header), index,
            )
            for index, header in enumerate(headers, 1)
        ]
        registry = sync.ErpFieldRegistry(fields)
        with patch.object(sync, "load_erp_field_registry", return_value=registry):
            return [raw for raw, _ in sync.iter_all_source_records(
                {}, lambda _: None, sync.SourceScanStats(),
                source_directory=root, selected_files=[path],
            )]

    def test_xlsx_keeps_interior_subtotal_but_skips_footer_totals(self):
        rows = [
            ["名称", "数量"],
            ["明细一", 2],
            ["合计", 2],
            ["明细二", 3],
            ["合计", 5],
            [" 汇总： ", 5],
            [None, "总计"],
            [None, None],
        ]
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            path = root / "原料资料明细.xlsx"
            workbook = Workbook()
            workbook.active.title = "Test"
            for row in rows:
                workbook.active.append(row)
            workbook.save(path)
            workbook.close()
            records = self.scan(path, root, rows)

        self.assertEqual([2, 3, 4], [row.source_row_no for row in records])
        self.assertEqual(["明细一", "合计", "明细二"], [
            row.field_values["erp_test_1"] for row in records
        ])

    def test_xls_skips_footer_after_blank_date_placeholder(self):
        rows = [
            ["日期", "名称", "数量"],
            ["2026-10-23", "明细一", 3],
            ["  -   -  : :", "合计：", 3],
            [None, None, None],
        ]
        sheet = Mock(nrows=len(rows))
        sheet.name = "Test"
        sheet.row_values.side_effect = lambda index: rows[index]
        sheet.cell_type.return_value = sync.xlrd.XL_CELL_TEXT
        workbook = Mock(nsheets=1, datemode=0, encoding="utf-8", codepage=1200)
        workbook.sheet_by_index.return_value = sheet

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            path = root / "原料资料明细.xls"
            path.write_bytes(b"mock ERP XLS")
            with patch.object(sync, "open_legacy_compatible_xls", return_value=workbook):
                records = self.scan(path, root, rows)

        self.assertEqual([2], [row.source_row_no for row in records])
        self.assertEqual("明细一", records[0].field_values["erp_test_2"])


if __name__ == "__main__":
    unittest.main()
