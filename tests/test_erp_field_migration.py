"""Behavioral tests for offline ERP field migration artifacts."""

import importlib
import json
import re
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

from qms_erp_sync import ErpFieldDefinition, ErpFieldRegistry, SyncError


class ErpFieldMigrationTests(unittest.TestCase):
    def setUp(self):
        self.migration = importlib.import_module("generate_erp_field_migration")
        self.row = self.migration.RenameManifestRow(
            table_name="qms_customer_order", source_file="客户订单资料.xls.xls",
            sheet_name="Test", column_index=1, excel_source_header="加工方式",
            excel_unique_header="加工方式", old_field="erp_加工方式",
            new_field="erp_processing_method", comment="Excel列名：加工方式",
            expected_field_definition="LONGTEXT NULL",
        )

    def field(self, **changes):
        values = dict(
            table_name="qms_customer_order", source_file="客户订单资料.xls.xls",
            sheet_name="Test", column_index=1, excel_source_header="加工方式",
            excel_unique_header="加工方式", legacy_database_column="erp_加工方式",
            database_column="erp_processing_method", column_comment="Excel列名：加工方式",
        )
        values.update(changes)
        return ErpFieldDefinition(**values)

    def rewrite(self, sql, rows, registry=None):
        if registry is None:
            registry = ErpFieldRegistry(ErpFieldDefinition(
                r.table_name, r.source_file, r.sheet_name, r.excel_source_header,
                r.excel_unique_header, r.new_field, r.old_field, r.comment, r.column_index,
            ) for r in rows)
        return self.migration.rewrite_bi_queries(sql, rows, registry)

    def test_apply_renders_real_change_column_and_backup_warning(self):
        sql = self.migration.render_apply_sql([self.row])
        self.assertIn("ALTER TABLE `qms_customer_order`", sql)
        self.assertIn("CHANGE COLUMN `erp_加工方式` `erp_processing_method` LONGTEXT NULL COMMENT 'Excel列名：加工方式'", sql)
        self.assertIn("BACKUP", sql)
        self.assertIn("STOP", sql)

    def test_comment_control_sanitation_accepts_clean_comment_and_preserves_raw_header(self):
        source = "加工\r\n方式"
        row = replace(self.row, excel_source_header=source, excel_unique_header=source,
                      comment="Excel列名：加工 方式")
        sql = self.migration.render_apply_sql([row])
        self.assertIn("COMMENT 'Excel列名：加工 方式'", sql)
        self.assertNotIn("Excel列名：加工\r\n方式", sql)
        self.assertEqual(row.excel_source_header, source)

    def test_comment_control_characters_are_rejected_by_migration_validation(self):
        row = replace(self.row, excel_source_header="加工\r方式", comment="Excel列名：加工\r方式")
        for render in (self.migration.render_apply_sql, self.migration.render_preflight_sql,
                       self.migration.render_verify_sql):
            with self.subTest(renderer=render.__name__):
                with self.assertRaisesRegex(SyncError, "元数据"):
                    render([row])

    def test_registry_target_collision_is_rejected(self):
        with self.assertRaisesRegex(SyncError, "目标字段冲突"):
            registry = ErpFieldRegistry([
                self.field(), self.field(source_file="另一文件.xls"),
            ])
            self.migration.build_rename_manifest(registry)

    def test_comments_escape_quotes_and_backslashes_independently_of_server_mode(self):
        row = replace(self.row, excel_source_header="加工'方式\\路径",
                      comment="Excel列名：加工'方式\\路径")
        sql = self.migration.render_apply_sql([row])
        self.assertIn("COMMENT 'Excel列名：加工''方式\\路径'", sql)
        self.assertIn("NO_BACKSLASH_ESCAPES", sql)
        self.assertIn("SET SESSION sql_mode = @erp_migration_saved_sql_mode", sql)

    def test_manifest_keeps_source_scope_and_omits_unchanged_names(self):
        unchanged = self.field(column_index=2, excel_source_header="quantity",
            excel_unique_header="quantity", legacy_database_column="erp_quantity",
            database_column="erp_quantity", column_comment="Excel列名：quantity")
        rows = self.migration.build_rename_manifest(ErpFieldRegistry([unchanged, self.field()]))
        self.assertEqual(rows, [self.row])

    def test_shared_old_column_expands_backfills_by_exact_scope_then_contracts_separately(self):
        registry = ErpFieldRegistry([
            self.field(), self.field(source_file="另一文件.xls", database_column="erp_processing_method_other"),
        ])
        rows = self.migration.build_rename_manifest(registry)
        self.assertEqual([r.migration_kind for r in rows], ["split_source", "split_source"])
        sql = self.migration.render_apply_sql(rows)
        self.assertIn("ADD COLUMN `erp_processing_method` LONGTEXT NULL COMMENT 'Excel列名：加工方式'", sql)
        self.assertIn("SET `erp_processing_method` = `erp_加工方式`", sql)
        self.assertIn("BINARY `source_file` = BINARY '客户订单资料.xls.xls'", sql)
        self.assertIn("BINARY `sheet_name` = BINARY 'Test'", sql)
        self.assertNotIn("DROP COLUMN", sql)
        self.assertNotIn("CHANGE COLUMN", sql)
        contract = self.migration.render_contract_sql(rows)
        self.assertEqual(contract.count("DROP COLUMN `erp_加工方式`"), 1)
        verify = self.migration.render_verify_sql(rows)
        for text in ("split_value_mismatch", "legacy_non_null_count", "new_non_null_count",
                     "unassigned_legacy_value", "source_file", "sheet_name"):
            self.assertIn(text, verify)
        self.assertIn("COALESCE(`erp_processing_method`, `erp_processing_method_other`)",
            self.rewrite("SELECT `erp_加工方式` FROM qms_customer_order", rows))

    def test_renderers_reject_unsafe_identifiers_lengths_definitions_and_collisions(self):
        cases = [
            [replace(self.row, table_name="users")],
            [replace(self.row, new_field="erp_x`; DROP TABLE users;")],
            [replace(self.row, old_field="erp_`unsafe")],
            [replace(self.row, new_field="erp_" + "a" * 61)],
            [replace(self.row, old_field="erp_" + "中" * 21)],
            [replace(self.row, expected_field_definition="INT NOT NULL")],
            [self.row, replace(self.row, new_field="erp_another")],
            [self.row, replace(self.row, old_field="erp_另一列")],
        ]
        for renderer in (self.migration.render_apply_sql, self.migration.render_preflight_sql,
                         self.migration.render_verify_sql):
            for rows in cases:
                with self.subTest(renderer=renderer.__name__, rows=rows):
                    with self.assertRaises(SyncError):
                        renderer(rows)

    def test_preflight_reports_actual_definitions_and_conflicting_targets(self):
        sql = self.migration.render_preflight_sql([self.row])
        for text in ("VERSION()", "@@SESSION.sql_mode", "information_schema.columns",
                     "COLUMN_TYPE", "IS_NULLABLE", "COLUMN_DEFAULT", "EXTRA", "COLUMN_COMMENT",
                     "CHARACTER_SET_NAME", "COLLATION_NAME", "LEFT(COLUMN_NAME, 4) = 'erp_'",
                     "missing_old_column", "target_already_exists", "unexpected_definition"):
            self.assertIn(text, sql)

    def test_schema_checks_use_mysql57_derived_manifest_without_cte(self):
        second = replace(self.row, table_name="qms_purchase_order")
        for render, expected_relations in (
            (self.migration.render_preflight_sql, 1),
            (self.migration.render_verify_sql, 4),
        ):
            with self.subTest(renderer=render.__name__):
                sql = render([self.row, second])
                self.assertNotRegex(sql, r"(?i)\bWITH\b")
                self.assertEqual(sql.count("FROM (\nSELECT "), expected_relations)
                self.assertEqual(sql.count("\n) AS m"), expected_relations)
                self.assertIn("UNION ALL\nSELECT 'qms_purchase_order' AS table_name", sql)
                self.assertNotIn("FROM manifest", sql)
                self.assertNotRegex(sql, r"(?i)\b(?:JSON_TABLE|ROW_NUMBER|RANK|DENSE_RANK)\s*\(")
                empty_sql = render([])
                self.assertNotRegex(empty_sql, r"(?i)\bWITH\b")
                self.assertIn("FROM (\nSELECT NULL AS table_name", empty_sql)
                self.assertIn("WHERE 1=0\n) AS m", empty_sql)

    def test_every_migration_sql_header_declares_mysql57_and_mysql80(self):
        for render in (self.migration.render_preflight_sql, self.migration.render_apply_sql,
                       self.migration.render_verify_sql, self.migration.render_contract_sql):
            with self.subTest(renderer=render.__name__):
                sql = render([self.row])
                self.assertIn("-- MySQL 5.7+/8.0.", sql)
                self.assertNotIn("MySQL 8.0+", sql)

    def test_current_registry_comments_remain_control_free_in_generated_artifacts(self):
        from qms_erp_sync import load_erp_field_registry
        rows = self.migration.build_rename_manifest(load_erp_field_registry())
        for row in rows:
            self.assertNotRegex(row.comment, r"[\x00-\x1f\x7f-\x9f]")
        for render in (self.migration.render_preflight_sql, self.migration.render_apply_sql,
                       self.migration.render_verify_sql, self.migration.render_contract_sql):
            with self.subTest(renderer=render.__name__):
                for literal in re.findall(r"'(?:''|[^'])*'", render(rows)):
                    self.assertNotRegex(literal, r"[\x00-\x1f\x7f-\x9f]")

    def test_verify_detects_remaining_missing_and_comment_mismatch(self):
        sql = self.migration.render_verify_sql([self.row])
        for text in ("remaining_old_column", "missing_new_column", "comment_mismatch",
                     "definition_mismatch", "BINARY", "Excel列名：加工方式"):
            self.assertIn(text, sql)

    def test_bi_rewrite_uses_query_block_table_and_join_alias_context(self):
        rows = [self.row, replace(self.row, table_name="qms_purchase_order", new_field="erp_purchase_processing_method")]
        source = ("WITH a AS (SELECT `erp_加工方式` FROM qms_customer_order), "
                  "b AS (SELECT `erp_加工方式` FROM qms_purchase_order) SELECT * FROM a JOIN b;\n"
                  "SELECT c.`erp_加工方式`, p.`erp_加工方式` FROM qms_customer_order c "
                  "JOIN qms_purchase_order AS p ON c.id=p.id;")
        actual = self.rewrite(source, rows)
        self.assertIn("SELECT `erp_processing_method` FROM qms_customer_order", actual)
        self.assertIn("SELECT `erp_purchase_processing_method` FROM qms_purchase_order", actual)
        self.assertIn("c.`erp_processing_method`, p.`erp_purchase_processing_method`", actual)

    def test_bi_unresolved_or_unknown_legacy_references_are_blocked(self):
        rows = [self.row, replace(self.row, table_name="qms_purchase_order", new_field="erp_purchase_processing_method")]
        for sql in (
            "SELECT `erp_加工方式` FROM qms_customer_order JOIN qms_purchase_order;",
            "SELECT `erp_未知字段` FROM qms_customer_order;",
        ):
            with self.subTest(sql=sql):
                with self.assertRaisesRegex(SyncError, "BLOCKED"):
                    self.rewrite(sql, rows)

    def test_bi_strings_and_comments_are_preserved_and_rewrite_is_idempotent(self):
        sql = "SELECT `erp_加工方式`, 'erp_加工方式' FROM qms_customer_order; -- `erp_加工方式`\n"
        actual = self.rewrite(sql, [self.row])
        self.assertEqual(actual, "SELECT `erp_processing_method`, 'erp_加工方式' FROM qms_customer_order; -- `erp_加工方式`\n")
        self.assertEqual(self.rewrite(actual, [self.row]), actual)

    def test_cli_writes_reproducible_artifacts_and_stops_before_writes_on_unknown_bi(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            registry = root / "registry.json"
            from dataclasses import asdict
            registry.write_text(json.dumps({"schema_version": 1, "fields": [asdict(self.field())]}), encoding="utf-8")
            bi = root / "bi.sql"
            bi.write_text("SELECT `erp_加工方式` FROM qms_customer_order;", encoding="utf-8")
            args = ["--registry", str(registry), "--output-root", str(root), "--bi-file", str(bi), "--update-bi"]
            self.assertEqual(self.migration.main(args), 0)
            manifest = root / "outputs/erp_field_rename_manifest.json"
            document = json.loads(manifest.read_text(encoding="utf-8"))
            self.assertEqual(document["rows"][0]["old_field"], "erp_加工方式")
            self.assertEqual(document["rows"][0]["source_file"], "客户订单资料.xls.xls")
            self.assertEqual(bi.read_text(encoding="utf-8"), "SELECT `erp_processing_method` FROM qms_customer_order;")
            artifacts = [manifest] + list((root / "sql").glob("*.sql"))
            self.assertEqual(len(artifacts), 5)
            original = {path: path.read_bytes() for path in artifacts}
            self.assertEqual(self.migration.main(args), 0)
            self.assertEqual(original, {path: path.read_bytes() for path in artifacts})
            bi.write_text("SELECT `erp_未知` FROM qms_customer_order;", encoding="utf-8")
            self.assertEqual(self.migration.main(args), 2)
            self.assertEqual(original, {path: path.read_bytes() for path in artifacts})
            self.assertEqual(bi.read_text(encoding="utf-8"), "SELECT `erp_未知` FROM qms_customer_order;")

    def test_cli_can_generate_customer_migration_without_unrelated_bi(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            registry = root / "registry.json"
            from dataclasses import asdict
            registry.write_text(json.dumps({"schema_version": 1, "fields": [asdict(self.field())]}), encoding="utf-8")
            args = ["--registry", str(registry), "--output-root", str(root),
                    "--bi-file", str(root / "missing-bi.sql"), "--skip-bi-validation"]
            self.assertEqual(self.migration.main(args), 0)
            self.assertTrue((root / "sql/erp_field_rename_apply.sql").is_file())
            self.assertTrue((root / "outputs/erp_field_rename_manifest.json").is_file())

    def test_bi_comma_join_ambiguity_is_not_silently_rewritten(self):
        rows = [self.row, replace(self.row, table_name="qms_purchase_order", new_field="erp_purchase_processing_method")]
        with self.assertRaisesRegex(SyncError, "BLOCKED"):
            self.rewrite(
                "SELECT `erp_加工方式` FROM qms_customer_order c, qms_purchase_order p", rows)

    def test_bi_erp_table_alias_declaration_and_qualifier_are_preserved(self):
        actual = self.rewrite(
            "SELECT `erp_加工方式`.`erp_加工方式` FROM qms_customer_order AS `erp_加工方式`;", [self.row])
        self.assertEqual(actual,
            "SELECT `erp_加工方式`.`erp_processing_method` FROM qms_customer_order AS `erp_加工方式`;")

    def test_bi_non_qms_table_aliases_are_declarations_not_erp_fields(self):
        for declaration in ("erp_aux", "AS `erp_aux`"):
            sql = "SELECT erp_aux.id FROM auxiliary_data " + declaration + " WHERE erp_aux.id > 0;"
            with self.subTest(declaration=declaration):
                self.assertEqual(self.rewrite(sql, [self.row]), sql)
                with self.assertRaisesRegex(SyncError, "BLOCKED"):
                    self.rewrite(sql.replace("erp_aux.id", "erp_aux.erp_processing_method"), [self.row])

    def test_bi_cte_name_declarations_table_references_and_qualifiers_are_preserved(self):
        sql = ("WITH erp_cte AS (SELECT `erp_加工方式` AS method FROM qms_customer_order), "
               "`erp_second` AS (SELECT erp_cte.method FROM erp_cte) "
               "SELECT erp_second.method FROM `erp_second`;")
        self.assertEqual(self.rewrite(sql, [self.row]),
            sql.replace("`erp_加工方式`", "`erp_processing_method`"))
        with self.assertRaisesRegex(SyncError, "BLOCKED"):
            self.rewrite("WITH erp_cte AS (SELECT `erp_unknown` FROM qms_customer_order) SELECT * FROM erp_cte", [self.row])

    def test_bi_derived_table_alias_declarations_and_qualifiers_are_preserved(self):
        for declaration in ("erp_derived", "AS `erp_derived`"):
            sql = ("SELECT erp_derived.method FROM (SELECT `erp_加工方式` AS method "
                   "FROM qms_customer_order) " + declaration + ";")
            with self.subTest(declaration=declaration):
                self.assertEqual(self.rewrite(sql, [self.row]),
                    sql.replace("`erp_加工方式`", "`erp_processing_method`"))
                with self.assertRaisesRegex(SyncError, "BLOCKED"):
                    self.rewrite(sql.replace("qms_customer_order", "qms_material_issue"), [self.row])

    def test_bi_erp_select_alias_declaration_and_order_reference_are_preserved(self):
        actual = self.rewrite(
            "SELECT `erp_加工方式` AS `erp_展示` FROM qms_customer_order ORDER BY `erp_展示`;", [self.row])
        self.assertEqual(actual,
            "SELECT `erp_processing_method` AS `erp_展示` FROM qms_customer_order ORDER BY `erp_展示`;")

    def test_bi_implicit_select_aliases_are_preserved(self):
        for expression in ("`erp_加工方式`", "TRIM(`erp_加工方式`)", "'literal'"):
            sql = "SELECT " + expression + " `erp_加工方式` FROM qms_customer_order ORDER BY `erp_加工方式`;"
            expected = ("SELECT " + expression.replace("`erp_加工方式`", "`erp_processing_method`")
                        + " `erp_加工方式` FROM qms_customer_order ORDER BY `erp_加工方式`;")
            with self.subTest(expression=expression):
                self.assertEqual(self.rewrite(sql, [self.row]), expected)

    def test_bi_accepts_valid_unchanged_fields_from_explicit_complete_registry(self):
        unchanged = self.field(column_index=2, excel_source_header="quantity",
            excel_unique_header="quantity", legacy_database_column="erp_quantity",
            database_column="erp_quantity", column_comment="Excel列名：quantity")
        registry = ErpFieldRegistry([self.field(), unchanged])
        self.assertEqual(self.rewrite(
            "SELECT `erp_quantity` FROM qms_customer_order", [self.row], registry),
            "SELECT `erp_quantity` FROM qms_customer_order")
        with self.assertRaisesRegex(SyncError, "BLOCKED"):
            self.rewrite("SELECT `erp_quantity` FROM qms_material_issue", [self.row], registry)

    def test_bi_legacy_and_english_columns_must_belong_to_resolved_table(self):
        for name in ("erp_加工方式", "erp_processing_method"):
            for prefix in ("", "i."):
                with self.subTest(name=name, prefix=prefix):
                    with self.assertRaisesRegex(SyncError, "BLOCKED"):
                        self.rewrite(
                            "SELECT " + prefix + "`" + name + "` FROM qms_material_issue i", [self.row])

    def test_real_registry_complete_package_omits_only_unchanged_fields(self):
        from qms_erp_sync import load_erp_field_registry
        registry = load_erp_field_registry()
        rows = self.migration.build_rename_manifest(registry)
        self.assertEqual(len(rows), 875)
        self.assertEqual(len({row.table_name for row in rows}), 11)
        self.assertEqual(sum(row.migration_kind == "split_source" for row in rows), 10)
        apply = self.migration.render_apply_sql(rows)
        self.assertEqual(apply.count("CHANGE COLUMN"), 865)
        self.assertEqual(apply.count("ADD COLUMN"), 10)
        self.assertEqual(apply.count("\nUPDATE "), 10)
        self.assertNotIn("DROP COLUMN", apply)
        self.assertNotIn("qms_completion_quantity", apply)
        self.assertNotIn("qms_scrap", apply)
        contract = self.migration.render_contract_sql(rows)
        self.assertEqual(contract.count("DROP COLUMN"), 5)
        # qms_material_issue's two unit fields retain both workbook values.
        query = self.rewrite("SELECT `erp_单位` FROM qms_material_issue", rows)
        self.assertEqual(query, "SELECT COALESCE(`erp_unit_replenishment_26e8962890`, `erp_unit_source_9659f2994f`) FROM qms_material_issue")


if __name__ == "__main__":
    unittest.main()
