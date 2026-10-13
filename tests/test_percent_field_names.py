"""Regression coverage for percent signs in ERP Excel headers."""

import unittest

from qms_erp_sync import QmsDatabaseClient, RawSourceRecord, WORK_ORDER_DB_FIELDS, load_erp_field_registry


class CapturingCursor:
    """Minimal DB-API cursor used to inspect generated parameterized SQL."""

    def __init__(self) -> None:
        self.executed = []
        self.executemany_calls = []

    def execute(self, statement, values=None) -> None:
        self.executed.append((statement, values))

    def executemany(self, statement, rows) -> None:
        self.executemany_calls.append((statement, list(rows)))

    def fetchone(self):
        return ("work-order-id",)

    def fetchall(self):
        return []


def client() -> QmsDatabaseClient:
    return QmsDatabaseClient(
        {
            "database_host": "127.0.0.1",
            "database_port": "3306",
            "database_name": "qms",
            "database_username": "qms",
            "database_password": "qms",
            "tenant_code": "customer-b",
        }
    )


class PercentFieldNameSqlTests(unittest.TestCase):
    def test_source_upsert_maps_percent_header_to_english_and_preserves_binding(self) -> None:
        sync_client = client()
        cursor = CapturingCursor()
        field = next(field for field in load_erp_field_registry().fields
                     if field.table_name == "qms_process_output_summary" and field.excel_source_header == "达成率%")
        record = RawSourceRecord(
            source_file="各工段出数汇总资料.xls",
            sheet_name="Test",
            source_row_no=2,
            business_key="行2",
            source_key="source-key",
            row_hash="row-hash",
            field_values={field.database_column: "98.6"},
            source_table="qms_process_output_summary",
            field_definitions={field.database_column: field},
        )

        sync_client._upsert_source_records(cursor, "qms_process_output_summary", [record])

        statement, rows = cursor.executemany_calls[0]
        rendered = statement % tuple("value" for _ in rows[0])
        self.assertIn("`erp_achievement_rate_percent`", rendered)
        self.assertNotIn("erp_达成率%", rendered)
        self.assertEqual(rows[0][-1], "98.6")
        self.assertIn(("Excel列名：达成率%",), [args for _, args in cursor.executed])

    def test_work_order_upsert_maps_percent_header_and_preserves_like_pattern(self) -> None:
        sync_client = client()
        cursor = CapturingCursor()
        field = next(field for field in load_erp_field_registry().fields
                     if field.table_name == "qms_work_order" and field.excel_source_header == "报废率%")
        payload = {api_field: None for _, api_field in WORK_ORDER_DB_FIELDS}
        payload.update(
            {
                "workOrderNo": "WO-1",
                "erpFields": {field.database_column: "0.5"},
                "erpFieldDefinitions": {field.database_column: field},
                "releasedAt": None,
                "sourceKey": "ERP-EXCEL:WO-1",
                "sourceVersion": "version",
            }
        )

        sync_client._upsert_work_order(cursor, payload)

        statement, values = next((sql, args) for sql, args in cursor.executed if "INSERT INTO `qms_work_order`" in sql)
        rendered = statement % tuple("value" for _ in values)
        self.assertIn("`erp_scrap_rate_percent`", rendered)
        self.assertNotIn("erp_报废率%", rendered)
        self.assertIn("LIKE 'ERP-EXCEL:%'", rendered)
        self.assertIn(("Excel列名：报废率%",), [args for _, args in cursor.executed])


if __name__ == "__main__":
    unittest.main()
