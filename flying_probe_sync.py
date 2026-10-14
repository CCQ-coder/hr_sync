"""Validate and version flying-probe program TXT files into QMS MySQL.

The flying-probe share stores raw Wantongda job INI bytes with a ``.txt``
extension.  These files are static program/test-counter snapshots, not ERP
work orders and not equipment telemetry.  Keeping their import path separate
from the ERP synchronizer prevents accidental data-model mixing.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import uuid
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, dataclass
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

import pymysql
from pymysql import MySQLError


APP_NAME = "QMS 飞针数据同步工具"
PARSER_VERSION = "2026-09-20.1"
DEFAULT_SOURCE_DIRECTORY = r"\\Scbgx\数字化\飞针机"
DEFAULT_MAX_DURATION_HOURS = 72
MYSQL_IDENTIFIER_MAX_LENGTH = 64

# Tables are deliberately approved mappings, rather than names derived from a
# share folder.  The raw data stays separate per device and an unexpected
# folder cannot cause arbitrary SQL identifiers to be created.
DEVICE_TABLES: Mapping[str, str] = {
    "25-EP-427": "qms_flyprobe_25_ep_427",
    "27-EP-428": "qms_flyprobe_27_ep_428",
    "测试设备1": "qms_flyprobe_test_device_1",
}
FILE_VERSION_TABLE = "qms_flyprobe_file_version"
SYNC_ERROR_TABLE = "qms_flyprobe_sync_error"

EXPECTED_KEYS: Tuple[str, ...] = (
    "Pad_Net_Count",
    "Job_Extents",
    "A_Align",
    "Reference_Net",
    "Pads_Per_Side",
    "B_Align",
    "Orientation",
    "Panel_Obsolete",
    "Panel_Layout",
    "Test_Counters",
    "Want_Ext_Resist_Test",
)
INT_TOKEN_PATTERN = re.compile(r"-?(?:0|[1-9]\d*)$")
# Most Wantongda files use H+:MM:SS.  Older/exported zero-duration records
# use the compact M:SS spelling (for example ``0:00``), which is equivalent
# to 00:00:00 and must not be rejected as malformed.
DURATION_PATTERN = re.compile(r"(\d+):(\d{2}):(\d{2})$")
COMPACT_DURATION_PATTERN = re.compile(r"(\d+):(\d{2})$")
SAFE_TABLE_PATTERN = re.compile(r"[a-z][a-z0-9_]*$")
MAX_SIGNED_BIGINT = 2**63 - 1
MIN_SIGNED_BIGINT = -(2**63)
MAX_UNSIGNED_BIGINT = 2**64 - 1


class FlyingProbeSyncError(RuntimeError):
    """A validation or database condition safe to show to the operator."""


@dataclass(frozen=True)
class ValidationIssue:
    severity: str
    code: str
    message: str
    field: str = ""
    raw_value: str = ""


@dataclass(frozen=True)
class ParsedProbeFile:
    values: Mapping[str, Any]
    issues: Tuple[ValidationIssue, ...]
    raw_text: str
    encoding: str

    @property
    def validation_status(self) -> str:
        if any(issue.severity == "ERROR" for issue in self.issues):
            return "INVALID"
        if any(issue.severity == "WARNING" for issue in self.issues):
            return "WARNING"
        return "VALID"


@dataclass(frozen=True)
class ProbeFileRecord:
    source_root: Path
    source_path: Path
    source_rel_path: str
    device_code: str
    source_file_name: str
    source_hash: str
    source_key: str
    source_mtime: datetime
    source_size_bytes: int
    parsed: ParsedProbeFile

    @property
    def validation_status(self) -> str:
        return self.parsed.validation_status


@dataclass(frozen=True)
class IgnoredSourceFile:
    source_rel_path: str
    reason: str


@dataclass(frozen=True)
class ScanResult:
    records: Tuple[ProbeFileRecord, ...]
    ignored_files: Tuple[IgnoredSourceFile, ...]

    def summary(self) -> Dict[str, Any]:
        statuses = {"VALID": 0, "WARNING": 0, "INVALID": 0}
        issue_counts: Dict[str, int] = {}
        per_device: Dict[str, Dict[str, int]] = {}
        for record in self.records:
            statuses[record.validation_status] += 1
            device = per_device.setdefault(
                record.device_code,
                {"files": 0, "valid": 0, "warning": 0, "invalid": 0},
            )
            device["files"] += 1
            device[record.validation_status.lower()] += 1
            for issue in record.parsed.issues:
                issue_counts[issue.code] = issue_counts.get(issue.code, 0) + 1
        return {
            "source_directory": str(self.records[0].source_root) if self.records else "",
            "files_scanned": len(self.records),
            "valid_files": statuses["VALID"],
            "warning_files": statuses["WARNING"],
            "invalid_files": statuses["INVALID"],
            "ignored_files": len(self.ignored_files),
            "devices": per_device,
            "issue_counts": dict(sorted(issue_counts.items())),
            "ignored": [asdict(item) for item in self.ignored_files],
        }


@dataclass(frozen=True)
class SyncResult:
    scanned_files: int
    valid_files: int
    warning_files: int
    invalid_files: int
    ignored_files: int
    imported_files: int
    new_versions: int
    existing_versions: int
    skipped_invalid_files: int
    issue_rows_upserted: int
    dry_run: bool


def _issue(
    issues: List[ValidationIssue], severity: str, code: str, message: str,
    field: str = "", raw_value: str = "",
) -> None:
    issues.append(ValidationIssue(severity, code, message, field, raw_value))


def _decimal(value: str, field: str, issues: List[ValidationIssue]) -> Optional[Decimal]:
    try:
        number = Decimal(value)
    except (InvalidOperation, ValueError):
        _issue(issues, "ERROR", "INVALID_DECIMAL", "小数格式无效。", field, value)
        return None
    if not number.is_finite():
        _issue(issues, "ERROR", "INVALID_DECIMAL", "小数必须是有限值。", field, value)
        return None
    return number


def _parse_int_values(
    raw_value: str,
    field: str,
    count: int,
    issues: List[ValidationIssue],
    non_negative: bool,
) -> List[Optional[int]]:
    tokens = raw_value.split()
    if len(tokens) != count:
        _issue(
            issues, "ERROR", "FIELD_VALUE_COUNT", f"{field} 必须包含 {count} 个整数。",
            field, raw_value,
        )
        return [None] * count
    values: List[Optional[int]] = []
    for token in tokens:
        if not INT_TOKEN_PATTERN.fullmatch(token):
            _issue(issues, "ERROR", "INVALID_INTEGER", f"{field} 存在无效整数。", field, raw_value)
            return [None] * count
        value = int(token)
        if value < MIN_SIGNED_BIGINT or value > MAX_SIGNED_BIGINT:
            _issue(issues, "ERROR", "INTEGER_OUT_OF_RANGE", f"{field} 超出 MySQL BIGINT 范围。", field, raw_value)
            return [None] * count
        if non_negative and value < 0:
            _issue(issues, "ERROR", "NEGATIVE_UNSIGNED_VALUE", f"{field} 不允许负数。", field, raw_value)
            return [None] * count
        values.append(value)
    return values


def _set_values(target: Dict[str, Any], prefix: str, values: Sequence[Optional[int]]) -> None:
    for index, value in enumerate(values, start=1):
        target[f"{prefix}_{index}"] = value


def _decode_probe_bytes(raw: bytes, issues: List[ValidationIssue]) -> Tuple[str, str]:
    for encoding in ("utf-8-sig", "gb18030"):
        try:
            return raw.decode(encoding), encoding
        except UnicodeDecodeError:
            continue
    _issue(issues, "ERROR", "TEXT_DECODE_FAILED", "TXT 无法按 UTF-8 或 GB18030 解码。")
    return raw.decode("utf-8", errors="replace"), "utf-8-replace"


def _status_from_issues(issues: Iterable[ValidationIssue]) -> str:
    levels = {issue.severity for issue in issues}
    if "ERROR" in levels:
        return "INVALID"
    if "WARNING" in levels:
        return "WARNING"
    return "VALID"


def parse_flying_probe_bytes(raw: bytes, max_duration_hours: int = DEFAULT_MAX_DURATION_HOURS) -> ParsedProbeFile:
    """Parse the fixed Wantongda text format without inventing business meaning."""
    if max_duration_hours < 1:
        raise FlyingProbeSyncError("最大测试时长必须至少为 1 小时。")

    issues: List[ValidationIssue] = []
    raw_text, encoding = _decode_probe_bytes(raw, issues)
    parsed_lines: List[Tuple[str, str]] = []
    fields: Dict[str, str] = {}
    for line_number, original_line in enumerate(raw_text.splitlines(), start=1):
        line = original_line.strip()
        if not line:
            continue
        parts = line.split(None, 1)
        key = parts[0]
        value = parts[1].strip() if len(parts) == 2 else ""
        if key in fields:
            _issue(issues, "ERROR", "DUPLICATE_FIELD", "TXT 出现重复字段。", key, original_line)
            continue
        fields[key] = value
        parsed_lines.append((key, value))

    actual_order = tuple(key for key, _ in parsed_lines)
    if len(parsed_lines) != len(EXPECTED_KEYS):
        _issue(
            issues, "ERROR", "RECORD_COUNT", "TXT 必须包含 11 条非空字段记录。",
            raw_value=str(len(parsed_lines)),
        )
    unknown_keys = [key for key in fields if key not in EXPECTED_KEYS]
    for key in unknown_keys:
        _issue(issues, "ERROR", "UNKNOWN_FIELD", "TXT 包含未定义字段。", key, fields[key])
    missing_keys = [key for key in EXPECTED_KEYS if key not in fields]
    for key in missing_keys:
        _issue(issues, "ERROR", "MISSING_FIELD", "TXT 缺少必填字段。", key)
    if actual_order != EXPECTED_KEYS:
        _issue(
            issues, "ERROR", "FIELD_ORDER", "TXT 字段顺序不符合万通达固定格式。",
            raw_value=" -> ".join(actual_order),
        )

    values: Dict[str, Any] = {
        "pad_count": None,
        "net_count": None,
        "reference_net": None,
        "panel_obsolete_marker": None,
        "test_total": None,
        "test_passed": None,
        "test_failed": None,
        "test_duration_raw": None,
        "test_duration_seconds": None,
        "resist_test_mode": None,
        "resist_param_1": None,
        "resist_param_2": None,
    }
    for prefix, count in (
        ("job_extent", 4), ("a_align", 6), ("pads_side", 3), ("b_align", 7),
        ("orientation", 4), ("panel_layout", 5),
    ):
        for index in range(1, count + 1):
            values[f"{prefix}_{index}"] = None

    def required_value(key: str) -> str:
        return fields.get(key, "")

    pad_net = _parse_int_values(required_value("Pad_Net_Count"), "Pad_Net_Count", 2, issues, True)
    values["pad_count"], values["net_count"] = pad_net

    _set_values(
        values,
        "job_extent",
        _parse_int_values(required_value("Job_Extents"), "Job_Extents", 4, issues, False),
    )
    if values["job_extent_1"] is not None and values["job_extent_3"] is not None:
        if values["job_extent_1"] >= values["job_extent_3"]:
            _issue(issues, "ERROR", "INVALID_JOB_EXTENTS", "Job_Extents 必须满足 xmin < xmax。", "Job_Extents", required_value("Job_Extents"))
    if values["job_extent_2"] is not None and values["job_extent_4"] is not None:
        if values["job_extent_2"] >= values["job_extent_4"]:
            _issue(issues, "ERROR", "INVALID_JOB_EXTENTS", "Job_Extents 必须满足 ymin < ymax。", "Job_Extents", required_value("Job_Extents"))

    _set_values(values, "a_align", _parse_int_values(required_value("A_Align"), "A_Align", 6, issues, False))
    reference_net = _parse_int_values(required_value("Reference_Net"), "Reference_Net", 1, issues, False)
    values["reference_net"] = reference_net[0]
    _set_values(values, "pads_side", _parse_int_values(required_value("Pads_Per_Side"), "Pads_Per_Side", 3, issues, True))
    _set_values(values, "b_align", _parse_int_values(required_value("B_Align"), "B_Align", 7, issues, False))

    orientation = _parse_int_values(required_value("Orientation"), "Orientation", 4, issues, True)
    if any(value not in (0, 1, None) for value in orientation):
        _issue(issues, "ERROR", "INVALID_ORIENTATION", "Orientation 只能由 0 或 1 构成。", "Orientation", required_value("Orientation"))
    _set_values(values, "orientation", orientation)

    panel_marker = required_value("Panel_Obsolete")
    values["panel_obsolete_marker"] = 1 if "Panel_Obsolete" in fields else None
    if panel_marker:
        _issue(issues, "ERROR", "PANEL_OBSOLETE_VALUE", "Panel_Obsolete 不应带参数。", "Panel_Obsolete", panel_marker)
    _set_values(values, "panel_layout", _parse_int_values(required_value("Panel_Layout"), "Panel_Layout", 5, issues, True))

    # Test_Counters has three integer counters followed by a duration, so it
    # is parsed separately from the fixed all-integer fields above.
    test_tokens = required_value("Test_Counters").split()
    if len(test_tokens) != 4:
        _issue(issues, "ERROR", "FIELD_VALUE_COUNT", "Test_Counters 必须包含 3 个计数和 1 个时长。", "Test_Counters", required_value("Test_Counters"))
    else:
        counter_values = _parse_int_values(" ".join(test_tokens[:3]), "Test_Counters", 3, issues, True)
        values["test_total"], values["test_passed"], values["test_failed"] = counter_values
        values["test_duration_raw"] = test_tokens[3]
        duration_match = DURATION_PATTERN.fullmatch(test_tokens[3])
        compact_duration_match = COMPACT_DURATION_PATTERN.fullmatch(test_tokens[3])
        if duration_match is None and compact_duration_match is None:
            _issue(issues, "ERROR", "INVALID_DURATION", "测试时长必须是 H+:MM:SS。", "Test_Counters", test_tokens[3])
        else:
            if duration_match is not None:
                hours, minutes, seconds = (int(part) for part in duration_match.groups())
            else:
                minutes, seconds = (int(part) for part in compact_duration_match.groups())
                hours = 0
            if minutes > 59 or seconds > 59:
                _issue(issues, "ERROR", "INVALID_DURATION", "测试时长的分钟和秒必须小于 60。", "Test_Counters", test_tokens[3])
            elif hours > max_duration_hours:
                _issue(
                    issues, "ERROR", "DURATION_EXCEEDS_LIMIT",
                    f"测试时长超过已配置的 {max_duration_hours} 小时上限。", "Test_Counters", test_tokens[3],
                )
            else:
                values["test_duration_seconds"] = hours * 3600 + minutes * 60 + seconds
        if (
            values["test_total"] is not None
            and values["test_passed"] is not None
            and values["test_failed"] is not None
            and values["test_total"] != values["test_passed"] + values["test_failed"]
        ):
            _issue(issues, "ERROR", "TEST_COUNTER_MISMATCH", "测试总数必须等于通过数加失败数。", "Test_Counters", required_value("Test_Counters"))
        elif values["test_total"] == 0:
            _issue(issues, "WARNING", "ZERO_TEST_COUNTER", "测试计数为 0，已保留但需确认是否未执行测试。", "Test_Counters", required_value("Test_Counters"))

    resist_tokens = required_value("Want_Ext_Resist_Test").split()
    if len(resist_tokens) != 3:
        _issue(issues, "ERROR", "FIELD_VALUE_COUNT", "Want_Ext_Resist_Test 必须包含模式和两个参数。", "Want_Ext_Resist_Test", required_value("Want_Ext_Resist_Test"))
    else:
        mode = _parse_int_values(resist_tokens[0], "Want_Ext_Resist_Test", 1, issues, True)
        values["resist_test_mode"] = mode[0]
        values["resist_param_1"] = _decimal(resist_tokens[1], "Want_Ext_Resist_Test", issues)
        values["resist_param_2"] = _decimal(resist_tokens[2], "Want_Ext_Resist_Test", issues)

    side_values = [values[f"pads_side_{index}"] for index in range(1, 4)]
    if values["pad_count"] is not None and all(value is not None for value in side_values):
        if values["pad_count"] != sum(int(value) for value in side_values):
            _issue(
                issues, "WARNING", "PAD_SIDE_TOTAL_MISMATCH",
                "焊盘总数与各面焊盘数之和不一致，已保留原始值。", "Pads_Per_Side",
                required_value("Pads_Per_Side"),
            )
    orientation_values = tuple(values[f"orientation_{index}"] for index in range(1, 5))
    if all(value is not None for value in orientation_values) and orientation_values != (1, 1, 0, 0):
        _issue(issues, "WARNING", "NONDEFAULT_ORIENTATION", "方向配置不是当前主流默认组合。", "Orientation", required_value("Orientation"))
    layout_values = tuple(values[f"panel_layout_{index}"] for index in range(1, 6))
    if all(value is not None for value in layout_values) and layout_values != (1, 1, 1, 0, 0):
        _issue(issues, "WARNING", "NONDEFAULT_PANEL_LAYOUT", "拼板配置不是当前主流默认组合。", "Panel_Layout", required_value("Panel_Layout"))
    b_align_values = tuple(values[f"b_align_{index}"] for index in range(1, 8))
    if all(value is not None for value in b_align_values) and b_align_values != (0, 0, 0, 0, 0, 0, 0):
        _issue(issues, "WARNING", "NONDEFAULT_B_ALIGN", "B 对位参数为非默认值，已正常保留。", "B_Align", required_value("B_Align"))

    return ParsedProbeFile(values=values, issues=tuple(issues), raw_text=raw_text, encoding=encoding)


def _source_key(tenant_code: str, device_code: str, source_rel_path: str, source_hash: str) -> str:
    payload = "\0".join((tenant_code, device_code, source_rel_path.casefold(), source_hash))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _build_probe_record(
    root: Path,
    path: Path,
    tenant_code: str,
    max_duration_hours: int,
    device_tables: Mapping[str, str],
) -> ProbeFileRecord:
    """Read one network-share file once and construct its immutable result."""
    relative = path.relative_to(root)
    relative_text = relative.as_posix()
    device_code = relative.parts[0]
    raw = path.read_bytes()
    parsed = parse_flying_probe_bytes(raw, max_duration_hours)
    if device_code not in device_tables:
        issues = list(parsed.issues)
        _issue(issues, "ERROR", "UNKNOWN_DEVICE", "设备目录未配置目标 QMS 业务表。", "device_code", device_code)
        parsed = ParsedProbeFile(parsed.values, tuple(issues), parsed.raw_text, parsed.encoding)
    stat = path.stat()
    digest = hashlib.sha256(raw).hexdigest()
    return ProbeFileRecord(
        root, path, relative_text, device_code, path.name, digest,
        _source_key(tenant_code, device_code, relative_text, digest),
        datetime.fromtimestamp(stat.st_mtime), stat.st_size, parsed,
    )


def scan_source_directory(
    source_directory: Path,
    tenant_code: str,
    max_duration_hours: int = DEFAULT_MAX_DURATION_HOURS,
    device_tables: Mapping[str, str] = DEVICE_TABLES,
    scan_workers: int = 12,
) -> ScanResult:
    """Read all candidate files and perform a complete no-write preflight."""
    root = Path(source_directory)
    if not root.is_dir():
        raise FlyingProbeSyncError(f"飞针数据目录不存在或不是目录：{root}")
    if not tenant_code.strip():
        raise FlyingProbeSyncError("tenant_code 不能为空。")

    if scan_workers < 1:
        raise FlyingProbeSyncError("扫描并发数必须至少为 1。")

    candidate_paths: List[Path] = []
    ignored: List[IgnoredSourceFile] = []
    for path in sorted((candidate for candidate in root.rglob("*") if candidate.is_file()), key=lambda item: item.relative_to(root).as_posix().casefold()):
        relative = path.relative_to(root)
        relative_text = relative.as_posix()
        if path.suffix.casefold() != ".txt":
            ignored.append(IgnoredSourceFile(relative_text, "仅同步设备子目录中的 .txt 文件"))
            continue
        if len(relative.parts) < 2:
            ignored.append(IgnoredSourceFile(relative_text, "TXT 必须位于设备子目录中，无法确定设备归属"))
            continue
        candidate_paths.append(path)
    worker_count = min(scan_workers, len(candidate_paths))
    if worker_count:
        with ThreadPoolExecutor(max_workers=worker_count, thread_name_prefix="flyprobe-scan") as executor:
            futures = [
                executor.submit(_build_probe_record, root, path, tenant_code, max_duration_hours, device_tables)
                for path in candidate_paths
            ]
            records = [future.result() for future in futures]
    else:
        records = []
    if not records:
        raise FlyingProbeSyncError(f"目录中没有可校验的飞针 TXT：{root}")
    return ScanResult(tuple(records), tuple(ignored))


def _safe_table_name(table_name: str) -> str:
    if (
        not SAFE_TABLE_PATTERN.fullmatch(table_name)
        or len(table_name) > MYSQL_IDENTIFIER_MAX_LENGTH
        or table_name not in set(DEVICE_TABLES.values()) | {FILE_VERSION_TABLE, SYNC_ERROR_TABLE}
    ):
        raise FlyingProbeSyncError(f"不允许的飞针目标表：{table_name}")
    return f"`{table_name}`"


def _validation_messages(issues: Sequence[ValidationIssue]) -> str:
    return json.dumps([asdict(issue) for issue in issues], ensure_ascii=False, separators=(",", ":"))


class FlyingProbeDatabase:
    """Versioned MySQL writer for approved device-specific fly-probe tables."""

    def __init__(self, config: Mapping[str, Any]):
        self.host = str(config.get("database_host", "")).strip()
        self.port = str(config.get("database_port", "")).strip()
        self.database = str(config.get("database_name", "")).strip()
        self.username = str(config.get("database_username", "")).strip()
        self.password = str(config.get("database_password", ""))
        self.tenant_code = str(config.get("tenant_code", "")).strip()
        try:
            self.timeout = int(config.get("request_timeout_seconds", 30))
            self.port_number = int(self.port)
        except (TypeError, ValueError) as exc:
            raise FlyingProbeSyncError("数据库端口和超时时间必须为整数。") from exc
        if not all((self.host, self.database, self.username, self.tenant_code)):
            raise FlyingProbeSyncError("数据库主机、库名、账号和 tenant_code 必须完整配置。")

    def _connect(self):
        try:
            return pymysql.connect(
                host=self.host,
                port=self.port_number,
                database=self.database,
                user=self.username,
                password=self.password,
                connect_timeout=self.timeout,
                charset="utf8mb4",
                autocommit=False,
            )
        except MySQLError as exc:
            raise FlyingProbeSyncError(f"无法连接 QMS MySQL 数据库：{exc}") from exc

    def test_connection(self) -> None:
        connection = self._connect()
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT DATABASE(), VERSION()")
                cursor.fetchone()
            connection.rollback()
        except MySQLError as exc:
            raise FlyingProbeSyncError(f"QMS MySQL 连接测试失败：{exc}") from exc
        finally:
            connection.close()

    @staticmethod
    def _ensure_audit_schema(cursor) -> None:
        cursor.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {_safe_table_name(FILE_VERSION_TABLE)} (
                id CHAR(36) NOT NULL,
                tenant_code VARCHAR(64) NOT NULL,
                device_code VARCHAR(255) NOT NULL,
                source_rel_path VARCHAR(500) NOT NULL,
                source_file_name VARCHAR(255) NOT NULL,
                source_sha256 CHAR(64) NOT NULL,
                source_key CHAR(64) NOT NULL,
                source_mtime DATETIME(6) NOT NULL,
                source_size_bytes BIGINT UNSIGNED NOT NULL,
                parser_version VARCHAR(32) NOT NULL,
                validation_status VARCHAR(16) NOT NULL,
                validation_messages LONGTEXT NOT NULL,
                raw_text MEDIUMTEXT NOT NULL,
                text_encoding VARCHAR(32) NOT NULL,
                is_current TINYINT(1) NOT NULL DEFAULT 1,
                first_seen_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
                last_seen_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
                created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
                updated_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
                PRIMARY KEY (id),
                UNIQUE KEY uq_flyprobe_version_source_key (tenant_code, source_key),
                KEY idx_flyprobe_version_current (tenant_code, device_code, source_rel_path(300), is_current),
                KEY idx_flyprobe_version_status (tenant_code, validation_status, last_seen_at)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """
        )
        cursor.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {_safe_table_name(SYNC_ERROR_TABLE)} (
                id CHAR(36) NOT NULL,
                tenant_code VARCHAR(64) NOT NULL,
                file_version_id CHAR(36) NOT NULL,
                issue_fingerprint CHAR(64) NOT NULL,
                severity VARCHAR(16) NOT NULL,
                issue_code VARCHAR(64) NOT NULL,
                issue_field VARCHAR(128) NOT NULL DEFAULT '',
                message VARCHAR(1000) NOT NULL,
                raw_value LONGTEXT NOT NULL,
                first_seen_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
                last_seen_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
                created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
                updated_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
                PRIMARY KEY (id),
                UNIQUE KEY uq_flyprobe_issue (tenant_code, file_version_id, issue_fingerprint),
                KEY idx_flyprobe_issue_status (tenant_code, severity, issue_code)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """
        )

    @staticmethod
    def _ensure_device_schema(cursor, table_name: str) -> None:
        table = _safe_table_name(table_name)
        columns = [
            "id CHAR(36) NOT NULL",
            "tenant_code VARCHAR(64) NOT NULL",
            "source_file_version_id CHAR(36) NOT NULL",
            "source_key CHAR(64) NOT NULL",
            "device_code VARCHAR(255) NOT NULL",
            "source_rel_path VARCHAR(500) NOT NULL",
            "source_file_name VARCHAR(255) NOT NULL",
            "source_sha256 CHAR(64) NOT NULL",
            "job_code_raw VARCHAR(255) NOT NULL",
            "source_mtime DATETIME(6) NOT NULL",
            "source_size_bytes BIGINT UNSIGNED NOT NULL",
            "pad_count BIGINT UNSIGNED NULL",
            "net_count BIGINT UNSIGNED NULL",
        ]
        columns.extend(f"job_extent_{index} BIGINT NULL" for index in range(1, 5))
        columns.extend(f"a_align_{index} BIGINT NULL" for index in range(1, 7))
        columns.append("reference_net BIGINT NULL")
        columns.extend(f"pads_side_{index} BIGINT UNSIGNED NULL" for index in range(1, 4))
        columns.extend(f"b_align_{index} BIGINT NULL" for index in range(1, 8))
        columns.extend(f"orientation_{index} TINYINT UNSIGNED NULL" for index in range(1, 5))
        columns.append("panel_obsolete_marker TINYINT UNSIGNED NULL")
        columns.extend(f"panel_layout_{index} BIGINT UNSIGNED NULL" for index in range(1, 6))
        columns.extend((
            "test_total BIGINT UNSIGNED NULL",
            "test_passed BIGINT UNSIGNED NULL",
            "test_failed BIGINT UNSIGNED NULL",
            "test_duration_raw VARCHAR(64) NULL",
            "test_duration_seconds BIGINT UNSIGNED NULL",
            "resist_test_mode BIGINT UNSIGNED NULL",
            "resist_param_1 DECIMAL(18,6) NULL",
            "resist_param_2 DECIMAL(18,6) NULL",
            "validation_status VARCHAR(16) NOT NULL",
            "validation_messages LONGTEXT NOT NULL",
            "created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6)",
            "updated_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6)",
            "PRIMARY KEY (id)",
            "UNIQUE KEY uq_flyprobe_source_key (tenant_code, source_key)",
            "UNIQUE KEY uq_flyprobe_file_version (tenant_code, source_file_version_id)",
            "KEY idx_flyprobe_status (tenant_code, validation_status, source_mtime)",
            "KEY idx_flyprobe_job (tenant_code, job_code_raw)",
        ))
        cursor.execute(
            f"CREATE TABLE IF NOT EXISTS {table} (\n                "
            + ",\n                ".join(columns)
            + "\n            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci"
        )

    def _upsert_file_version(self, cursor, record: ProbeFileRecord) -> Tuple[str, bool]:
        audit_table = _safe_table_name(FILE_VERSION_TABLE)
        cursor.execute(
            f"""
            SELECT id FROM {audit_table}
            WHERE tenant_code = %s AND source_key = %s
            """,
            (self.tenant_code, record.source_key),
        )
        existing = cursor.fetchone()
        if existing:
            version_id = str(existing[0])
            cursor.execute(
                f"""
                UPDATE {audit_table}
                SET source_mtime = %s, source_size_bytes = %s, parser_version = %s,
                    validation_status = %s, validation_messages = %s, raw_text = %s,
                    text_encoding = %s, is_current = 1, last_seen_at = CURRENT_TIMESTAMP(6)
                WHERE tenant_code = %s AND source_key = %s
                """,
                (
                    record.source_mtime, record.source_size_bytes, PARSER_VERSION,
                    record.validation_status, _validation_messages(record.parsed.issues),
                    record.parsed.raw_text, record.parsed.encoding,
                    self.tenant_code, record.source_key,
                ),
            )
            return version_id, False

        cursor.execute(
            f"""
            UPDATE {audit_table}
            SET is_current = 0, updated_at = CURRENT_TIMESTAMP(6)
            WHERE tenant_code = %s AND device_code = %s AND source_rel_path = %s AND is_current = 1
            """,
            (self.tenant_code, record.device_code, record.source_rel_path),
        )
        version_id = str(uuid.uuid4())
        cursor.execute(
            f"""
            INSERT INTO {audit_table} (
                id, tenant_code, device_code, source_rel_path, source_file_name, source_sha256,
                source_key, source_mtime, source_size_bytes, parser_version, validation_status,
                validation_messages, raw_text, text_encoding, is_current
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 1)
            """,
            (
                version_id, self.tenant_code, record.device_code, record.source_rel_path,
                record.source_file_name, record.source_hash, record.source_key, record.source_mtime,
                record.source_size_bytes, PARSER_VERSION, record.validation_status,
                _validation_messages(record.parsed.issues), record.parsed.raw_text, record.parsed.encoding,
            ),
        )
        return version_id, True

    def _upsert_issues(self, cursor, version_id: str, issues: Sequence[ValidationIssue]) -> int:
        if not issues:
            return 0
        table = _safe_table_name(SYNC_ERROR_TABLE)
        statement = f"""
            INSERT INTO {table} (
                id, tenant_code, file_version_id, issue_fingerprint, severity,
                issue_code, issue_field, message, raw_value
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                severity = VALUES(severity), issue_field = VALUES(issue_field),
                message = VALUES(message), raw_value = VALUES(raw_value),
                last_seen_at = CURRENT_TIMESTAMP(6)
        """
        rows = []
        for issue in issues:
            fingerprint = hashlib.sha256(
                "\0".join((issue.severity, issue.code, issue.field, issue.message, issue.raw_value)).encode("utf-8")
            ).hexdigest()
            rows.append(
                (
                    str(uuid.uuid4()), self.tenant_code, version_id, fingerprint, issue.severity,
                    issue.code, issue.field, issue.message, issue.raw_value,
                )
            )
        cursor.executemany(statement, rows)
        return len(rows)

    def _upsert_device_record(self, cursor, table_name: str, version_id: str, record: ProbeFileRecord) -> None:
        table = _safe_table_name(table_name)
        values = dict(record.parsed.values)
        columns = [
            "id", "tenant_code", "source_file_version_id", "source_key", "device_code",
            "source_rel_path", "source_file_name", "source_sha256", "job_code_raw",
            "source_mtime", "source_size_bytes", "pad_count", "net_count",
        ]
        columns.extend(f"job_extent_{index}" for index in range(1, 5))
        columns.extend(f"a_align_{index}" for index in range(1, 7))
        columns.append("reference_net")
        columns.extend(f"pads_side_{index}" for index in range(1, 4))
        columns.extend(f"b_align_{index}" for index in range(1, 8))
        columns.extend(f"orientation_{index}" for index in range(1, 5))
        columns.append("panel_obsolete_marker")
        columns.extend(f"panel_layout_{index}" for index in range(1, 6))
        columns.extend((
            "test_total", "test_passed", "test_failed", "test_duration_raw", "test_duration_seconds",
            "resist_test_mode", "resist_param_1", "resist_param_2", "validation_status", "validation_messages",
        ))
        placeholders = ", ".join(["%s"] * len(columns))
        updates = ", ".join(
            f"`{column}` = VALUES(`{column}`)" for column in columns if column not in {"id", "tenant_code", "source_key"}
        )
        statement = f"""
            INSERT INTO {table} ({", ".join(f"`{column}`" for column in columns)})
            VALUES ({placeholders})
            ON DUPLICATE KEY UPDATE {updates}, updated_at = CURRENT_TIMESTAMP(6)
        """
        parameters: List[Any] = [
            str(uuid.uuid4()), self.tenant_code, version_id, record.source_key, record.device_code,
            record.source_rel_path, record.source_file_name, record.source_hash, record.source_path.stem,
            record.source_mtime, record.source_size_bytes,
        ]
        parameters.extend(values.get(column) for column in columns[11:-2])
        parameters.extend((record.validation_status, _validation_messages(record.parsed.issues)))
        cursor.execute(statement, tuple(parameters))

    @staticmethod
    def _execute_many(cursor, statement: str, rows: Sequence[Tuple[Any, ...]], batch_size: int = 250) -> None:
        """Keep remote MySQL round trips bounded for a large share directory."""
        for offset in range(0, len(rows), batch_size):
            cursor.executemany(statement, rows[offset:offset + batch_size])

    def _sync_file_versions(self, cursor, records: Sequence[ProbeFileRecord]) -> Tuple[Dict[str, str], int, int]:
        audit_table = _safe_table_name(FILE_VERSION_TABLE)
        cursor.execute(
            f"SELECT source_key, id FROM {audit_table} WHERE tenant_code = %s",
            (self.tenant_code,),
        )
        existing_by_key = {str(row[0]): str(row[1]) for row in cursor.fetchall()}
        cursor.execute(
            f"""
            SELECT device_code, source_rel_path, source_key
            FROM {audit_table}
            WHERE tenant_code = %s AND is_current = 1
            """,
            (self.tenant_code,),
        )
        current_by_path = {(str(row[0]), str(row[1])): str(row[2]) for row in cursor.fetchall()}

        version_ids: Dict[str, str] = {}
        new_rows: List[Tuple[Any, ...]] = []
        existing_rows: List[Tuple[Any, ...]] = []
        deactivations: List[Tuple[Any, ...]] = []
        for record in records:
            current_key = current_by_path.get((record.device_code, record.source_rel_path))
            if current_key is not None and current_key != record.source_key:
                deactivations.append(
                    (self.tenant_code, record.device_code, record.source_rel_path, record.source_key)
                )
            version_id = existing_by_key.get(record.source_key)
            if version_id is None:
                version_id = str(uuid.uuid4())
                new_rows.append(
                    (
                        version_id, self.tenant_code, record.device_code, record.source_rel_path,
                        record.source_file_name, record.source_hash, record.source_key, record.source_mtime,
                        record.source_size_bytes, PARSER_VERSION, record.validation_status,
                        _validation_messages(record.parsed.issues), record.parsed.raw_text, record.parsed.encoding,
                    )
                )
            else:
                existing_rows.append(
                    (
                        record.source_mtime, record.source_size_bytes, PARSER_VERSION,
                        record.validation_status, _validation_messages(record.parsed.issues),
                        record.parsed.raw_text, record.parsed.encoding, self.tenant_code, record.source_key,
                    )
                )
            version_ids[record.source_key] = version_id

        if deactivations:
            self._execute_many(
                cursor,
                f"""
                UPDATE {audit_table}
                SET is_current = 0, updated_at = CURRENT_TIMESTAMP(6)
                WHERE tenant_code = %s AND device_code = %s AND source_rel_path = %s
                  AND source_key <> %s AND is_current = 1
                """,
                deactivations,
            )
        if new_rows:
            self._execute_many(
                cursor,
                f"""
                INSERT INTO {audit_table} (
                    id, tenant_code, device_code, source_rel_path, source_file_name, source_sha256,
                    source_key, source_mtime, source_size_bytes, parser_version, validation_status,
                    validation_messages, raw_text, text_encoding, is_current
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 1)
                """,
                new_rows,
            )
        if existing_rows:
            self._execute_many(
                cursor,
                f"""
                UPDATE {audit_table}
                SET source_mtime = %s, source_size_bytes = %s, parser_version = %s,
                    validation_status = %s, validation_messages = %s, raw_text = %s,
                    text_encoding = %s, is_current = 1, last_seen_at = CURRENT_TIMESTAMP(6)
                WHERE tenant_code = %s AND source_key = %s
                """,
                existing_rows,
            )
        return version_ids, len(new_rows), len(existing_rows)

    def _upsert_issue_batch(
        self, cursor, records: Sequence[ProbeFileRecord], version_ids: Mapping[str, str],
    ) -> int:
        rows: List[Tuple[Any, ...]] = []
        for record in records:
            version_id = version_ids[record.source_key]
            for issue in record.parsed.issues:
                fingerprint = hashlib.sha256(
                    "\0".join((issue.severity, issue.code, issue.field, issue.message, issue.raw_value)).encode("utf-8")
                ).hexdigest()
                rows.append(
                    (
                        str(uuid.uuid4()), self.tenant_code, version_id, fingerprint, issue.severity,
                        issue.code, issue.field, issue.message, issue.raw_value,
                    )
                )
        if not rows:
            return 0
        table = _safe_table_name(SYNC_ERROR_TABLE)
        self._execute_many(
            cursor,
            f"""
            INSERT INTO {table} (
                id, tenant_code, file_version_id, issue_fingerprint, severity,
                issue_code, issue_field, message, raw_value
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                severity = VALUES(severity), issue_field = VALUES(issue_field),
                message = VALUES(message), raw_value = VALUES(raw_value),
                last_seen_at = CURRENT_TIMESTAMP(6)
            """,
            rows,
        )
        return len(rows)

    @staticmethod
    def _device_columns() -> List[str]:
        columns = [
            "id", "tenant_code", "source_file_version_id", "source_key", "device_code",
            "source_rel_path", "source_file_name", "source_sha256", "job_code_raw",
            "source_mtime", "source_size_bytes", "pad_count", "net_count",
        ]
        columns.extend(f"job_extent_{index}" for index in range(1, 5))
        columns.extend(f"a_align_{index}" for index in range(1, 7))
        columns.append("reference_net")
        columns.extend(f"pads_side_{index}" for index in range(1, 4))
        columns.extend(f"b_align_{index}" for index in range(1, 8))
        columns.extend(f"orientation_{index}" for index in range(1, 5))
        columns.append("panel_obsolete_marker")
        columns.extend(f"panel_layout_{index}" for index in range(1, 6))
        columns.extend((
            "test_total", "test_passed", "test_failed", "test_duration_raw", "test_duration_seconds",
            "resist_test_mode", "resist_param_1", "resist_param_2", "validation_status", "validation_messages",
        ))
        return columns

    def _upsert_device_batches(
        self,
        cursor,
        records: Sequence[ProbeFileRecord],
        version_ids: Mapping[str, str],
        include_invalid: bool,
    ) -> Tuple[int, int]:
        rows_by_table: Dict[str, List[Tuple[Any, ...]]] = {}
        skipped_invalid = 0
        columns = self._device_columns()
        for record in records:
            if record.validation_status == "INVALID" and not include_invalid:
                skipped_invalid += 1
                continue
            table_name = DEVICE_TABLES.get(record.device_code)
            if table_name is None:
                skipped_invalid += 1
                continue
            values = dict(record.parsed.values)
            row: List[Any] = [
                str(uuid.uuid4()), self.tenant_code, version_ids[record.source_key], record.source_key,
                record.device_code, record.source_rel_path, record.source_file_name, record.source_hash,
                record.source_path.stem, record.source_mtime, record.source_size_bytes,
            ]
            row.extend(values.get(column) for column in columns[11:-2])
            row.extend((record.validation_status, _validation_messages(record.parsed.issues)))
            rows_by_table.setdefault(table_name, []).append(tuple(row))

        placeholders = ", ".join(["%s"] * len(columns))
        updates = ", ".join(
            f"`{column}` = VALUES(`{column}`)" for column in columns if column not in {"id", "tenant_code", "source_key"}
        )
        imported = 0
        for table_name, rows in rows_by_table.items():
            table = _safe_table_name(table_name)
            self._execute_many(
                cursor,
                f"""
                INSERT INTO {table} ({", ".join(f"`{column}`" for column in columns)})
                VALUES ({placeholders})
                ON DUPLICATE KEY UPDATE {updates}, updated_at = CURRENT_TIMESTAMP(6)
                """,
                rows,
            )
            imported += len(rows)
        return imported, skipped_invalid

    def synchronize(self, scan: ScanResult, include_invalid: bool = False) -> SyncResult:
        connection = self._connect()
        new_versions = 0
        existing_versions = 0
        imported_files = 0
        skipped_invalid = 0
        issue_rows = 0
        try:
            with connection.cursor() as cursor:
                self._ensure_audit_schema(cursor)
                for table_name in sorted(set(DEVICE_TABLES.values())):
                    self._ensure_device_schema(cursor, table_name)
                version_ids, new_versions, existing_versions = self._sync_file_versions(cursor, scan.records)
                issue_rows = self._upsert_issue_batch(cursor, scan.records, version_ids)
                imported_files, skipped_invalid = self._upsert_device_batches(
                    cursor, scan.records, version_ids, include_invalid,
                )
            connection.commit()
        except MySQLError as exc:
            connection.rollback()
            raise FlyingProbeSyncError(f"QMS MySQL 飞针数据写入失败，事务已回滚：{exc}") from exc
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

        summary = scan.summary()
        return SyncResult(
            scanned_files=len(scan.records),
            valid_files=int(summary["valid_files"]),
            warning_files=int(summary["warning_files"]),
            invalid_files=int(summary["invalid_files"]),
            ignored_files=int(summary["ignored_files"]),
            imported_files=imported_files,
            new_versions=new_versions,
            existing_versions=existing_versions,
            skipped_invalid_files=skipped_invalid,
            issue_rows_upserted=issue_rows,
            dry_run=False,
        )


def load_database_config(config_path: Path) -> Dict[str, Any]:
    path = Path(config_path)
    try:
        raw = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as exc:
        raise FlyingProbeSyncError(f"无法读取 QMS 数据库配置：{path}") from exc
    if not isinstance(raw, dict):
        raise FlyingProbeSyncError("QMS 数据库配置必须是 JSON 对象。")
    return dict(raw)


def validate_and_optionally_sync(
    source_directory: Path,
    database_config: Mapping[str, Any],
    dry_run: bool,
    max_duration_hours: int = DEFAULT_MAX_DURATION_HOURS,
    include_invalid: bool = False,
    scan_workers: int = 12,
) -> Tuple[ScanResult, SyncResult]:
    tenant_code = str(database_config.get("tenant_code", "")).strip()
    scan = scan_source_directory(source_directory, tenant_code, max_duration_hours, scan_workers=scan_workers)
    summary = scan.summary()
    if dry_run:
        return scan, SyncResult(
            scanned_files=len(scan.records),
            valid_files=int(summary["valid_files"]),
            warning_files=int(summary["warning_files"]),
            invalid_files=int(summary["invalid_files"]),
            ignored_files=int(summary["ignored_files"]),
            imported_files=0,
            new_versions=0,
            existing_versions=0,
            skipped_invalid_files=int(summary["invalid_files"]),
            issue_rows_upserted=0,
            dry_run=True,
        )
    database = FlyingProbeDatabase(database_config)
    return scan, database.synchronize(scan, include_invalid=include_invalid)


def _result_document(scan: ScanResult, result: SyncResult) -> Dict[str, Any]:
    return {"validation": scan.summary(), "sync": asdict(result)}


def parse_arguments(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=APP_NAME)
    parser.add_argument("--source-directory", type=Path, default=Path(DEFAULT_SOURCE_DIRECTORY), help="飞针 TXT 共享目录")
    parser.add_argument("--database-config", type=Path, required=True, help="现有 QMS MySQL JSON 配置文件")
    parser.add_argument("--dry-run", action="store_true", help="只校验格式，不创建或写入数据库表")
    parser.add_argument("--include-invalid", action="store_true", help="将格式错误文件也保存到设备表，并保持 INVALID 状态")
    parser.add_argument("--max-duration-hours", type=int, default=DEFAULT_MAX_DURATION_HOURS, help="允许的最大测试时长（小时）")
    parser.add_argument("--scan-workers", type=int, default=12, help="读取共享目录的并发数")
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    arguments = parse_arguments(argv)
    try:
        config = load_database_config(arguments.database_config)
        scan, result = validate_and_optionally_sync(
            arguments.source_directory,
            config,
            dry_run=arguments.dry_run,
            max_duration_hours=arguments.max_duration_hours,
            include_invalid=arguments.include_invalid,
            scan_workers=arguments.scan_workers,
        )
        print(json.dumps(_result_document(scan, result), ensure_ascii=False, indent=2, default=str))
        return 0
    except FlyingProbeSyncError as exc:
        print(f"同步失败：{exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
