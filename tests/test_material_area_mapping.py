import unittest

import qms_erp_sync as sync


class MaterialAreaMappingTests(unittest.TestCase):
    def test_work_order_uses_erp_total_material_input_area(self):
        row = {
            sync.normalize_header("生产指令号"): "26100075",
            sync.normalize_header("厂内编号"): "02PC33158B01",
            sync.normalize_header("工艺"): "沉金",
            sync.normalize_header("投料数量"): 162,
            sync.normalize_header("总投料面积\r<成品>"): 5.4165,
            sync.normalize_header("板材面积"): 0,
        }

        self.assertEqual(sync.build_payload(row, 0)["materialArea"], "5.4165")


if __name__ == "__main__":
    unittest.main()
