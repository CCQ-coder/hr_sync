"""Delivery exports retain separate rows and update matching details across files."""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from openpyxl import Workbook

import qms_erp_sync as sync


class DeliveryNoteIdentityTests(unittest.TestCase):
    def _scan(self, root, folder, rows):
        path = root / folder / "送货单资料.xlsx"
        path.parent.mkdir(parents=True, exist_ok=True)
        workbook = Workbook()
        workbook.active.title = "Test"
        workbook.active.append(["送货单号", "厂内编号", "订单编号", "制令单号", "数量"])
        for row in rows:
            workbook.active.append(row)
        workbook.save(path)
        workbook.close()
        columns = (
            "erp_delivery_note_no", "erp_internal_product_no", "erp_order_no",
            "erp_production_order_no", "erp_delivery_quantity",
        )
        headers = ("送货单号", "厂内编号", "订单编号", "制令单号", "数量")
        registry = sync.ErpFieldRegistry(
            sync.ErpFieldDefinition(
                "qms_delivery_note", "送货单资料.xlsx", "Test", header, header,
                column, sync.legacy_database_column_name(header),
                sync.erp_column_comment(header), index,
            )
            for index, (header, column) in enumerate(zip(headers, columns), 1)
        )
        with patch.object(sync, "load_erp_field_registry", return_value=registry):
            pairs = list(sync.iter_all_source_records(
                sync.DEFAULT_CONFIG, lambda _: None, sync.SourceScanStats(),
                source_directory=root, selected_files=[path],
            ))
        return [raw for raw, _ in pairs]

    def test_different_orders_on_one_delivery_note_keep_separate_keys(self):
        with tempfile.TemporaryDirectory() as temporary:
            records = self._scan(Path(temporary), "baseline", [
                ("HK1", "P1", "PI1", "WO1", 10),
                ("HK1", "P1", "PI2", "WO1", 20),
            ])
        self.assertNotEqual(records[0].source_key, records[1].source_key)

    def test_production_order_separates_rows_without_order_number(self):
        with tempfile.TemporaryDirectory() as temporary:
            records = self._scan(Path(temporary), "baseline", [
                ("HK1", "P1", None, "WO1", 10),
                ("HK1", "P1", None, "WO2", 20),
            ])
        self.assertNotEqual(records[0].source_key, records[1].source_key)

    def test_production_order_keeps_identity_when_rows_reorder(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            earlier = self._scan(root, "baseline", [
                ("HK1", "P1", "PI1", "WO1", 10),
                ("HK1", "P1", "PI1", "WO2", 20),
            ])
            later = self._scan(root, "daily", [
                ("HK1", "P1", "PI1", "WO2", 21),
                ("HK1", "P1", "PI1", "WO1", 11),
            ])
        self.assertEqual(earlier[0].source_key, later[1].source_key)
        self.assertEqual(earlier[1].source_key, later[0].source_key)

    def test_repeated_business_identity_keeps_every_occurrence(self):
        with tempfile.TemporaryDirectory() as temporary:
            records = self._scan(Path(temporary), "baseline", [
                ("HK1", "P1", "PI1", "WO1", 10),
                ("HK1", "P1", "PI1", "WO1", 20),
                ("HK1", "P1", "PI1", "WO1", 20),
            ])
        self.assertEqual(3, len({record.source_key for record in records}))

    def test_later_export_updates_same_occurrence_across_files(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            earlier = self._scan(root, "2026-10-19", [
                ("HK1", "P1", "PI1", "WO1", 10),
                ("HK1", "P1", "PI1", "WO1", 20),
            ])
            later = self._scan(root, "2026-10-20", [
                ("HK1", "P1", "PI1", "WO1", 11),
                ("HK1", "P1", "PI1", "WO1", 22),
            ])
        self.assertEqual([record.source_key for record in earlier],
                         [record.source_key for record in later])
        self.assertNotEqual(earlier[0].row_hash, later[0].row_hash)
        self.assertNotEqual(earlier[0].source_key, earlier[1].source_key)


if __name__ == "__main__":
    unittest.main()
