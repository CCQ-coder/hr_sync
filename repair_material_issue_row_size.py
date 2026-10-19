"""Preview or apply the reviewed, zero-row qms_material_issue 1118 repair.

The sync application intentionally does not delete legacy columns. This
one-time maintenance command requires a schema snapshot and an explicit
--apply flag. Stop all sync writers and take a database backup first.
"""

from __future__ import annotations

import argparse
import json
import sys
import uuid
from pathlib import Path

import pymysql

from qms_erp_sync import load_erp_field_registry


ROOT = Path(__file__).resolve().parent
MANIFEST_PATH = ROOT / "sql" / "qms_material_issue_1118_manifest.json"


class RepairError(RuntimeError):
    pass


def quote_identifier(name: str) -> str:
    return "`" + name.replace("`", "``") + "`"


def read_columns(cursor, table: str) -> set[str]:
    cursor.execute(
        "SELECT column_name FROM information_schema.columns "
        "WHERE table_schema = DATABASE() AND table_name = %s",
        (table,),
    )
    return {row[0] for row in cursor.fetchall()}


def assert_empty(cursor, table: str) -> None:
    cursor.execute(f"SELECT 1 FROM {quote_identifier(table)} LIMIT 1")
    if cursor.fetchone() is not None:
        raise RepairError(f"{table} 已有数据；为避免丢失旧字段值，拒绝修改。")


def schema_change_sql(table: str, obsolete: list[str], missing_fields) -> tuple[str, tuple[str, ...]]:
    alterations = [f"DROP COLUMN {quote_identifier(name)}" for name in obsolete]
    alterations.extend(
        f"ADD COLUMN {quote_identifier(field.database_column)} LONGTEXT NULL COMMENT %s"
        for field in missing_fields
    )
    return f"ALTER TABLE {quote_identifier(table)} " + ", ".join(alterations), tuple(
        field.column_comment for field in missing_fields
    )


def repair(connection, manifest: dict, apply: bool) -> None:
    table = manifest["table"]
    backup = manifest["backup_table"]
    if table != "qms_material_issue" or not backup.startswith("qms_material_issue_schema_backup_"):
        raise RepairError("修复清单的目标表或备份表名无效。")
    registry = load_erp_field_registry()
    registered = {
        field.database_column: field for field in registry.fields if field.table_name == table
    }
    expected_obsolete = set(manifest["obsolete_columns"])
    expected_missing = set(manifest["missing_columns"])
    if (not expected_obsolete or not expected_missing
            or not all(name.startswith("erp_") for name in expected_obsolete)
            or expected_obsolete & registered.keys()
            or not expected_missing <= registered.keys()):
        raise RepairError("修复清单与当前字段注册表不一致。")

    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT engine, row_format FROM information_schema.tables "
            "WHERE table_schema = DATABASE() AND table_name = %s",
            (table,),
        )
        info = cursor.fetchone()
        if info != ("InnoDB", "Dynamic"):
            raise RepairError(f"目标表存储格式已变化：{info!r}。")
        columns = read_columns(cursor, table)
        obsolete = {name for name in columns if name.startswith("erp_")} - registered.keys()
        missing = registered.keys() - columns
        if (len(columns) != manifest["expected_column_count"]
                or obsolete != expected_obsolete or missing != expected_missing):
            raise RepairError("目标表结构已变化；请重新检查，不执行旧清单。")
        assert_empty(cursor, table)
        cursor.execute(
            "SELECT 1 FROM information_schema.tables WHERE table_schema = DATABASE() "
            "AND table_name = %s", (backup,)
        )
        if cursor.fetchone() is not None:
            raise RepairError(f"备份表 {backup} 已存在；拒绝覆盖。")

        obsolete_names = sorted(obsolete)
        missing_fields = [registered[name] for name in sorted(missing)]
        temporary = "tmp_material_repair_" + uuid.uuid4().hex[:12]
        sql, comments = schema_change_sql(table, obsolete_names, missing_fields)
        try:
            cursor.execute(
                f"CREATE TEMPORARY TABLE {quote_identifier(temporary)} "
                f"LIKE {quote_identifier(table)}"
            )
            trial_sql, trial_comments = schema_change_sql(temporary, obsolete_names, missing_fields)
            cursor.execute(trial_sql, trial_comments)
        finally:
            cursor.execute(f"DROP TEMPORARY TABLE IF EXISTS {quote_identifier(temporary)}")

        print(f"预检通过：{table} 当前 0 行；待清理旧列 {len(obsolete_names)} 个，待新增列 {len(missing_fields)} 个。")
        print(f"预定保留结构备份：{backup}")
        if not apply:
            print("仅预检，业务表未修改。")
            return

        cursor.execute(f"CREATE TABLE {quote_identifier(backup)} LIKE {quote_identifier(table)}")
        cursor.execute(
            f"INSERT INTO {quote_identifier(backup)} "
            f"SELECT * FROM {quote_identifier(table)}"
        )
        assert_empty(cursor, backup)
        assert_empty(cursor, table)
        cursor.execute(sql, comments)
        after = read_columns(cursor, table)
        if any(name in after for name in obsolete_names) or any(name not in after for name in missing):
            raise RepairError("ALTER 已执行，但字段验证未通过；请检查业务表和结构备份。")
        print(f"修复完成：{table} 已加入 {len(missing_fields)} 个字段；结构备份保留在 {backup}。")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True, help="本机 qms_erp_sync_config.json 路径")
    parser.add_argument("--apply", action="store_true", help="完成预检后修改目标数据库")
    args = parser.parse_args()
    try:
        manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        config = json.loads(args.config.read_text(encoding="utf-8-sig"))
        connection = pymysql.connect(
            host=config["database_host"], port=int(config["database_port"]),
            database=config["database_name"], user=config["database_username"],
            password=config["database_password"], connect_timeout=10,
            read_timeout=30, charset="utf8mb4", autocommit=True,
        )
        try:
            repair(connection, manifest, args.apply)
        finally:
            connection.close()
    except (OSError, KeyError, ValueError, pymysql.MySQLError, RepairError) as exc:
        print(f"修复未完成：{exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
