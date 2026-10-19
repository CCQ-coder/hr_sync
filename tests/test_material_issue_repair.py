"""Safety checks for the one-time, reviewed material-issue schema repair."""

import unittest

from repair_material_issue_row_size import RepairError, assert_empty, schema_change_sql


class RepairSafetyTests(unittest.TestCase):
    def test_nonempty_table_is_rejected_before_schema_change(self):
        class Cursor:
            def execute(self, statement):
                self.statement = statement

            def fetchone(self):
                return (1,)

        cursor = Cursor()
        with self.assertRaises(RepairError):
            assert_empty(cursor, "qms_material_issue")
        self.assertEqual(cursor.statement, "SELECT 1 FROM `qms_material_issue` LIMIT 1")

    def test_repair_sql_only_uses_reviewed_identifiers_and_bound_comments(self):
        class Field:
            database_column = "erp_supplier_no"
            column_comment = "Excel列名：供应商'编号"

        sql, values = schema_change_sql(
            "qms_material_issue", ["erp_旧`列"], [Field()]
        )
        self.assertIn("DROP COLUMN `erp_旧``列`", sql)
        self.assertIn("ADD COLUMN `erp_supplier_no` LONGTEXT NULL COMMENT %s", sql)
        self.assertNotIn(Field.column_comment, sql)
        self.assertEqual(values, (Field.column_comment,))


if __name__ == "__main__":
    unittest.main()
