"""Regression coverage for pre-2026-09-16 ERP incremental exports."""

import unittest
from pathlib import Path

import qms_erp_sync as sync


LEGACY_RECEIPT_HEADERS = (
    "ylr_bh", "chsh_j", "date_rk", "ok_tc_thh2", "caig_bh", "yuanl_bh", "yuanlm",
    "guig", "shul_mq", "jine_mq", "shul_xd", "shul_ljjh", "shul_z_rk", "shul_z_th",
    "dw", "hs_danj", "shuil", "danj", "bb", "jine", "shench_dt", "shench_po",
    "beizh_m", "date_rzh", "yue", "dazh", "kouk", "tuih_pd", "tuih_qr", "shul_ljll",
    "ylr_mm1", "ylr_mi1", "user_name", "user_date", "mianj", "baozh_day", "id_ylr_m",
    "id_caig_m", "gch_j", "shul_ljhch", "id_ylch_m", "ylr_lb", "ylr_bc1", "bum_shul",
    "leib1", "leib2", "ylr_mm2", "cg1_bx2_chr", "hs_danj2", "shul_qr2", "danj_qm",
    "ylr_mc2", "zhol_rk", "cw_j", "jine_bhs", "shul_rk", "shul_th", "iqc_ok123_c",
    "danj_chb", "danj_chb_bb", "bum3b_kt", "bum3b_name", "bum3b_date", "jine_chb",
    "jine_benb_chb", "stop_name", "stop_date", "qm", "shh_name", "shh_date", "ruk_mj",
    "stop_hch", "beizh_hch", "stop_name1", "stop_date1", "shul_aq", "shul_aqmax",
    "day_youx", "ok_bg_c", "ylr_mc3", "ylr_mc4", "chsh_bh", "leib3", "chsh_bh_w",
    "chsh_j_w", "danj_wf", "bb_wf", "baogdh", "ck_j", "cangw", "yq_tsh", "ylr_bc2",
    "date_dq", "yuanlm_en", "guig_en", "date_xd", "bum_bh", "bum_j",
)

LEGACY_WORK_ORDER_HEADERS = (
    "date_tl", "shch_bh", "keh_bh", "cengsh", "pingm_bh", "shul_jt_sum", "shul_tl",
    "mianj_tl", "zun_yc", "pnl_piansh", "pnl2_piansh", "hep_pm_bh", "gongy", "caizh",
    "banh", "tunbh", "chengx", "sunh_100", "shul_jhll", "shul_ljll", "shul_ljrk",
    "shul_ljbf", "date_yqjh", "shul_jt", "user_name", "user_date", "zhch12_chr",
    "pcs_lpsh_bom", "pingm", "pnl_ch", "pnl_k", "pnl2_ch", "pnl2_k", "bfl_100",
    "shch_jp_ok", "lyl_lp", "mj_pb_dd", "zhch1_bl2", "lch1_c0", "shul_qrk",
    "pingm_bh_old", "date_rkend", "dind_bh", "shul_xd", "mj_pb_tl", "shul_mq",
)


class LegacyIncrementalExportTests(unittest.TestCase):
    def setUp(self):
        self.registry = sync.load_erp_field_registry()

    def test_reviewed_internal_receipt_headers_map_to_current_registered_fields(self):
        schema = sync.resolve_source_schema(
            self.registry,
            "2026-09-11/原料入库单资料.xls",
            "原料入库单资料",
            LEGACY_RECEIPT_HEADERS,
            map_work_orders=False,
        )

        self.assertFalse(schema.is_work_order)
        self.assertEqual(schema.target_table, "qms_material_receipt")
        self.assertEqual(schema.normalized_headers[0], sync.normalize_header("入库单号"))
        self.assertEqual(schema.definitions[0].database_column, "erp_receipt_no")
        self.assertEqual(schema.definitions[3].database_column, "erp_acceptance_result")

    def test_one_changed_internal_header_does_not_bypass_registry_review(self):
        changed = list(LEGACY_RECEIPT_HEADERS)
        changed[0] = "unreviewed_field"

        with self.assertRaisesRegex(sync.SyncError, "字段注册表"):
            sync.resolve_source_schema(
                self.registry,
                "2026-09-11/原料入库单资料.xls",
                "原料入库单资料",
                changed,
                map_work_orders=False,
            )

    def test_reviewed_internal_work_order_headers_keep_qms_mapping(self):
        schema = sync.resolve_source_schema(
            self.registry,
            "2026-09-11/生产指示资料.xls",
            "生产指示资料",
            LEGACY_WORK_ORDER_HEADERS,
            map_work_orders=True,
        )

        self.assertTrue(schema.is_work_order)
        self.assertIsNone(schema.target_table)
        self.assertEqual(schema.normalized_headers[1], sync.normalize_header("生产指令号"))
        self.assertEqual(schema.normalized_headers[4], sync.normalize_header("厂内编号"))
        self.assertEqual(schema.normalized_headers[12], sync.normalize_header("工艺"))

    def test_missing_codepage_text_is_decoded_as_the_erp_gbk_export(self):
        mojibake = "\xd4\xad\xc1\xcf\xc8\xeb\xbf\xe2\xb5\xa5\xd7\xca\xc1\xcf"
        self.assertEqual(sync.decode_legacy_xls_text(mojibake), "原料入库单资料")
        self.assertEqual(sync.decode_legacy_xls_text("ylr_bh"), "ylr_bh")

    def test_real_legacy_biff5_customer_part_export_can_read_past_row_16384(self):
        source = Path(r"D:\华软导出\2026-09-11\客户料号资料.xls")
        if not source.is_file():
            self.skipTest("local legacy ERP workbook is unavailable")

        workbook = sync.open_legacy_compatible_xls(source)
        try:
            sheet = sync.xls_sheet_by_index(workbook, 0)
            headers = sync.xls_row_values(workbook, sheet, 0)
        finally:
            workbook.release_resources()

        self.assertEqual(sheet.nrows, 65535)
        self.assertEqual(headers[:4], ["pingm_bh", "gongy", "keh_bh", "pingm"])
        self.assertEqual(sync.xls_text_value(workbook, sheet.name), "客户料号资料")


if __name__ == "__main__":
    unittest.main()
