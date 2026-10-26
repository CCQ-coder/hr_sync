"""Generate reviewed, offline MySQL ERP migration artifacts; never connect to MySQL.

Run with --update-bi to rewrite the checked-in dashboard using explicit registry
mappings. A failed validation produces no output. SQL targets MySQL 5.7+/8.0;
a DBA must review preflight results before running apply and the separate contract.
"""
from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import List, Sequence

from qms_erp_sync import (
    ERP_FIELD_NAME_PATTERN, ERP_FIELD_TABLES, MYSQL_IDENTIFIER_LIMIT,
    ErpFieldRegistry, SyncError, erp_column_comment, load_erp_field_registry,
)


# These tables are new and created with English fields by the synchronizer.
NEW_ENGLISH_ONLY_TABLES = frozenset({"qms_completion_quantity", "qms_scrap"})


@dataclass(frozen=True)
class RenameManifestRow:
    table_name: str
    source_file: str
    sheet_name: str
    column_index: int
    excel_source_header: str
    excel_unique_header: str
    old_field: str
    new_field: str
    comment: str
    expected_field_definition: str = "LONGTEXT NULL"
    migration_kind: str = "change"


def _groups(rows):
    result = defaultdict(list)
    for row in rows:
        result[(row.table_name, row.old_field)].append(row)
    return result


def _validate(manifest):
    rows = sorted(manifest, key=lambda r: (r.table_name, r.old_field, r.new_field))
    targets = set()
    for row in rows:
        if row.table_name not in ERP_FIELD_TABLES:
            raise SyncError("迁移目标表不允许：" + row.table_name)
        if not ERP_FIELD_NAME_PATTERN.fullmatch(row.new_field):
            raise SyncError("迁移目标字段必须为英文标识符：" + row.new_field)
        if (not row.old_field.startswith("erp_") or re.search(r"[`\x00-\x1f\x7f]", row.old_field)
                or any(len(n.encode("utf-8")) > MYSQL_IDENTIFIER_LIMIT
                       for n in (row.old_field, row.new_field))):
            raise SyncError("迁移字段名无效或超过字节限制：" + row.old_field)
        if (row.expected_field_definition != "LONGTEXT NULL"
                or row.comment != erp_column_comment(row.excel_source_header)
                or len(row.comment) > 1024 or "\x00" in row.comment
                or not row.source_file or not row.sheet_name
                or row.column_index < 1 or row.migration_kind not in ("change", "split_source")):
            raise SyncError("迁移字段定义或来源元数据无效：" + row.old_field)
        key = row.table_name, row.new_field
        if key in targets:
            raise SyncError("迁移目标字段冲突：" + str(key))
        targets.add(key)
    for key, group in _groups(rows).items():
        if len(group) > 1:
            if (any(r.migration_kind != "split_source" for r in group)
                    or len({(r.source_file, r.sheet_name) for r in group}) != len(group)):
                raise SyncError("迁移旧字段冲突：" + str(key))
        elif group[0].migration_kind != "change":
            raise SyncError("迁移拆分组不完整：" + str(key))
        if key in targets and any(r.new_field != r.old_field for r in group):
            raise SyncError("迁移目标与旧字段交叉冲突：" + str(key))
    return rows


def build_rename_manifest(registry: ErpFieldRegistry) -> List[RenameManifestRow]:
    # Revalidate public registry.fields before consuming them.
    registry = ErpFieldRegistry(registry.fields)
    counts = Counter((f.table_name, f.legacy_database_column) for f in registry.fields)
    rows = [RenameManifestRow(
        f.table_name, f.source_file, f.sheet_name, f.column_index,
        f.excel_source_header, f.excel_unique_header, f.legacy_database_column,
        f.database_column, f.column_comment,
        migration_kind="split_source" if counts[(f.table_name, f.legacy_database_column)] > 1 else "change",
    ) for f in registry.fields if f.table_name not in NEW_ENGLISH_ONLY_TABLES]
    return [r for r in _validate(rows) if r.old_field != r.new_field]


def _literal(value):
    # All scripts establish NO_BACKSLASH_ESCAPES, then restore the session mode.
    return "'" + value.replace("'", "''") + "'"


def _identifier(value):
    return "`" + value.replace("`", "``") + "`"


def _begin(title):
    return (
        "-- " + title + "\n"
        "-- MySQL 5.7+/8.0. Select the intended database before running this file.\n"
        "-- Use a UTF-8 client. STOP synchronization and take a verified BACKUP first.\n"
        "-- DDL auto-commits; this is not a transaction or an idempotent rerun script.\n"
        "SET @erp_migration_saved_sql_mode = @@SESSION.sql_mode;\n"
        "SET SESSION sql_mode = CONCAT_WS(',', NULLIF(@@SESSION.sql_mode, ''), 'NO_BACKSLASH_ESCAPES');\n"
        "SET NAMES utf8mb4;\n\n"
    )


def _end():
    return "\nSET SESSION sql_mode = @erp_migration_saved_sql_mode;\n"


def _manifest_relation(rows):
    """An inline UNION-derived table, supported by both MySQL 5.7 and 8.0."""
    fields = ("table_name", "old_field", "new_field", "comment", "migration_kind")
    if not rows:
        return "(\nSELECT " + ", ".join("NULL AS " + f for f in fields) + " WHERE 1=0\n) AS m"
    return "(\n" + "\nUNION ALL\n".join(
        "SELECT " + ", ".join(_literal(getattr(r, f)) + " AS " + f for f in fields)
        for r in rows
    ) + "\n) AS m"


def _scope(row):
    return ("BINARY `source_file` = BINARY " + _literal(row.source_file)
            + " AND BINARY `sheet_name` = BINARY " + _literal(row.sheet_name))


def render_preflight_sql(manifest: Sequence[RenameManifestRow]) -> str:
    rows = _validate(manifest)
    tables = ", ".join(_literal(t) for t in sorted({r.table_name for r in rows})) or "NULL"
    sql = _begin("PREFLIGHT: inspect every result before approving apply")
    sql += "SELECT VERSION() AS mysql_version, DATABASE() AS selected_database, @erp_migration_saved_sql_mode AS original_sql_mode, @@SESSION.sql_mode AS effective_sql_mode;\n"
    sql += (
        "SELECT TABLE_NAME, COLUMN_NAME, ORDINAL_POSITION, COLUMN_TYPE, IS_NULLABLE,\n"
        "       COLUMN_DEFAULT, EXTRA, COLUMN_COMMENT, CHARACTER_SET_NAME, COLLATION_NAME, GENERATION_EXPRESSION\n"
        "FROM information_schema.columns\n"
        "WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME IN (" + tables + ")\n"
        "  AND LEFT(COLUMN_NAME, 4) = 'erp_'\nORDER BY TABLE_NAME, ORDINAL_POSITION;\n\n"
        "-- All following issue rows must be resolved. Manually modified definitions,\n"
        "-- collations/character sets, defaults, indexes and dependencies need DBA review.\n"
    )
    sql += (
        "SELECT m.*, CASE WHEN o.COLUMN_NAME IS NULL THEN 'missing_old_column'\n"
        " WHEN n.COLUMN_NAME IS NOT NULL THEN 'target_already_exists'\n"
        " ELSE 'unexpected_definition' END AS issue\n"
        "FROM " + _manifest_relation(rows) + "\n"
        "LEFT JOIN information_schema.columns o ON o.TABLE_SCHEMA = DATABASE() AND o.TABLE_NAME = m.table_name AND o.COLUMN_NAME = m.old_field\n"
        "LEFT JOIN information_schema.columns n ON n.TABLE_SCHEMA = DATABASE() AND n.TABLE_NAME = m.table_name AND n.COLUMN_NAME = m.new_field\n"
        "WHERE o.COLUMN_NAME IS NULL OR n.COLUMN_NAME IS NOT NULL OR LOWER(o.COLUMN_TYPE) <> 'longtext'\n"
        " OR o.IS_NULLABLE <> 'YES' OR o.COLUMN_DEFAULT IS NOT NULL OR o.EXTRA <> '' OR o.GENERATION_EXPRESSION <> '';\n"
    )
    split_tables = sorted({r.table_name for r in rows if r.migration_kind == "split_source"})
    for table in split_tables:
        sql += ("\n-- Exact source scopes must match the reviewed registry before backfill.\n"
                "SELECT `tenant_code`, `source_file`, `sheet_name`, COUNT(*) AS row_count FROM "
                + _identifier(table) + " GROUP BY `tenant_code`, `source_file`, `sheet_name`;\n")
    return sql + _end()


def render_apply_sql(manifest: Sequence[RenameManifestRow]) -> str:
    rows = _validate(manifest)
    sql = _begin("APPLY: BACKUP, STOP synchronization, review preflight, then run once")
    sql += "-- Requires zero preflight issues. Stop on the first SQL error; do not use --force.\n"
    by_table = defaultdict(list)
    for row in rows:
        action = ("CHANGE COLUMN " + _identifier(row.old_field) + " "
                  if row.migration_kind == "change" else "ADD COLUMN ")
        by_table[row.table_name].append(action + _identifier(row.new_field)
            + " LONGTEXT NULL COMMENT " + _literal(row.comment))
    for table, clauses in sorted(by_table.items()):
        sql += "\nALTER TABLE " + _identifier(table) + "\n  " + ",\n  ".join(clauses) + ";\n"
    for row in rows:
        if row.migration_kind == "split_source":
            sql += ("\nUPDATE " + _identifier(row.table_name) + " SET " + _identifier(row.new_field)
                    + " = " + _identifier(row.old_field) + "\nWHERE " + _scope(row) + ";\n")
    sql += "\n-- Split legacy columns are retained until verification and separate contract approval.\n"
    return sql + _end()


def render_verify_sql(manifest: Sequence[RenameManifestRow]) -> str:
    rows = _validate(manifest)
    sql = _begin("VERIFY before contract: every issue result set must be empty")
    relation = _manifest_relation(rows)
    sql += (
        "SELECT m.table_name, m.old_field, m.new_field, 'remaining_old_column' AS issue\n"
        "FROM " + relation + " JOIN information_schema.columns c ON c.TABLE_SCHEMA=DATABASE() AND c.TABLE_NAME=m.table_name AND c.COLUMN_NAME=m.old_field\n"
        "WHERE m.migration_kind = 'change'\nUNION ALL\n"
        "SELECT m.table_name, m.old_field, m.new_field, 'missing_new_column' FROM " + relation + "\n"
        "LEFT JOIN information_schema.columns c ON c.TABLE_SCHEMA=DATABASE() AND c.TABLE_NAME=m.table_name AND c.COLUMN_NAME=m.new_field WHERE c.COLUMN_NAME IS NULL\nUNION ALL\n"
        "SELECT m.table_name, m.old_field, m.new_field, 'comment_mismatch' FROM " + relation + "\n"
        "JOIN information_schema.columns c ON c.TABLE_SCHEMA=DATABASE() AND c.TABLE_NAME=m.table_name AND c.COLUMN_NAME=m.new_field WHERE BINARY c.COLUMN_COMMENT <> BINARY m.comment\nUNION ALL\n"
        "SELECT m.table_name, m.old_field, m.new_field, 'definition_mismatch' FROM " + relation + "\n"
        "JOIN information_schema.columns c ON c.TABLE_SCHEMA=DATABASE() AND c.TABLE_NAME=m.table_name AND c.COLUMN_NAME=m.new_field\n"
        "WHERE LOWER(c.COLUMN_TYPE) <> 'longtext' OR c.IS_NULLABLE <> 'YES' OR c.COLUMN_DEFAULT IS NOT NULL OR c.EXTRA <> '';\n"
        "\n-- Do not run the data checks below until the schema result above is clean.\n"
        "-- Informational per-tenant counts must agree; subsequent issue queries must return zero rows.\n"
    )
    for (table, old), group in _groups(rows).items():
        if group[0].migration_kind != "split_source":
            continue
        for row in group:
            sql += ("\nSELECT " + _literal(table) + " AS table_name, " + _literal(row.new_field)
                + " AS new_field, `tenant_code`, COUNT(" + _identifier(old) + ") AS legacy_non_null_count, COUNT("
                + _identifier(row.new_field) + ") AS new_non_null_count FROM " + _identifier(table)
                + " WHERE " + _scope(row) + " GROUP BY `tenant_code`;\n"
                + "SELECT 'split_value_mismatch' AS issue, " + _literal(row.new_field)
                + " AS new_field, `tenant_code`, COUNT(*) AS mismatch_count FROM " + _identifier(table)
                + " WHERE " + _scope(row) + " AND NOT (BINARY " + _identifier(old)
                + " <=> BINARY " + _identifier(row.new_field) + ") GROUP BY `tenant_code`;\n"
                + "SELECT 'split_value_outside_scope' AS issue, " + _literal(row.new_field)
                + " AS new_field, `tenant_code`, COUNT(*) AS unexpected_count FROM " + _identifier(table)
                + " WHERE NOT COALESCE((" + _scope(row) + "), FALSE) AND " + _identifier(row.new_field)
                + " IS NOT NULL GROUP BY `tenant_code`;\n")
        sql += ("SELECT 'unassigned_legacy_value' AS issue, " + _literal(old)
            + " AS old_field, `tenant_code`, `source_file`, `sheet_name`, COUNT(*) AS unassigned_count FROM "
            + _identifier(table) + " WHERE " + _identifier(old) + " IS NOT NULL AND NOT COALESCE(("
            + " OR ".join("(" + _scope(r) + ")" for r in group)
            + "), FALSE) GROUP BY `tenant_code`, `source_file`, `sheet_name`;\n")
    return sql + _end()


def render_contract_sql(manifest: Sequence[RenameManifestRow]) -> str:
    rows = _validate(manifest)
    sql = _begin("CONTRACT: DESTRUCTIVE separate DBA step, only AFTER verification is clean")
    sql += ("-- Keep sync stopped. Confirm backup, equal per-tenant scoped counts, zero\n"
            "-- value mismatches, zero outside-scope targets and zero unassigned legacy values.\n"
            "-- Confirm BI/other consumers use English fields. Do not run automatically with apply.\n")
    for (table, old), group in _groups(rows).items():
        if group[0].migration_kind == "split_source":
            sql += "ALTER TABLE " + _identifier(table) + " DROP COLUMN " + _identifier(old) + ";\n"
    return sql + _end()


# A conservative lexer for static example SELECTs, not a general SQL transpiler.
_TOKEN = re.compile(r"--[^\n]*|/\*[\s\S]*?\*/|'(?:''|\\.|[^'\\])*'|\"(?:\"\"|\\.|[^\"\\])*\"|`(?:``|[^`])*`|[\w]+|[^\s]", re.UNICODE)


def rewrite_bi_queries(sql: str, manifest: Sequence[RenameManifestRow], registry: ErpFieldRegistry) -> str:
    """Rewrite physical fields using explicit query scope and the complete schema."""
    rows = _validate(manifest)
    registry = ErpFieldRegistry(registry.fields)
    mapping = defaultdict(list)
    for row in rows:
        mapping[row.old_field].append(row)
    english_tables = defaultdict(set)
    for field in registry.fields:
        english_tables[field.database_column].add(field.table_name)
    tokens = [m for m in _TOKEN.finditer(sql)
              if not m.group().startswith(("--", "/*"))]
    depths, depth = [], 0
    open_parentheses, closing_parentheses = [], {}
    for index, token in enumerate(tokens):
        if token.group() == ")":
            depth -= 1
            if open_parentheses:
                closing_parentheses[open_parentheses.pop()] = index
        depths.append(depth)
        if token.group() == "(":
            open_parentheses.append(index)
            depth += 1
    blocks = []
    declarations = set()
    # WITH declarations precede their SELECT blocks. Mark only names at the
    # syntactic declaration positions; inner physical fields still validate.
    for i, token in enumerate(tokens):
        if token.group().upper() != "WITH":
            continue
        k = i + 1
        if k < len(tokens) and tokens[k].group().upper() == "RECURSIVE":
            k += 1
        while k + 2 < len(tokens):
            name_index = k
            k += 1
            column_names = []
            if tokens[k].group() == "(" and k in closing_parentheses:
                end_columns = closing_parentheses[k]
                column_names = [j for j in range(k + 1, end_columns) if tokens[j].group() != ","]
                k = end_columns + 1
            if (k + 1 >= len(tokens) or tokens[k].group().upper() != "AS"
                    or tokens[k + 1].group() != "(" or k + 1 not in closing_parentheses):
                break
            declarations.add(name_index)
            declarations.update(column_names)
            k = closing_parentheses[k + 1] + 1
            if k >= len(tokens) or tokens[k].group() != ",":
                break
            k += 1
    for i, token in enumerate(tokens):
        if token.group().upper() != "SELECT":
            continue
        level, end = depths[i], len(tokens)
        for j in range(i + 1, len(tokens)):
            if (depths[j] < level or (depths[j] == level and tokens[j].group().upper() in (";", "UNION", "SELECT"))):
                end = j
                break
        tables, aliases, select_aliases = set(), {}, set()
        in_from = False
        from_start = end
        for j in range(i + 1, end):
            if depths[j] != level:
                continue
            if tokens[j].group().upper() == "FROM":
                from_start = j
                break
            if tokens[j].group().upper() == "AS" and j + 1 < end:
                declarations.add(j + 1)
                select_aliases.add(tokens[j + 1].group().strip("`"))
        segment_start = i + 1
        for boundary in range(i + 1, from_start + 1):
            if boundary != from_start and not (depths[boundary] == level and tokens[boundary].group() == ","):
                continue
            last = boundary - 1
            if last > segment_start and last not in declarations:
                previous = tokens[last - 1].group()
                candidate = tokens[last].group().strip("`")
                # An identifier following a complete expression is an implicit
                # SELECT alias. Operators, dots and DISTINCT/ALL are not ends.
                expression_end = (previous == ")" or previous.startswith(("'", '"', "`"))
                                  or bool(re.fullmatch(r"\w+", previous)))
                if (candidate.startswith("erp_") and expression_end
                        and previous.upper() not in ("DISTINCT", "ALL", "AS", "COLLATE", "BINARY", "INTERVAL")):
                    declarations.add(last)
                    select_aliases.add(candidate)
            segment_start = boundary + 1
        for j in range(i + 1, end - 1):
            if depths[j] != level:
                continue
            word = tokens[j].group().upper()
            if word in ("WHERE", "GROUP", "ORDER", "LIMIT", "HAVING"):
                in_from = False
            if word == "FROM":
                in_from = True
            if word not in ("FROM", "JOIN") and not (word == "," and in_from):
                continue
            relation_start = j + 1
            if tokens[relation_start].group() == "(":
                relation_end = closing_parentheses.get(relation_start)
                if relation_end is None:
                    raise SyncError("BLOCKED: BI 派生表括号不完整")
                table = None  # Never infer physical ownership through a projection.
                k = relation_end + 1
            else:
                table = tokens[relation_start].group().strip("`")
                declarations.add(relation_start)
                aliases[table] = table
                k = relation_start + 1
                if table in ERP_FIELD_TABLES:
                    tables.add(table)
            if k < end and tokens[k].group().upper() == "AS":
                k += 1
            if k < end and re.fullmatch(r"`?\w+`?", tokens[k].group()) and tokens[k].group().upper() not in (
                    "WHERE", "ON", "JOIN", "LEFT", "RIGHT", "INNER", "CROSS", "GROUP", "ORDER", "LIMIT", "HAVING"):
                aliases[tokens[k].group().strip("`")] = table
                declarations.add(k)
        blocks.append((i, end, tables, aliases, select_aliases, from_start))
    replacements = []
    for i, token in enumerate(tokens):
        name = token.group().strip("`")
        if not name.startswith("erp_"):
            continue
        if i in declarations or (i + 1 < len(tokens) and tokens[i + 1].group() == "."):
            continue
        context = [b for b in blocks if b[0] <= i < b[1]]
        block = max(context, key=lambda b: b[0]) if context else None
        if block is None:
            raise SyncError("BLOCKED: BI 字段查询作用域无法确定：" + name)
        qualified = i >= 2 and tokens[i - 1].group() == "."
        if not qualified and name in block[4] and i > block[5]:
            # SELECT aliases are visible in ORDER/GROUP/HAVING, not WHERE/ON.
            clause = ""
            for j in range(block[5], i):
                if depths[j] == depths[block[0]] and tokens[j].group().upper() in (
                        "WHERE", "ON", "ORDER", "GROUP", "HAVING", "LIMIT"):
                    clause = tokens[j].group().upper()
            if clause in ("ORDER", "GROUP", "HAVING"):
                continue
        prefix, start = "", token.start()
        source_tables = block[2]
        if qualified:
            alias = tokens[i - 2].group().strip("`")
            table = block[3].get(alias) if block else None
            if table is None:
                raise SyncError("BLOCKED: BI 表别名无法确定：" + alias)
            source_tables = {table}
            prefix, start = tokens[i - 2].group() + ".", tokens[i - 2].start()
        if name in english_tables:
            owners = english_tables[name] & source_tables
            if len(owners) != 1:
                raise SyncError("BLOCKED: BI 英文字段不属于唯一来源表：" + name)
            continue
        candidates = [r for r in mapping.get(name, []) if r.table_name in source_tables]
        if not candidates:
            raise SyncError("BLOCKED: BI 字段无明确来源表映射：" + name)
        if len({r.table_name for r in candidates}) > 1:
            raise SyncError("BLOCKED: BI 字段来源表存在歧义：" + name)
        targets = sorted({r.new_field for r in candidates})
        if len(targets) == 1:
            output = prefix + _identifier(targets[0])
        elif (len(targets) > 1 and len({r.table_name for r in candidates}) == 1
              and all(r.migration_kind == "split_source" for r in candidates)
              and len({r.excel_source_header for r in candidates}) == 1):
            output = "COALESCE(" + ", ".join(prefix + _identifier(t) for t in targets) + ")"
        else:
            raise SyncError("BLOCKED: BI 字段映射存在歧义：" + name)
        replacements.append((start, token.end(), output))
    for start, end, output in reversed(replacements):
        sql = sql[:start] + output + sql[end:]
    return sql


def main(argv=None):
    root = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", type=Path, default=root / "erp_field_registry.json")
    parser.add_argument("--output-root", type=Path, default=root)
    parser.add_argument("--bi-file", type=Path, default=root / "bi_dashboard_queries.sql")
    parser.add_argument("--update-bi", action="store_true")
    parser.add_argument("--skip-bi-validation", action="store_true",
                        help="Generate migration SQL for a customer source without validating the BI query file")
    args = parser.parse_args(argv)
    if args.skip_bi_validation and args.update_bi:
        parser.error("--skip-bi-validation cannot be combined with --update-bi")
    try:
        registry = load_erp_field_registry(args.registry)
        rows = build_rename_manifest(registry)
        rewritten = None if args.skip_bi_validation else rewrite_bi_queries(
            args.bi_file.read_text(encoding="utf-8"), rows, registry)
        artifacts = {
            "sql/erp_field_rename_preflight.sql": render_preflight_sql(rows),
            "sql/erp_field_rename_apply.sql": render_apply_sql(rows),
            "sql/erp_field_rename_verify.sql": render_verify_sql(rows),
            "sql/erp_field_rename_contract.sql": render_contract_sql(rows),
            "outputs/erp_field_rename_manifest.json": json.dumps(
                {"schema_version": 1, "rows": [asdict(r) for r in rows]}, ensure_ascii=False, indent=2) + "\n",
        }
        for relative, content in artifacts.items():
            path = args.output_root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
        if args.update_bi:
            args.bi_file.write_text(rewritten, encoding="utf-8")
        split = [r for r in rows if r.migration_kind == "split_source"]
        print("Generated: {} rows, {} tables, {} CHANGE, {} split targets in {} groups.".format(
            len(rows), len({r.table_name for r in rows}), len(rows) - len(split), len(split), len(_groups(split))))
        return 0
    except (SyncError, OSError) as exc:
        print(str(exc) if str(exc).startswith("BLOCKED:") else "BLOCKED: " + str(exc))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
