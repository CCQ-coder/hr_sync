"""SQL-boundary coverage for registry-based ERP columns; no database is used."""

import re
import unittest
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

from openpyxl import Workbook

import qms_erp_sync as sync


class RecordingCursor:
    def __init__(self, columns=()):
        self.columns = list(columns)
        self.executed = []
        self.executemany_calls = []

    def execute(self, statement, values=None):
        self.executed.append((statement, values))

    def executemany(self, statement, rows):
        self.executemany_calls.append((statement, list(rows)))

    def fetchall(self):
        return self.columns

    def fetchone(self):
        return ("work-order-id",)


def make_client():
    return sync.QmsDatabaseClient(sync.DEFAULT_CONFIG)


def processing_field(table="qms_work_order"):
    return sync.ErpFieldDefinition(
        table_name=table, source_file="生产指示资料.xls.xls", sheet_name="Test",
        excel_source_header="加工方式", excel_unique_header="加工方式",
        database_column="erp_processing_method", legacy_database_column="erp_加工方式",
        column_comment="Excel列名：加工方式", column_index=1,
    )


def work_order_payload(field):
    payload = {api_name: None for _, api_name in sync.WORK_ORDER_DB_FIELDS}
    payload.update({
        "workOrderNo": "WO-1", "productCode": "P-01",
        "erpFields": {field.database_column: "机械加工 95%"},
        "erpFieldDefinitions": {field.database_column: field},
        "releasedAt": "2026-09-16", "sourceKey": "ERP-EXCEL:WO-1",
        "sourceVersion": "version",
    })
    return payload


class ErpColumnCommentTests(unittest.TestCase):
    def test_new_column_uses_english_identifier_and_bound_chinese_comment(self):
        field = processing_field()
        cursor = RecordingCursor()
        make_client()._ensure_erp_columns(cursor, "qms_work_order", {field.database_column: field})
        alters = [(sql, args) for sql, args in cursor.executed if sql.startswith("ALTER TABLE")]
        self.assertEqual(len(alters), 1)
        sql, args = alters[0]
        self.assertIn("ADD COLUMN `erp_processing_method` LONGTEXT NULL COMMENT %s", sql)
        self.assertEqual(args, ("Excel列名：加工方式",))
        self.assertNotIn("加工方式", sql)

    def test_work_order_upsert_preserves_english_identifier_and_value_bind_order(self):
        field = processing_field()
        cursor = RecordingCursor()
        payload = work_order_payload(field)
        try:
            result = make_client()._upsert_work_order(cursor, payload)
        except TypeError as exc:
            self.fail(f"Work-order field definitions must be supported through SQL construction: {exc}")
        self.assertEqual(result, "work-order-id")
        sql, values = next((sql, args) for sql, args in cursor.executed if "INSERT INTO `qms_work_order`" in sql)
        self.assertIn("`erp_processing_method`", sql)
        self.assertNotIn("erp_加工方式", sql)
        columns = re.findall(r"`([^`]+)`", sql.split("VALUES", 1)[0])[1:]
        bound = dict(zip(columns, values))
        self.assertEqual(bound["tenant_code"], "customer-b")
        self.assertEqual(bound["work_order_no"], "WO-1")
        self.assertEqual(bound["product_code"], "P-01")
        self.assertEqual(bound["erp_processing_method"], "机械加工 95%")
        self.assertEqual(bound["released_at"], "2026-09-16")
        self.assertEqual(bound["completed_quantity"], 0)
        self.assertEqual(bound["source_system"], "ERP_EXCEL")
        self.assertEqual(bound["source_key"], "ERP-EXCEL:WO-1")
        self.assertEqual(len(values), len(columns) - 2)
        rendered = sql % tuple("value" for _ in values)
        self.assertIn("LIKE 'ERP-EXCEL:%'", rendered)

    def test_existing_comment_is_corrected_once_without_renaming(self):
        field = processing_field()
        cursor = RecordingCursor([(field.database_column, "旧注释"), ("erp_加工方式", "")])
        client = make_client()
        for _ in range(2):
            client._ensure_erp_columns(cursor, "qms_work_order", {field.database_column: field})
        alters = [(sql, args) for sql, args in cursor.executed if sql.startswith("ALTER TABLE")]
        self.assertEqual(alters, [(
            "ALTER TABLE `qms_work_order` MODIFY COLUMN `erp_processing_method` LONGTEXT NULL COMMENT %s",
            ("Excel列名：加工方式",),
        )])

    def test_matching_comment_does_not_alter_table(self):
        field = processing_field()
        cursor = RecordingCursor([(field.database_column, field.column_comment)])
        make_client()._ensure_erp_columns(cursor, "qms_work_order", {field.database_column: field})
        self.assertFalse(any(sql.startswith("ALTER TABLE") for sql, _ in cursor.executed))

    def test_multiple_comments_are_bound_and_successful_add_is_cached(self):
        first = processing_field()
        second = replace(first, database_column="erp_special_note", column_index=2,
                         excel_source_header="说明' 95% `", excel_unique_header="说明' 95% `",
                         legacy_database_column="erp_说明'_95%_", column_comment="Excel列名：说明' 95% `")
        cursor = RecordingCursor()
        client = make_client()
        fields = {second.database_column: second, first.database_column: first}
        for _ in range(2):
            client._ensure_erp_columns(cursor, "qms_work_order", fields)
        alters = [(sql, args) for sql, args in cursor.executed if sql.startswith("ALTER TABLE")]
        self.assertEqual(len(alters), 1)
        sql, args = alters[0]
        self.assertEqual(sql.count("COMMENT %s"), 2)
        self.assertEqual(args, ("Excel列名：加工方式", "Excel列名：说明' 95% `"))
        self.assertNotIn("说明", sql)
        sql % args

    def test_unknown_or_mismatched_definitions_cannot_reach_sql(self):
        field = processing_field()
        for fields, values in [
            ({}, {"erp_processing_method": "value"}),
            ({"erp_加工方式": replace(field, database_column="erp_加工方式")}, {"erp_加工方式": "value"}),
            ({field.database_column: replace(field, table_name="qms_purchase_order")}, {field.database_column: "value"}),
            ({"erp_other": field}, {"erp_other": "value"}),
        ]:
            with self.subTest(fields=fields):
                cursor = RecordingCursor()
                payload = work_order_payload(field)
                payload.update(erpFields=values, erpFieldDefinitions=fields)
                with self.assertRaises(sync.SyncError):
                    make_client()._upsert_work_order(cursor, payload)
                self.assertEqual(cursor.executed, [])

    def test_scan_preserves_source_definition_and_work_order_values(self):
        headers = ["生产指令号", "厂内编号", "工艺", "投料数量", "加工方式", "加工方式", None]
        columns = ["erp_work_order_no", "erp_internal_product_no", "erp_process", "erp_input_quantity",
                   "erp_processing_method", "erp_processing_method_duplicate_2", "erp_blank_column_7"]
        unique = ["生产指令号", "厂内编号", "工艺", "投料数量", "加工方式", "加工方式（重复列2）", "列7"]
        fields = [sync.ErpFieldDefinition(
            "qms_work_order", "sub/生产指示资料.xlsx", "Test", header or "", unique[index],
            columns[index], sync.legacy_database_column_name(unique[index]), f"Excel列名：{header or ''}", index + 1,
        ) for index, header in enumerate(headers)]
        registry = sync.ErpFieldRegistry(fields)
        workbook = Workbook()
        workbook.active.title = "Test"
        workbook.active.append(headers)
        workbook.active.append(["WO-1", "P-1", "钻孔", 10, "普通", "特殊", "保留"])
        root = Path("D:/test-source")
        with patch.object(sync, "candidate_files", return_value=[root / "sub/生产指示资料.xlsx"]), \
                patch.object(sync, "load_workbook", return_value=workbook), \
                patch.object(sync, "load_erp_field_registry", return_value=registry):
            pairs = list(sync.iter_all_source_records({"source_directory": str(root)}, lambda _: None, sync.SourceScanStats()))
        raw, payload = pairs[0]
        self.assertEqual(raw.field_values, dict(zip(columns, ["WO-1", "P-1", "钻孔", "10", "普通", "特殊", "保留"])))
        self.assertEqual(raw.field_definitions, {field.database_column: field for field in fields})
        self.assertEqual(payload["erpFields"], raw.field_values)
        self.assertEqual(payload["erpFieldDefinitions"], raw.field_definitions)
        self.assertEqual(sync.payload_hash(payload), sync.payload_hash({k: v for k, v in payload.items() if k != "erpFieldDefinitions"}))


if __name__ == "__main__":
    unittest.main()
