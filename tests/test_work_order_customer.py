"""Production-instruction exports name the customer column '客户'."""

import unittest

import qms_erp_sync as sync


class WorkOrderCustomerTests(unittest.TestCase):
    def test_customer_from_production_instruction_is_sent_to_qms(self):
        row = {
            sync.normalize_header("生产指令号"): "26090593",
            sync.normalize_header("厂内编号"): "P2E046276A",
            sync.normalize_header("工艺"): "沉金",
            sync.normalize_header("投料数量"): 40,
            sync.normalize_header("客户"): "示例客户",
        }

        self.assertEqual("示例客户", sync.build_payload(row, 0)["customerCode"])


if __name__ == "__main__":
    unittest.main()
