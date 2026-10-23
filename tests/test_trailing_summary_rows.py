"""Summary footers must not become ERP source records."""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from openpyxl import Workbook

import qms_erp_sync as sync


class TrailingSummaryRowsTests(unittest.TestCase):
    ROWS = [
        ["名称", "数量"],
        ["明细一", 2],
        ["合计", 2],  # A subtotal within the data is still a source row.
        ["明细二", 3],
        ["合计", 5],
        [" 汇总： ", 5],
        [None, "总计"],
        [None, None],
    ]

    class Registry:
        def canonical_headers_for(self, _source_file, headers):
            return headers

        def resolve_sheet(self, table, source_file, sheet, headers):
            return [sync.ErpFieldDefinition(
                table, source_file, sheet, header, header, column,
                sync.legacy_database_column_name(header),
                sync.erp_column_comment(header), index,
            ) for index, (header, column) in enumerate(zip(
                headers, ("erp_label", "erp_quantity"),
            ), 1)]

    def _scan(self, path, root):
        stats = sync.SourceScanStats()
        with patch.object(sync, "load_erp_field_registry", return_value=self.Registry()):
            records = [raw for raw, _ in sync.iter_all_source_records(
                {}, lambda _: None, stats, source_directory=root, selected_files=[path],
            )]
        self.assertEqual(["明细一", "合计", "明细二"], [
            raw.field_values["erp_label"] for raw in records
        ])
        self.assertEqual([2, 3, 4], [raw.source_row_no for raw in records])
        self.assertEqual(3, stats.raw_records)

    def test_xlsx_skips_only_trailing_summary_rows(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            path = root / "原料资料明细.xlsx"
            workbook = Workbook()
            for row in self.ROWS:
                workbook.active.append(row)
            workbook.save(path)
            workbook.close()
            self._scan(path, root)

    def test_xls_skips_only_trailing_summary_rows(self):
        root = Path("/tmp/trailing-summary-xls")
        path = root / "原料资料明细.xls"
        sheet = Mock(nrows=len(self.ROWS))
        sheet.row_values.side_effect = lambda index: self.ROWS[index]
        sheet.cell_type.return_value = sync.xlrd.XL_CELL_TEXT
        workbook = Mock(encoding="utf-8", biff_version=80, datemode=0)
        workbook.sheet_names.return_value = ["Test"]
        workbook.sheet_by_name.return_value = sheet
        with patch.object(sync, "open_erp_xls", return_value=workbook):
            self._scan(path, root)

    def test_summary_text_in_detail_column_is_not_a_footer(self):
        rows = [(2, ["明细一", 2]), (3, ["明细二", "汇总"])]
        self.assertEqual(rows, list(sync.without_trailing_summary_rows(rows)))

    def test_empty_date_placeholder_before_footer_label(self):
        detail = (50, ["RK2610-0012", "正常明细"])
        footer = (51, [None, None, "  -   -  : :", None, None, None, "合计：", 2514])
        self.assertEqual([detail], list(sync.without_trailing_summary_rows([detail, footer])))


if __name__ == "__main__":
    unittest.main()
