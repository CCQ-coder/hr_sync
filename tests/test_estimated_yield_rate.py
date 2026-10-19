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
    def test_value_inside_decimal_5_2_stays_in_typed_field(self):
        self.assertEqual(sync.build_payload(work_order_row(95.25), 0)["estimatedYieldRate"], "95.25")

    def test_outlier_is_retained_as_erp_text_and_logged_with_location(self):
        field = next(field for field in sync.load_erp_field_registry().fields
                     if field.table_name == "qms_work_order" and field.excel_source_header == "成品利用率")
        messages = []
        raw, payload = next(iter(sync._source_record_pair(
            "生产指示资料.XLS.XLS", "Test", 11349, work_order_row(5894.55),
            {"成品利用率": 5894.55}, 0, True, sync.SourceScanStats(),
            "qms_work_order", [field], messages.append,
        )))
        self.assertIsNone(payload["estimatedYieldRate"])
        self.assertEqual(raw.field_values[field.database_column], "5894.55")
        self.assertEqual(payload["erpFields"][field.database_column], "5894.55")
        self.assertTrue(any("第 11349 行" in message and "5894.55" in message for message in messages))


if __name__ == "__main__":
    unittest.main()
