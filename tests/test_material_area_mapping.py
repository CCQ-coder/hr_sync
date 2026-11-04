import unittest

import qms_erp_sync as sync


class MaterialAreaMappingTests(unittest.TestCase):
    def test_work_order_uses_erp_total_material_input_area(self):
        row = {
            sync.normalize_header("生产指令号"): "26110135",
            sync.normalize_header("厂内编号"): "P2L029541A",
            sync.normalize_header("工艺"): "无铅喷锡",
            sync.normalize_header("投料数量"): 72,
            sync.normalize_header("总投料面积"): 0.5846,
            sync.normalize_header("板材面积"): 0.68,
        }

        self.assertEqual(sync.build_payload(row, 0)["materialArea"], "0.5846")


if __name__ == "__main__":
    unittest.main()
