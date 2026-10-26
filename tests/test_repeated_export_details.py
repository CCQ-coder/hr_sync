"""Repeated business numbers retain distinct details across daily exports."""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from openpyxl import Workbook

import qms_erp_sync as sync


class RepeatedExportDetailsTests(unittest.TestCase):
    def scan(self, root, folder, file_name, headers, columns, rows):
        path = root / folder / file_name
        path.parent.mkdir(parents=True)
        workbook = Workbook()
        workbook.active.title = "Test"
        workbook.active.append(headers)
        for row in rows:
            workbook.active.append(row)
        workbook.save(path)
        workbook.close()
        registry = sync.ErpFieldRegistry(
            sync.ErpFieldDefinition(
                sync.source_table_name(file_name, "Test", False), file_name,
                "Test", header, header, column,
                sync.legacy_database_column_name(header),
                sync.erp_column_comment(header), index,
            )
            for index, (header, column) in enumerate(zip(headers, columns), 1)
        )
        with patch.object(sync, "load_erp_field_registry", return_value=registry):
            return [raw for raw, _ in sync.iter_all_source_records(
                {}, lambda _: None, sync.SourceScanStats(),
                source_directory=root, selected_files=[path],
            )]

    def test_customer_order_occurrences_keep_even_identical_details(self):
        headers = ["订单编号", "厂内编号", "数量"]
        columns = ["erp_order_no", "erp_internal_product_no", "erp_order_quantity"]
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            baseline = self.scan(root, "baseline", "客户订单资料.xlsx", headers, columns, [
                ["O1", "P1", 10], ["O1", "P1", 10], ["O1", "P1", 20],
            ])
            daily = self.scan(root, "daily", "客户订单资料.xlsx", headers, columns, [
                ["O1", "P1", 11], ["O1", "P1", 12], ["O1", "P1", 23],
            ])

        self.assertEqual(3, len({row.source_key for row in baseline}))
        self.assertEqual([row.source_key for row in baseline], [row.source_key for row in daily])
        self.assertNotEqual(baseline[0].row_hash, daily[0].row_hash)

    def test_delivery_occurrences_use_production_order_then_ordinal(self):
        headers = ["送货单号", "厂内编号", "制令单号", "数量"]
        columns = [
            "erp_delivery_note_no", "erp_internal_product_no",
            "erp_production_order_no", "erp_delivery_quantity",
        ]
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            baseline = self.scan(root, "baseline", "送货单资料.xlsx", headers, columns, [
                ["HK1", "P1", "WO1", 10],
                ["HK1", "P1", "WO1", 20],
                ["HK1", "P1", "WO1", 20],
                ["HK1", "P1", "WO2", 30],
            ])
            daily = self.scan(root, "daily", "送货单资料.xlsx", headers, columns, [
                ["HK1", "P1", "WO2", 33],
                ["HK1", "P1", "WO1", 11],
                ["HK1", "P1", "WO1", 22],
                ["HK1", "P1", "WO1", 23],
            ])

        self.assertEqual(4, len({row.source_key for row in baseline}))
        self.assertEqual(
            [baseline[3].source_key, baseline[0].source_key,
             baseline[1].source_key, baseline[2].source_key],
            [row.source_key for row in daily],
        )


if __name__ == "__main__":
    unittest.main()
