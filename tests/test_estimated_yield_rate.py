"""Keep an out-of-range ERP rate without overflowing the typed QMS column."""

import unittest

import qms_erp_sync as sync


def work_order_row(rate):
    return {
        sync.normalize_header("生产指令号"): "WO-1",
        sync.normalize_header("厂内编号"): "P-1",
        sync.normalize_header("工艺"): "钻孔",
        sync.normalize_header("投料数量"): 1,
        sync.normalize_header("成品利用率"): rate,
    }


class EstimatedYieldRateTests(unittest.TestCase):
    def test_values_inside_decimal_10_2_stay_in_typed_field(self):
        for source, expected in (
            ("95.25", "95.25"),
            ("1500.9", "1500.9"),
            ("5894.55", "5894.55"),
            ("99999999.99", "99999999.99"),
        ):
            with self.subTest(source=source):
                self.assertEqual(sync.build_payload(work_order_row(source), 0)["estimatedYieldRate"], expected)

    def test_outlier_is_retained_as_erp_text_and_logged_with_location(self):
        field = next(field for field in sync.load_erp_field_registry().fields
                     if field.table_name == "qms_work_order" and field.excel_source_header == "成品利用率")
        messages = []
        raw, payload = next(iter(sync._source_record_pair(
            "生产指示资料.XLS.XLS", "Test", 11349, work_order_row("100000000.00"),
            {"成品利用率": "100000000.00"}, 0, True, sync.SourceScanStats(),
            "qms_work_order", [field], messages.append,
        )))
        self.assertIsNone(payload["estimatedYieldRate"])
        self.assertEqual(raw.field_values[field.database_column], "100000000.00")
        self.assertEqual(payload["erpFields"][field.database_column], "100000000.00")
        self.assertTrue(any(
            "第 11349 行" in message
            and "100000000" in message
            and "DECIMAL(10,2)" in message
            for message in messages
        ))


if __name__ == "__main__":
    unittest.main()
