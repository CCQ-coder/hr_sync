"""ERP BI Excel -> QMS production-instruction synchronizer.

The program is deliberately dependency-light so it can be packaged as a single
Windows executable.  It talks to QMS through the gateway API, therefore the
QMS database keeps its tenant isolation and business validation rules.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import queue
import re
import sys
import threading
import traceback
import urllib.error
import urllib.request
import uuid
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from decimal import Decimal, InvalidOperation
from pathlib import Path
from types import MappingProxyType
from typing import Any, Callable, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

import tkinter as tk
from tkinter import filedialog, messagebox, ttk

import xlrd
from openpyxl import load_workbook
import pymysql
from pymysql import MySQLError


APP_NAME = "QMS ERP 数据同步工具"
CONFIG_FILE_NAME = "qms_erp_sync_config.json"
STATE_FILE_NAME = "qms_erp_sync_state.json"
BASELINE_REPLAY_STATE_KEY = "baseline-replay-pending"
SOURCE_IDENTITY_VERSION_STATE_KEY = "source-identity-version"
CUSTOMER_ORDER_RECONCILE_STATE_KEY = "customer-order-latest-version"
CUSTOMER_ORDER_RECONCILE_VERSION = "2"
LOG_DIR_NAME = "logs"
SOURCE_KEY_PREFIX = "ERP-EXCEL:"
API_PATH = "/api/v1/integrations/work-orders"
SNAPSHOT_API_PATH = "/api/v1/integrations/work-orders/snapshot"
EXCEL_SUFFIXES = (".xls", ".xlsx")
DATABASE_MODE_LABEL = "数据库直连（默认，不需要 Token）"
API_MODE_LABEL = "QMS 接口（需要网关 Token）"
AUTO_SYNC_DEFAULT_INTERVAL_MINUTES = 5
AUTO_SYNC_MIN_INTERVAL_MINUTES = 1
AUTO_SYNC_MAX_INTERVAL_MINUTES = 1440
SOURCE_TABLE_POLICY = "qms_erp_business_tenant_isolation"
# Fixed, business-readable destination tables.  Source file and sheet remain
# columns in every table, so files sharing a business domain stay traceable
# without creating qms_erp_data_<file>_<sheet>_<hash> tables.
BUSINESS_SOURCE_TABLE_BY_FILE: Sequence[Tuple[str, str]] = (
    ("客户订单资料", "qms_customer_order"),
    ("客户料号资料", "qms_customer_part"),
    ("工程资料资料", "qms_engineering_data"),
    ("采购订单资料", "qms_purchase_order"),
    ("原料资料明细", "qms_material"),
    ("原料入库单资料", "qms_material_receipt"),
    ("原料出库单资料", "qms_material_issue"),
    ("补料资料", "qms_material_issue"),
    ("成品入库单资料", "qms_finished_goods_receipt"),
    ("送货单资料", "qms_delivery_note"),
    ("各工段出数汇总资料", "qms_process_output_summary"),
)
UNCLASSIFIED_SOURCE_TABLE = "qms_erp_unclassified"
BUSINESS_SOURCE_TABLES = frozenset(
    [destination for _, destination in BUSINESS_SOURCE_TABLE_BY_FILE] + [UNCLASSIFIED_SOURCE_TABLE]
)

# Use ERP identifiers rather than the export's file, row, headers or mutable amounts.
# Each inner tuple is an alternative identity, in preference order.
ERP_ROW_IDENTITIES: Mapping[str, Tuple[Tuple[str, ...], ...]] = {
    "qms_customer_order": (("erp_order_no", "erp_internal_product_no"), ("erp_order_no", "erp_customer_part_no"), ("erp_order_no", "erp_material_code"), ("erp_order_no",)),
    "qms_customer_part": (("erp_internal_product_no",), ("erp_customer_code", "erp_customer_part_no")),
    "qms_engineering_data": (("erp_mi_id",), ("erp_internal_product_no", "erp_version"), ("erp_internal_product_no",)),
    "qms_purchase_order": (("erp_purchase_order_no", "erp_material_no"), ("erp_purchase_order_no",)),
    "qms_material": (("erp_material_no",),),
    "qms_material_receipt": (("erp_receipt_no", "erp_receipt_detail_no"), ("erp_receipt_detail_no",), ("erp_receipt_no", "erp_material_no"), ("erp_receipt_no",)),
    "qms_material_issue": (("erp_material_issue_detail_id",), ("erp_material_issue_id", "erp_material_no_id"), ("erp_material_issue_no", "erp_material_no_source_3b3dc2fa70"), ("erp_material_issue_no", "erp_material_no_source_3d14d54480"), ("erp_material_issue_no",)),
    "qms_finished_goods_receipt": (("erp_combined_panel_detail_id",), ("erp_receipt_no", "erp_carton_no", "erp_internal_product_no"), ("erp_receipt_no", "erp_internal_product_no"), ("erp_receipt_no",)),
    "qms_delivery_note": (("erp_delivery_note_no", "erp_internal_product_no"), ("erp_delivery_note_no",)),
    "qms_work_order": (("erp_production_order_no",),),
}


def erp_row_identity(table: str, values: Mapping[str, Optional[str]]) -> str:
    for columns in ERP_ROW_IDENTITIES.get(table, ()):
        if all(values.get(column) for column in columns):
            return json.dumps([(column, values[column]) for column in columns], ensure_ascii=False)
    # shortcut: sources without reviewed row IDs use canonical field content; add ERP row IDs when supplied.
    return json.dumps(sorted(values.items()), ensure_ascii=False, separators=(",", ":"))


DEFAULT_CONFIG: Dict[str, Any] = {
    # source_directory is retained as a read-only compatibility alias for
    # configurations created by older releases.
    "source_directory": str(Path(__file__).resolve().parent / "data" / "BI数据源"),
    "initialization_directory": str(Path(__file__).resolve().parent / "data" / "BI数据源"),
    "incremental_directory": "",
    "skip_initialization": False,
    "source_file_keyword": "生产指示资料",
    "sync_mode": "database",
    "database_host": "127.0.0.1",
    "database_port": "3306",
    "database_name": "qms",
    "database_username": "qms",
    "database_password": "qms",
    "qms_base_url": "http://localhost:8080",
    "tenant_code": "customer-b",
    "gateway_token": "",
    "deactivate_missing": False,
    "request_timeout_seconds": 30,
    "auto_sync_enabled": False,
    "auto_sync_interval_minutes": AUTO_SYNC_DEFAULT_INTERVAL_MINUTES,
    "last_source_fingerprint": "",
}


WORK_ORDER_DB_FIELDS: Sequence[Tuple[str, str]] = (
    ("product_code", "productCode"),
    ("product_name", "productName"),
    ("specification", "specification"),
    ("current_process_code", "currentProcessCode"),
    ("current_process_name", "currentProcessName"),
    ("planned_quantity", "plannedQuantity"),
    ("customer_code", "customerCode"),
    ("internal_product_no", "internalProductNo"),
    ("customer_part_no", "customerPartNo"),
    ("process_technology", "processTechnology"),
    ("material", "material"),
    ("board_thickness", "boardThickness"),
    ("copper_thickness", "copperThickness"),
    ("warehouse_status", "warehouseStatus"),
    ("material_input_date", "materialInputDate"),
    ("pcs_length", "pcsLength"),
    ("pcs_width", "pcsWidth"),
    ("material_no", "materialNo"),
    ("material_name", "materialName"),
    ("material_specification", "materialSpecification"),
    ("standard_material_consumption", "standardMaterialConsumption"),
    ("material_input_quantity", "materialInputQuantity"),
    ("cumulative_warehouse_quantity", "cumulativeWarehouseQuantity"),
    ("cumulative_scrap_quantity", "cumulativeScrapQuantity"),
    ("cumulative_defect_quantity", "cumulativeDefectQuantity"),
    ("required_delivery_date", "requiredDeliveryDate"),
    ("production_notice_no", "productionNoticeNo"),
    ("input_date", "inputDate"),
    ("single_pcs_area", "singlePcsArea"),
    ("pnl_length", "pnlLength"),
    ("pnl_width", "pnlWidth"),
    ("a_board_length", "aBoardLength"),
    ("a_board_width", "aBoardWidth"),
    ("b_board_length", "bBoardLength"),
    ("b_board_width", "bBoardWidth"),
    ("forming_method", "formingMethod"),
    ("layer_count", "layerCount"),
    ("production_notice_quantity", "productionNoticeQuantity"),
    ("production_notice_order_quantity", "productionNoticeOrderQuantity"),
    ("customer_order", "customerOrder"),
    ("customer_order_no", "customerOrderNo"),
    ("customer_order_quantity", "customerOrderQuantity"),
    ("material_area", "materialArea"),
    ("production_notice_area", "productionNoticeArea"),
    ("customer_order_area", "customerOrderArea"),
    ("unreceived_quantity", "unreceivedQuantity"),
    ("last_warehouse_date", "lastWarehouseDate"),
    ("total_panel_quantity", "totalPanelQuantity"),
    ("a_board_panel_quantity", "aBoardPanelQuantity"),
    ("b_board_panel_quantity", "bBoardPanelQuantity"),
    ("panelization_no", "panelizationNo"),
    ("estimated_yield_rate", "estimatedYieldRate"),
    ("planned_material_issue_quantity", "plannedMaterialIssueQuantity"),
    ("priority", "priority"),
    ("process_route_version", "processRouteVersion"),
    ("mi_version", "miVersion"),
)


# QMS field -> ERP production-instruction header.  Headers are normalized, so
# line breaks in Excel headings (for example “订单数量\n<生产通知单>”) are safe.
FIELD_MAP: Dict[str, str] = {
    "workOrderNo": "生产指令号",
    "productCode": "厂内编号",
    "productName": "客户料号",
    "currentProcessCode": "工艺",
    "currentProcessName": "工艺",
    "plannedQuantity": "投料数量",
    "batchNo": "管制卡号",
    "customerCode": "客户编号",
    "internalProductNo": "厂内编号",
    "customerPartNo": "客户料号",
    "processTechnology": "工艺",
    "material": "材质",
    "boardThickness": "板厚",
    "copperThickness": "铜箔",
    "materialInputDate": "投料日期",
    "pcsLength": "PCS长",
    "pcsWidth": "PCS宽",
    "materialNo": "板材编号",
    "materialName": "板材名称",
    "materialSpecification": "板材规格",
    "standardMaterialConsumption": "标准用量",
    "materialInputQuantity": "投料数量",
    "cumulativeWarehouseQuantity": "累计入库",
    "cumulativeScrapQuantity": "累计报废",
    "cumulativeDefectQuantity": "累计不良",
    "requiredDeliveryDate": "要求交期",
    "productionNoticeNo": "生产通知单号",
    "inputDate": "输入日期",
    "singlePcsArea": "单PCS面积",
    "pnlLength": "PNL长",
    "pnlWidth": "PNL宽",
    "aBoardLength": "A板长",
    "aBoardWidth": "A板宽",
    "bBoardLength": "B板长",
    "bBoardWidth": "B板宽",
    "formingMethod": "成型方式",
    "layerCount": "层数",
    "productionNoticeQuantity": "生产通知单数量",
    "productionNoticeOrderQuantity": "订单数量<生产通知单>",
    "customerOrder": "客户订单",
    "customerOrderNo": "订单编号",
    "customerOrderQuantity": "订单数量",
    "materialArea": "板材面积",
    "productionNoticeArea": "生产通知单面积<成品>",
    "customerOrderArea": "客户订单面积<成品>",
    "aBoardPanelQuantity": "A板总PNL",
    "bBoardPanelQuantity": "B板总PNL",
    "estimatedYieldRate": "成品利用率",
    "plannedMaterialIssueQuantity": "计划领料",
    "unreceivedQuantity": "未入库数量",
    "lastWarehouseDate": "最后入库日期",
}

DATE_FIELDS = {
    "materialInputDate", "requiredDeliveryDate", "inputDate", "lastWarehouseDate",
}
INTEGER_FIELDS = {
    "plannedQuantity", "materialInputQuantity", "cumulativeWarehouseQuantity",
    "cumulativeScrapQuantity", "cumulativeDefectQuantity", "productionNoticeQuantity",
    "productionNoticeOrderQuantity", "customerOrderQuantity", "unreceivedQuantity",
    "aBoardPanelQuantity", "bBoardPanelQuantity",
}
DECIMAL_FIELDS = {
    "pcsLength", "pcsWidth", "standardMaterialConsumption", "singlePcsArea",
    "pnlLength", "pnlWidth", "aBoardLength", "aBoardWidth", "bBoardLength",
    "bBoardWidth", "materialArea", "productionNoticeArea", "customerOrderArea",
    "estimatedYieldRate", "plannedMaterialIssueQuantity",
}


class SyncError(RuntimeError):
    """A problem that is useful to show directly to a business user."""


@dataclass
class SyncSummary:
    source_file: str
    rows_read: int
    added: int
    updated: int
    unchanged: int
    deactivated: int
    dry_run: bool
    source_files: int = 1
    raw_records: int = 0
    work_orders: int = 0
    source_tables: int = 0
    raw_written: int = 0
    work_orders_written: int = 0


@dataclass(frozen=True)
class RawSourceRecord:
    """One non-empty source row with every Excel column in a real DB column."""

    source_file: str
    sheet_name: str
    source_row_no: int
    business_key: str
    source_key: str
    row_hash: str
    field_values: Mapping[str, Optional[str]]
    source_table: Optional[str]
    field_definitions: Mapping[str, ErpFieldDefinition]


@dataclass
class SourceScanStats:
    files_scanned: int = 0
    sheets_scanned: int = 0
    raw_records: int = 0
    work_order_records: int = 0


@dataclass(frozen=True)
class SourceScanGroup:
    """A set of changed Excel files sharing one configured source root."""

    role: str
    directory: Path
    files: Tuple[Path, ...]


def app_directory() -> Path:
    """Use the EXE folder when packaged; fall back to AppData if it is read-only."""
    if getattr(sys, "frozen", False):
        candidate = Path(sys.executable).resolve().parent
    else:
        candidate = Path(__file__).resolve().parent
    try:
        candidate.mkdir(parents=True, exist_ok=True)
        probe = candidate / ".qms_erp_sync_write_probe"
        probe.write_text("ok", encoding="utf-8")
        probe.unlink()
        return candidate
    except OSError:
        fallback = Path(os.environ.get("APPDATA", str(Path.home()))) / "QmsErpSync"
        fallback.mkdir(parents=True, exist_ok=True)
        return fallback


def config_path() -> Path:
    return app_directory() / CONFIG_FILE_NAME


def state_path() -> Path:
    return app_directory() / STATE_FILE_NAME


def normalize_header(value: Any) -> str:
    return re.sub(r"\s+", "", as_text(value))


def is_empty(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return not value.strip() or value.strip().lower() in {"none", "null", "nan", "n/a"}
    return False


def as_text(value: Any) -> str:
    if is_empty(value):
        return ""
    if isinstance(value, bool):
        return "是" if value else "否"
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    if isinstance(value, Decimal):
        return format(value.normalize(), "f")
    return str(value).strip()


def excel_header_identity(value: Any) -> str:
    """Preserve nonblank Excel strings exactly; only whitespace-only is blank.

    Header identity must not inherit business-cell trimming or textual null
    aliases. Non-string values keep the existing numeric/bool canonicalization.
    """
    if isinstance(value, str):
        return value if value.strip() else ""
    return as_text(value)


def as_decimal(value: Any) -> Optional[str]:
    if is_empty(value):
        return None
    if isinstance(value, (datetime, date)):
        return None
    try:
        decimal_value = Decimal(str(value).strip())
    except (InvalidOperation, ValueError):
        return None
    if not decimal_value.is_finite():
        return None
    return format(decimal_value.normalize(), "f")


def as_integer(value: Any) -> Optional[int]:
    decimal_value = as_decimal(value)
    if decimal_value is None:
        return None
    try:
        return int(Decimal(decimal_value).quantize(Decimal("1")))
    except (InvalidOperation, ValueError):
        return None


def excel_date(value: Any, datemode: int = 0) -> Optional[str]:
    if is_empty(value):
        return None
    if isinstance(value, datetime):
        return value.date().isoformat()
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, (int, float)):
        try:
            return xlrd.xldate_as_datetime(float(value), datemode).date().isoformat()
        except (ValueError, OverflowError):
            return None
    text = as_text(value)
    for pattern in ("%Y-%m-%d", "%Y/%m/%d", "%Y.%m.%d", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(text, pattern).date().isoformat()
        except ValueError:
            pass
    return None


def truthy(value: Any) -> bool:
    text = as_text(value).upper()
    return text in {"1", "Y", "YES", "TRUE", "是", "加急", "紧急", "URGENT"}


def warehouse_status(value: Any) -> str:
    text = as_text(value)
    if "结批" in text or "关闭" in text or "完成" in text:
        return "CLOSED"
    if "入库" in text or "已入" in text:
        return "RECEIVED"
    return "PENDING"


def normalize_auto_sync_interval(value: Any) -> int:
    """Return a safe, user-configurable polling interval in minutes."""
    try:
        interval = int(str(value).strip())
    except (TypeError, ValueError):
        return AUTO_SYNC_DEFAULT_INTERVAL_MINUTES
    return max(AUTO_SYNC_MIN_INTERVAL_MINUTES, min(AUTO_SYNC_MAX_INTERVAL_MINUTES, interval))


def build_desktop_config(
    base_config: Mapping[str, Any], *, initialization_directory: str,
    incremental_directory: str, skip_initialization: bool,
    auto_sync_enabled: bool, auto_sync_interval_minutes: Any,
) -> Dict[str, Any]:
    """Merge visible desktop options without exposing or losing DB credentials."""
    config = dict(DEFAULT_CONFIG)
    config.update(dict(base_config))
    previous_incremental = str(config.get("incremental_directory", "")).strip()
    next_incremental = incremental_directory.strip()
    config.update(
        {
            "source_directory": initialization_directory.strip(),
            "initialization_directory": initialization_directory.strip(),
            "incremental_directory": next_incremental,
            "skip_initialization": bool(skip_initialization),
            "source_file_keyword": "生产指示资料",
            "sync_mode": "database",
            # This desktop tool no longer provides deletion synchronization.
            # Keep historic config keys harmless for command-line compatibility.
            "deactivate_missing": False,
            "auto_sync_enabled": bool(auto_sync_enabled),
            "auto_sync_interval_minutes": normalize_auto_sync_interval(auto_sync_interval_minutes),
        }
    )
    if Path(previous_incremental) != Path(next_incremental):
        config["last_source_fingerprint"] = ""
    return config


def load_config() -> Dict[str, Any]:
    config = dict(DEFAULT_CONFIG)
    path = config_path()
    if path.exists():
        try:
            saved = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(saved, dict):
                config.update(saved)
                legacy_directory = str(saved.get("source_directory", "")).strip()
                if "initialization_directory" not in saved and legacy_directory:
                    config["initialization_directory"] = legacy_directory
                if "incremental_directory" not in saved:
                    config["incremental_directory"] = ""
                # Existing installations stored the former PostgreSQL default.
                # A retained 5432 value is not a valid MySQL default, so migrate
                # it once while preserving any user-specified MySQL port.
                if str(saved.get("database_port", "")).strip() == "5432":
                    config["database_port"] = DEFAULT_CONFIG["database_port"]
        except (OSError, json.JSONDecodeError) as exc:
            raise SyncError(f"配置文件无法读取：{path}\n{exc}") from exc
    # In a one-file PyInstaller build __file__ points to its temporary unpack
    # directory. A first-run source folder must instead sit beside the EXE (or
    # one level above it when the EXE is kept in a conventional dist folder).
    if getattr(sys, "frozen", False) and not path.exists():
        executable_directory = app_directory()
        nearby = executable_directory / "data" / "BI数据源"
        parent_nearby = executable_directory.parent / "data" / "BI数据源"
        initial_directory = str(nearby if nearby.is_dir() or not parent_nearby.is_dir() else parent_nearby)
        config["source_directory"] = initial_directory
        config["initialization_directory"] = initial_directory
    # Delete synchronization was removed from the desktop workflow.  Old
    # configurations may retain this field, but it must never activate it.
    config["deactivate_missing"] = False
    config["skip_initialization"] = bool(config.get("skip_initialization", False))
    config["source_directory"] = str(
        config.get("initialization_directory") or config.get("source_directory") or ""
    )
    config["auto_sync_enabled"] = bool(config.get("auto_sync_enabled", False))
    config["auto_sync_interval_minutes"] = normalize_auto_sync_interval(
        config.get("auto_sync_interval_minutes", AUTO_SYNC_DEFAULT_INTERVAL_MINUTES)
    )
    return config


def save_config(config: Mapping[str, Any]) -> None:
    target = config_path()
    temporary = target.with_suffix(".tmp")
    temporary.write_text(json.dumps(dict(config), ensure_ascii=False, indent=2), encoding="utf-8")
    temporary.replace(target)


def load_state() -> Dict[str, str]:
    target = state_path()
    records: Dict[str, str] = {}
    if target.exists():
        try:
            document = json.loads(target.read_text(encoding="utf-8"))
            values = document.get("records", {})
            if isinstance(values, dict):
                records.update(values)
        except (OSError, json.JSONDecodeError):
            # A corrupt local cursor must never result in a destructive operation.
            pass
    progress = progress_directory()
    if progress.is_dir():
        for entry in sorted(progress.glob("*.json"), key=lambda path: path.stat().st_mtime_ns):
            try:
                document = json.loads(entry.read_text(encoding="utf-8"))
                values = document.get("records", {})
                if isinstance(values, dict):
                    records.update(values)
            except (OSError, json.JSONDecodeError):
                # A damaged progress entry is replayed from the source file.
                continue
    return records


def save_state(records: Mapping[str, str]) -> None:
    target = state_path()
    temporary = target.with_suffix(".tmp")
    document = {"version": 1, "records": dict(records), "saved_at": datetime.now().isoformat(timespec="seconds")}
    temporary.write_text(json.dumps(document, ensure_ascii=False, indent=2), encoding="utf-8")
    temporary.replace(target)


def progress_directory() -> Path:
    """Keep completed-file deltas separate until the full state is compacted."""
    target = state_path()
    return target.with_name(f"{target.stem}_progress")


def save_file_progress(file_key: str, records: Mapping[str, str]) -> None:
    """Persist one committed file without rewriting the entire row-hash cache."""
    directory = progress_directory()
    directory.mkdir(parents=True, exist_ok=True)
    name = hashlib.sha256(file_key.encode("utf-8")).hexdigest()
    target = directory / f"{name}.json"
    temporary = directory / f"{name}.tmp"
    document = {"file_key": file_key, "records": dict(records)}
    with temporary.open("w", encoding="utf-8") as stream:
        json.dump(document, stream, ensure_ascii=False, separators=(",", ":"))
        stream.flush()
        os.fsync(stream.fileno())
    temporary.replace(target)


def clear_file_progress() -> None:
    directory = progress_directory()
    if not directory.is_dir():
        return
    for entry in directory.iterdir():
        if entry.is_file() and entry.suffix in {".json", ".tmp"}:
            entry.unlink()
    try:
        directory.rmdir()
    except OSError:
        pass


def log_line(message: str) -> None:
    directory = app_directory() / LOG_DIR_NAME
    directory.mkdir(parents=True, exist_ok=True)
    target = directory / f"sync-{date.today().isoformat()}.log"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with target.open("a", encoding="utf-8") as stream:
        stream.write(f"[{timestamp}] {message}\n")


def candidate_files(source_directory: Path) -> List[Path]:
    if not source_directory.exists() or not source_directory.is_dir():
        raise SyncError(f"数据源目录不存在：{source_directory}")
    return sorted(
        (path for path in source_directory.rglob("*") if path.is_file() and path.name.lower().endswith(EXCEL_SUFFIXES)),
        key=lambda item: source_path_sort_key(source_directory, item),
    )


def source_path_sort_key(source_directory: Path, path: Path) -> Tuple[Any, ...]:
    """Sort YYYY-M-D daily folders chronologically even without zero padding."""
    relative = path.relative_to(source_directory)
    for index, part in enumerate(relative.parts[:-1]):
        match = re.fullmatch(r"(\d{4})-(\d{1,2})-(\d{1,2})", part)
        if match:
            try:
                folder_date = date(*(int(value) for value in match.groups()))
            except ValueError:
                break
            remainder = "/".join(relative.parts[index + 1:]).casefold()
            return (0, folder_date.toordinal(), remainder)
    return (1, 0, relative.as_posix().casefold())


def configured_source_directories(config: Mapping[str, Any]) -> Tuple[str, str, bool]:
    """Return initialization/incremental roots with legacy-config support."""
    legacy = str(config.get("source_directory", "")).strip()
    initialization = str(config.get("initialization_directory", legacy)).strip()
    incremental = str(config.get("incremental_directory", "")).strip()
    return initialization, incremental, bool(config.get("skip_initialization", False))


def source_file_checkpoint(path: Path) -> str:
    """Content checkpoint that detects same-name, same-size daily overwrites."""
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return f"sha256:{digest.hexdigest()}"


def source_file_state_key(role: str, directory: Path, path: Path) -> str:
    # The root may point at a different day's flat export directory.  A
    # relative filename alone would reuse yesterday's checkpoint.
    path.relative_to(directory)
    return f"source-file:{role}:{path.resolve().as_posix().casefold()}"


def legacy_source_key(relative_file: str, sheet_name: str, row_no: int) -> str:
    """Reproduce the row identity written by releases before absolute paths."""
    identity = "\x1f".join((relative_file.casefold(), sheet_name.casefold(), str(row_no)))
    return hashlib.sha256(identity.encode("utf-8")).hexdigest()


def compatible_source_key(
    record: RawSourceRecord, relative_file: str,
    existing: Mapping[str, Tuple[str, str]],
) -> str:
    """Reuse a legacy row only when its current file ownership is certain."""
    if record.source_key in existing:
        return record.source_key
    old_key = legacy_source_key(relative_file, record.sheet_name, record.source_row_no)
    old = existing.get(old_key)
    if old is None:
        return record.source_key
    old_file, old_hash = old
    current_file = record.source_file.replace("\\", "/").casefold()
    previous_file = old_file.replace("\\", "/").casefold()
    if previous_file == current_file:
        return old_key
    if previous_file == relative_file.casefold() and old_hash == record.row_hash:
        return old_key
    return record.source_key


def file_membership_state_key(file_key: str) -> str:
    return f"file-membership:{file_key}"


def parse_file_membership(value: str) -> Dict[str, Any]:
    if not value:
        return {"raw": {}, "work_orders": [], "batches": []}
    try:
        document = json.loads(value)
        if isinstance(document, dict) and isinstance(document.get("raw"), dict):
            return document
    except (TypeError, ValueError):
        pass
    return {"raw": {}, "work_orders": [], "batches": []}


def removed_file_membership(
    state: Mapping[str, str], file_key: str, current: Mapping[str, Any],
) -> Dict[str, Any]:
    """Find rows removed from this file and absent from all other tracked files."""
    membership_key = file_membership_state_key(file_key)
    old = parse_file_membership(state.get(membership_key, ""))
    removed_raw = {
        table: set(keys) - set(current["raw"].get(table, []))
        for table, keys in old["raw"].items()
    }
    removed_orders = set(old["work_orders"]) - set(current["work_orders"])
    removed_batches = set(old["batches"]) - set(current["batches"])
    if not any(removed_raw.values()) and not removed_orders and not removed_batches:
        return {"raw": {}, "work_orders": [], "batches": []}
    for key, value in state.items():
        if not key.startswith("file-membership:") or key == membership_key:
            continue
        other = parse_file_membership(value)
        for table, keys in other["raw"].items():
            if table in removed_raw:
                removed_raw[table].difference_update(keys)
        removed_orders.difference_update(other["work_orders"])
        removed_batches.difference_update(other["batches"])
        if not any(removed_raw.values()) and not removed_orders and not removed_batches:
            break
    return {
        "raw": {table: sorted(keys) for table, keys in removed_raw.items() if keys},
        "work_orders": sorted(removed_orders),
        "batches": sorted(removed_batches),
    }


def build_source_scan_plan(
    config: Mapping[str, Any], previous: Mapping[str, str], *, force_all: bool = False,
) -> Tuple[List[SourceScanGroup], Dict[str, str]]:
    """Select only new/changed files, replaying deltas after a baseline change."""
    initialization, incremental, skip_initialization = configured_source_directories(config)
    groups: List[SourceScanGroup] = []
    checkpoints: Dict[str, str] = {}
    initialization_changed = False

    if not skip_initialization:
        if not initialization:
            raise SyncError("请选择初始化数据目录，或勾选“跳过初始化”。")
        root = Path(initialization).expanduser()
        all_files = candidate_files(root)
        if not all_files:
            raise SyncError(f"初始化数据目录中没有 Excel 文件：{root}")
        changed = []
        for path in all_files:
            key = source_file_state_key("initialization", root, path)
            value = source_file_checkpoint(path)
            checkpoints[key] = value
            if force_all or previous.get(key) != value:
                changed.append(path)
        if changed:
            initialization_changed = True
            groups.append(SourceScanGroup("initialization", root, tuple(changed)))

    if incremental:
        root = Path(incremental).expanduser()
        all_files = candidate_files(root)
        changed = []
        for path in all_files:
            key = source_file_state_key("incremental", root, path)
            value = source_file_checkpoint(path)
            checkpoints[key] = value
            if force_all or initialization_changed or previous.get(BASELINE_REPLAY_STATE_KEY) == "1" \
                    or previous.get(key) != value:
                changed.append(path)
        if changed:
            groups.append(SourceScanGroup("incremental", root, tuple(changed)))
    elif skip_initialization:
        raise SyncError("已勾选“跳过初始化”，请选择增量同步目录。")

    return groups, checkpoints


def directory_fingerprint(source_directory: Path) -> str:
    """Fingerprint Excel paths and content for reliable overwrite detection."""
    directory = Path(source_directory).expanduser()
    digest = hashlib.sha256()
    files = sorted(
        candidate_files(directory),
        key=lambda path: path.relative_to(directory).as_posix().casefold(),
    )
    for path in files:
        relative_path = path.relative_to(directory).as_posix()
        digest.update(relative_path.encode("utf-8"))
        digest.update(b"\0")
        digest.update(source_file_checkpoint(path).encode("ascii"))
        digest.update(b"\n")
    return digest.hexdigest()


class DirectoryChangeMonitor:
    """Keep a successful-sync fingerprint and detect later Excel changes."""

    def __init__(self, source_directory: Path, last_successful_fingerprint: str):
        self.source_directory = Path(source_directory).expanduser()
        self.last_successful_fingerprint = str(last_successful_fingerprint or "")

    def current_fingerprint(self) -> str:
        return directory_fingerprint(self.source_directory)

    def capture_sync_start(self) -> str:
        """Capture the directory state a sync is responsible for processing."""
        return self.current_fingerprint()

    def mark_synchronized(self, fingerprint: str) -> None:
        self.last_successful_fingerprint = str(fingerprint)

    def has_changed(self) -> bool:
        current = self.current_fingerprint()
        if not self.last_successful_fingerprint:
            # First enable establishes a baseline.  Subsequent file changes
            # trigger a sync, and a saved earlier fingerprint triggers one at
            # the next desktop startup.
            self.last_successful_fingerprint = current
            return False
        return current != self.last_successful_fingerprint


def open_erp_xls(path: Path):
    """Read ERP XLS, including the known oversized BIFF5 customer-part export."""
    workbook = xlrd.open_workbook(str(path), on_demand=True)
    if (workbook.biff_version == 50
            and canonical_source_file_name(path.name) == canonical_source_file_name("客户料号资料.xls")):
        try:
            if len(workbook.sheet_names()) != 1:
                raise SyncError(f"旧版客户料号文件工作表数量异常：{path}")
            # This exporter writes up to 65,535 rows while declaring BIFF5.
            # Build only this one known sheet with BIFF8's row ceiling; leave
            # xlrd's BIFF5 decoding rules otherwise unchanged.
            workbook._position = workbook._sh_abs_posn[0]
            workbook.getbof(xlrd.biffh.XL_WORKSHEET)
            sheet = xlrd.sheet.Sheet(
                workbook, workbook._position, workbook._sheet_names[0], 0,
            )
            sheet.utter_max_rows = 65536
            sheet.read(workbook)
            workbook._sheet_list[0] = sheet
        except Exception:
            workbook.release_resources()
            raise
    return workbook


def decode_erp_xls_cell(value: Any, encoding: str, warnings: Optional[List[int]] = None) -> Any:
    """Decode no-CODEPAGE ERP text, visibly escaping truncated GBK bytes."""
    if encoding != "iso-8859-1" or not isinstance(value, str):
        return value
    raw = value.encode("latin1")
    try:
        return raw.decode("gbk")
    except UnicodeDecodeError:
        if warnings is not None:
            warnings[0] += 1
        return raw.decode("gbk", errors="backslashreplace")


def open_excel_header(path: Path) -> List[str]:
    lower_name = path.name.lower()
    if lower_name.endswith(".xlsx"):
        workbook = load_workbook(path, read_only=True, data_only=True)
        try:
            sheet = workbook.active
            return [as_text(value) for value in next(sheet.iter_rows(values_only=True), ())]
        finally:
            workbook.close()
    workbook = open_erp_xls(path)
    try:
        sheet = workbook.sheet_by_index(0)
        return [as_text(decode_erp_xls_cell(value, workbook.encoding))
                for value in sheet.row_values(0)] if sheet.nrows else []
    finally:
        workbook.release_resources()


def find_source_file(config: Mapping[str, Any]) -> Path:
    directory = Path(str(config["source_directory"])).expanduser()
    files = candidate_files(directory)
    keyword = str(config.get("source_file_keyword", "生产指示资料")).strip()
    named = [path for path in files if keyword and keyword.lower() in path.name.lower()]
    for path in named + [path for path in files if path not in named]:
        try:
            headers = {normalize_header(header) for header in open_excel_header(path)}
        except Exception:
            continue
        if normalize_header("生产指令号") in headers and normalize_header("厂内编号") in headers:
            return path
    hint = f"（优先文件名包含“{keyword}”）" if keyword else ""
    raise SyncError(f"未在 {directory} 找到包含“生产指令号”和“厂内编号”列的生产指示 Excel {hint}。")


def iter_excel_rows(path: Path) -> Tuple[int, Iterable[Dict[str, Any]]]:
    """Return datemode and an iterator whose keys are normalized Excel headers."""
    lower_name = path.name.lower()
    if lower_name.endswith(".xlsx"):
        workbook = load_workbook(path, read_only=True, data_only=True)
        sheet = workbook.active
        values = sheet.iter_rows(values_only=True)
        headers = [normalize_header(item) for item in next(values, ())]

        def rows() -> Iterable[Dict[str, Any]]:
            try:
                for values_row in values:
                    yield {headers[index]: values_row[index] if index < len(values_row) else None for index in range(len(headers)) if headers[index]}
            finally:
                workbook.close()

        return 0, rows()

    workbook = open_erp_xls(path)
    sheet = workbook.sheet_by_index(0)
    headers = [normalize_header(decode_erp_xls_cell(item, workbook.encoding))
               for item in sheet.row_values(0)] if sheet.nrows else []
    datemode = workbook.datemode

    def rows() -> Iterable[Dict[str, Any]]:
        try:
            for row_index in range(1, sheet.nrows):
                values_row = [decode_erp_xls_cell(value, workbook.encoding)
                              for value in sheet.row_values(row_index)]
                yield {headers[index]: values_row[index] if index < len(values_row) else None for index in range(len(headers)) if headers[index]}
        finally:
            workbook.release_resources()

    return datemode, rows()


def json_safe_cell(value: Any) -> Any:
    """Represent an Excel value in portable JSON without losing its meaning."""
    if value is None:
        return None
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return format(value.normalize(), "f")
    if isinstance(value, float):
        if not math.isfinite(value):
            return None
        return int(value) if value.is_integer() else value
    if isinstance(value, (str, int, bool)):
        return value
    return str(value)


def xls_safe_cell(value: Any, cell_type: int, datemode: int) -> Any:
    """Preserve an XLS date cell as a real date/datetime before direct field import.

    ``xlrd`` exposes dates as numeric Excel serials in ``row_values()``.  The
    generic ERP business-table path writes every source column directly, so
    relying on the value alone would persist values such as ``42195`` instead
    of the intended date.  Only the explicit XLS date cell type is converted;
    ordinary numeric identifiers and quantities remain numeric.
    """
    if cell_type != xlrd.XL_CELL_DATE:
        return json_safe_cell(value)
    try:
        serial = float(value)
        # The ERP exports use the first three 1900-system serials as blank
        # date sentinels in several columns.  Persisting them would create
        # misleading BI values such as 1900-01-02.
        if datemode == 0 and serial in (0.0, 1.0, 2.0):
            return None
        converted = xlrd.xldate_as_datetime(serial, datemode)
    except (TypeError, ValueError, OverflowError):
        return json_safe_cell(value)
    if converted.time() == datetime.min.time():
        return converted.date().isoformat()
    return converted.isoformat(sep=" ", timespec="seconds")


def xlsx_safe_cell(value: Any) -> Any:
    """Use one BI-friendly date representation for modern Excel workbooks."""
    if isinstance(value, datetime):
        if value.time() == datetime.min.time():
            return value.date().isoformat()
        return value.isoformat(sep=" ", timespec="seconds")
    if isinstance(value, date):
        return value.isoformat()
    return json_safe_cell(value)


def unique_headers(values: Sequence[Any]) -> List[str]:
    """Keep every Excel column, including blank or duplicate headings."""
    counts: Dict[str, int] = {}
    result: List[str] = []
    for index, value in enumerate(values, start=1):
        base = excel_header_identity(value) or f"列{index}"
        count = counts.get(base, 0) + 1
        counts[base] = count
        result.append(base if count == 1 else f"{base}（重复列{count}）")
    return result


ERP_FIELD_PREFIX = "erp_"
MYSQL_IDENTIFIER_LIMIT = 64


def legacy_database_column_name(excel_header: Any) -> str:
    """Create a stable, human-readable MySQL field for an Excel column.

    The ERP header remains visible in the physical database field, for example
    ``客户订单号`` becomes ``erp_客户订单号``.  This keeps BI queries readable
    while reserving the non-prefixed names for QMS's native business fields.
    """
    original = as_text(excel_header) or "空列"
    cleaned = re.sub(r"[\x00-\x1f\x7f]", "", original)
    cleaned = re.sub(r"\s+", "_", cleaned).replace("`", "") or "空列"
    candidate = f"{ERP_FIELD_PREFIX}{cleaned}"
    if len(candidate) <= MYSQL_IDENTIFIER_LIMIT:
        return candidate
    digest = hashlib.sha256(candidate.encode("utf-8")).hexdigest()[:10]
    return f"{candidate[:MYSQL_IDENTIFIER_LIMIT - len(digest) - 1]}_{digest}"


def database_column_name(excel_header: Any) -> str:
    """Compatibility for old callers; new consumers must resolve the registry."""
    return legacy_database_column_name(excel_header)


ERP_FIELD_NAME_PATTERN = re.compile(r"erp_[a-z][a-z0-9_]{0,59}\Z")
ERP_FIELD_TABLES = BUSINESS_SOURCE_TABLES | {"qms_work_order"}


def erp_column_comment(excel_source_header: str) -> str:
    """Replace each C0/C1 control run with one space, only for display comments.

    Keep ordinary text/spacing intact; raw headers remain separate lookup keys
    and inputs to the historical physical-name algorithm.
    """
    display_header = re.sub(r"[\x00-\x1f\x7f-\x9f]+", " ", excel_source_header)
    return f"Excel列名：{display_header}"


@dataclass(frozen=True)
class ErpFieldDefinition:
    table_name: str
    source_file: str
    sheet_name: str
    excel_source_header: str
    excel_unique_header: str
    database_column: str
    legacy_database_column: str
    column_comment: str
    column_index: int = 0


def canonical_source_file_name(source_file: str) -> str:
    """Match registry files by basename across date folders and doubled suffixes."""
    name = Path(str(source_file).replace("\\", "/")).name.casefold()
    while name.endswith(".xlsx") or name.endswith(".xls"):
        name = name[:-5] if name.endswith(".xlsx") else name[:-4]
    return name


class ErpFieldRegistry:
    """Validated source-scoped mappings; no dynamic fallback is permitted."""

    def __init__(
        self, fields: Iterable[ErpFieldDefinition],
        source_layouts: Iterable[Mapping[str, Any]] = (),
    ) -> None:
        definitions = tuple(fields)
        scopes = {}
        by_position = {}
        by_target = {}
        targets = set()
        positions = set()
        for field in definitions:
            canonical_file = canonical_source_file_name(field.source_file)
            scope = (field.table_name, canonical_file, field.sheet_name, field.excel_unique_header)
            target = (field.table_name, field.database_column)
            position = (field.table_name, canonical_file, field.sheet_name, field.column_index)
            strings = (
                field.table_name, field.source_file, field.sheet_name, field.excel_source_header,
                field.excel_unique_header, field.database_column, field.legacy_database_column,
                field.column_comment,
            )
            if (not all(isinstance(value, str) for value in strings)
                    or not field.source_file or not field.sheet_name or not field.excel_unique_header
                    or type(field.column_index) is not int or field.column_index < 1):
                raise SyncError(f"字段注册表条目格式错误：{field!r}")
            if field.table_name not in ERP_FIELD_TABLES:
                raise SyncError(f"字段注册表目标表不允许：{field.table_name}")
            if (not ERP_FIELD_NAME_PATTERN.fullmatch(field.database_column)
                    or len(field.database_column.encode("utf-8")) > MYSQL_IDENTIFIER_LIMIT):
                raise SyncError(f"字段注册表必须使用有效英文数据库字段：{field.database_column}")
            if field.column_comment != erp_column_comment(field.excel_source_header):
                raise SyncError(f"字段注册表注释与原始列名不一致：{scope}")
            if field.legacy_database_column != legacy_database_column_name(field.excel_unique_header):
                raise SyncError(f"字段注册表旧数据库字段不一致：{scope}")
            if scope in scopes or position in positions:
                raise SyncError(f"字段注册表来源作用域重复：{scope}")
            if target in targets:
                raise SyncError(f"字段注册表目标字段冲突：{target}")
            scopes[scope] = field
            by_position[position] = field
            by_target[target] = field
            targets.add(target)
            positions.add(position)
        self.fields = definitions
        self._by_scope = MappingProxyType(scopes)
        self._by_position = MappingProxyType(by_position)
        self._by_target = MappingProxyType(by_target)
        layouts = {}
        new_target_comments = {}
        new_target_sources = {}
        for source_layout in source_layouts:
            if not isinstance(source_layout, dict):
                raise SyncError("字段注册表增量表头版本格式错误。")
            source_file = source_layout.get("source_file")
            table_name = source_layout.get("table_name")
            raw_headers = source_layout.get("raw_headers")
            canonical_headers = source_layout.get("canonical_headers", raw_headers)
            database_columns = source_layout.get("database_columns")
            if (not isinstance(source_file, str) or not source_file
                    or table_name not in ERP_FIELD_TABLES
                    or not all(isinstance(item, list) for item in
                               (raw_headers, canonical_headers, database_columns))
                    or not raw_headers
                    or not (len(raw_headers) == len(canonical_headers) == len(database_columns))
                    or not all(item is None or isinstance(item, (str, int, float, bool))
                               for item in raw_headers + canonical_headers)
                    or not all(isinstance(item, str) and ERP_FIELD_NAME_PATTERN.fullmatch(item)
                               for item in database_columns)
                    or len(set(database_columns)) != len(database_columns)):
                raise SyncError(f"字段注册表增量表头版本格式错误：{source_file}")
            key = (canonical_source_file_name(source_file), tuple(raw_headers))
            if key in layouts:
                raise SyncError(f"字段注册表增量表头版本重复：{source_file}")
            for header, column in zip(canonical_headers, database_columns):
                if (table_name, column) not in by_target:
                    target = (table_name, column)
                    source = excel_header_identity(header)
                    comment = erp_column_comment(source)
                    if target in new_target_comments and new_target_comments[target] != comment:
                        raise SyncError(f"字段注册表增量字段语义冲突：{target}")
                    new_target_comments[target] = comment
                    new_target_sources.setdefault(target, (source_file, source))
            layouts[key] = source_layout
        self.source_layouts = tuple(layouts.values())
        self._source_layouts = MappingProxyType(layouts)
        extra_fields = {}
        extra_positions = {}
        for (table_name, column), (source_file, source) in sorted(new_target_sources.items()):
            position_key = (table_name, canonical_source_file_name(source_file))
            index = extra_positions.get(position_key, 0) + 1
            extra_positions[position_key] = index
            unique = f"{source}__{column}"
            extra_fields[(table_name, column)] = ErpFieldDefinition(
                table_name, source_file, "增量字段", source, unique, column,
                legacy_database_column_name(unique), new_target_comments[(table_name, column)], index,
            )
        self._layout_extra_fields = MappingProxyType(extra_fields)

    def _matched_layout(self, source_file: str, raw_headers: Sequence[Any]) -> Optional[Mapping[str, Any]]:
        if not all(header is None or isinstance(header, (str, int, float, bool))
                   for header in raw_headers):
            return None
        return self._source_layouts.get((canonical_source_file_name(source_file), tuple(raw_headers)))

    def canonical_headers_for(self, source_file: str, raw_headers: Sequence[Any]) -> List[Any]:
        layout = self._matched_layout(source_file, raw_headers)
        return list(layout.get("canonical_headers", raw_headers)) if layout else list(raw_headers)

    def resolve_sheet(
        self, table_name: str, source_file: str, sheet_name: str, raw_headers: Sequence[Any],
    ) -> List[ErpFieldDefinition]:
        layout = self._matched_layout(source_file, raw_headers)
        if layout is None:
            return [
                self.resolve(table_name, source_file, sheet_name,
                             excel_header_identity(header), unique, index)
                for index, (header, unique) in enumerate(
                    zip(raw_headers, unique_headers(raw_headers)), 1)
            ]
        if layout["table_name"] != table_name:
            raise SyncError(f"字段注册表增量表头目标表不一致：{source_file} / {sheet_name}")
        return [
            self._by_target.get((table_name, column))
            or self._layout_extra_fields[(table_name, column)]
            for column in layout["database_columns"]
        ]

    def resolve(
        self, table_name: str, source_file: str, sheet_name: str,
        excel_source_header: str, excel_unique_header: str, column_index: int,
    ) -> ErpFieldDefinition:
        scope = (table_name, canonical_source_file_name(source_file), sheet_name, excel_unique_header)
        field = self._by_scope.get(scope)
        if field is None and type(column_index) is int:
            candidate = self._by_position.get(
                (table_name, canonical_source_file_name(source_file), sheet_name, column_index)
            )
            if (
                candidate is not None
                and candidate.excel_source_header.lstrip("\\") == excel_source_header.lstrip("\\")
                and candidate.excel_unique_header.lstrip("\\") == excel_unique_header.lstrip("\\")
            ):
                # Some ERP daily exports collapse a doubled leading backslash
                # in two customer-part headers.  Position and semantic header
                # still have to match; unrelated header drift remains fatal.
                field = candidate
        if (field is None or field.excel_source_header.lstrip("\\") != excel_source_header.lstrip("\\")
                or type(column_index) is not int or field.column_index != column_index):
            raise SyncError(
                f"字段注册表未登记或表头已变化：{table_name} / {source_file} / {sheet_name} / "
                f"第{column_index}列 {excel_source_header!r}（唯一列名 {excel_unique_header!r}）。"
                "请更新并审核 erp_field_registry.json 后重试。"
            )
        return field


def bundled_resource_path(name: str) -> Path:
    """Return a bundled PyInstaller resource or the adjacent source resource."""
    bundle_root = getattr(sys, "_MEIPASS", None) if getattr(sys, "frozen", False) else None
    if bundle_root:
        return Path(bundle_root) / name
    return Path(__file__).resolve().with_name(name)


def load_erp_field_registry(path: Optional[Path] = None) -> ErpFieldRegistry:
    registry_path = Path(path) if path is not None else bundled_resource_path("erp_field_registry.json")
    try:
        data = json.loads(registry_path.read_text(encoding="utf-8"))
        if (not isinstance(data, dict) or data.get("schema_version") != 1
                or not isinstance(data.get("fields"), list) or not data["fields"]):
            raise ValueError("需要 schema_version=1 和非空 fields 列表")
        return ErpFieldRegistry(
            (ErpFieldDefinition(**entry) for entry in data["fields"]),
            data.get("source_layouts", ()),
        )
    except (OSError, ValueError, TypeError, KeyError) as exc:
        raise SyncError(f"字段注册表读取失败：{registry_path}；{exc}。请检查或重新生成注册表。") from exc


def database_cell_value(value: Any) -> Optional[str]:
    """Keep an Excel cell in a direct, nullable database field without JSON."""
    if is_empty(value):
        return None
    if isinstance(value, datetime):
        return value.isoformat(sep=" ")
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, Decimal):
        return format(value.normalize(), "f")
    if isinstance(value, float):
        if not math.isfinite(value):
            return None
        return str(int(value)) if value.is_integer() else str(value)
    return as_text(value) or None


def source_table_name(source_file: str, _sheet_name: str, is_work_order: bool) -> Optional[str]:
    """Return the fixed business table for an ERP workbook.

    Production-instruction rows are written through the specialized
    qms_work_order / qms_production_batch mappings, not to a generic source
    table.  All other workbooks use one stable business table name.
    """
    if is_work_order:
        return None
    file_name = Path(source_file).name.casefold()
    for marker, destination in BUSINESS_SOURCE_TABLE_BY_FILE:
        if marker.casefold() in file_name:
            return destination
    return UNCLASSIFIED_SOURCE_TABLE


def is_work_order_sheet(headers: Sequence[Any]) -> bool:
    normalized = {normalize_header(header) for header in headers if normalize_header(header)}
    return normalize_header("生产指令号") in normalized and normalize_header("厂内编号") in normalized


def raw_business_key(row: Mapping[str, Any], row_no: int) -> str:
    """A readable, stable-enough source identifier; row number guarantees uniqueness."""
    candidates = (
        "生产指令号", "生产通知单号", "客户订单号", "订单编号", "采购订单号",
        "送货单号", "入库单号", "出库单号", "单据编号", "单号", "厂内编号",
        "客户料号", "料号", "物料编号", "板材编号",
    )
    for header in candidates:
        value = as_text(row.get(normalize_header(header)))
        if value and value.rstrip(":：").strip() != "合计":
            return f"{header}:{value}#行{row_no}"
    return f"行{row_no}"


def iter_all_source_records(
    config: Mapping[str, Any], callback: Callable[[str], None], stats: SourceScanStats,
    *, source_directory: Optional[Path] = None, selected_files: Optional[Sequence[Path]] = None,
) -> Iterable[Tuple[RawSourceRecord, Optional[Dict[str, Any]]]]:
    """Traverse every Excel file and every worksheet below the configured directory.

    The keyword selects only the workbook whose rows are additionally mapped to
    QMS work orders.  It never filters the ERP raw-record import.
    """
    if source_directory is None:
        initialization, _, _ = configured_source_directories(config)
        directory = Path(initialization).expanduser()
    else:
        directory = Path(source_directory).expanduser()
    files = list(selected_files) if selected_files is not None else candidate_files(directory)
    if not files:
        raise SyncError(f"数据源目录中没有 Excel 文件：{directory}")
    registry = load_erp_field_registry()
    keyword = str(config.get("source_file_keyword", "生产指示资料")).strip().casefold()
    callback(f"本次处理 {len(files):,} 个新增或变更的 Excel 文件及其所有工作表。")

    for file_index, path in enumerate(files, start=1):
        try:
            relative_file = path.relative_to(directory).as_posix()
        except ValueError:
            relative_file = path.name
        source_location = path.resolve().as_posix()
        if len(source_location) > 500:
            raise SyncError(f"源文件完整路径超过数据库字段长度：{relative_file}")
        stats.files_scanned += 1
        callback(f"遍历文件 {file_index:,}/{len(files):,}：{relative_file}")
        map_work_orders = not keyword or keyword in path.name.casefold()
        lower_name = path.name.lower()

        if lower_name.endswith(".xlsx"):
            try:
                workbook = load_workbook(path, read_only=True, data_only=True)
            except Exception as exc:
                raise SyncError(f"无法打开 Excel 文件 {relative_file}：{exc}") from exc
            try:
                for sheet in workbook.worksheets:
                    stats.sheets_scanned += 1
                    values = sheet.iter_rows(values_only=True)
                    raw_header_values = list(next(values, ()))
                    if sheet.max_row <= 1:
                        callback(f"  工作表：{sheet.title}（0 条数据，跳过字段写入）")
                        continue
                    raw_headers = unique_headers(raw_header_values)
                    reviewed_headers = registry.canonical_headers_for(relative_file, raw_header_values)
                    normalized_headers = [normalize_header(value) for value in reviewed_headers]
                    is_work_order = map_work_orders and is_work_order_sheet(reviewed_headers)
                    target_table = source_table_name(relative_file, sheet.title, is_work_order)
                    definitions = registry.resolve_sheet(
                        target_table or "qms_work_order", relative_file, sheet.title, raw_header_values,
                    )
                    callback(
                        f"  工作表：{sheet.title}（{'工单映射 + 实体字段写入' if is_work_order else '实体字段写入'}，"
                        f"目标表：{target_table or 'qms_work_order / qms_production_batch'}）"
                    )
                    for row_index, values_row in enumerate(values, start=2):
                        row = {
                            normalized_headers[index]: values_row[index] if index < len(values_row) else None
                            for index in range(len(normalized_headers)) if normalized_headers[index]
                        }
                        raw_data = {
                            raw_headers[index]: xlsx_safe_cell(values_row[index] if index < len(values_row) else None)
                            for index in range(len(raw_headers))
                        }
                        if all(is_empty(value) for value in raw_data.values()):
                            continue
                        yield from _source_record_pair(
                            relative_file, sheet.title, row_index, row, raw_data, 0, is_work_order,
                            stats, target_table, definitions, source_location,
                        )
            finally:
                workbook.close()
            continue

        try:
            workbook = open_erp_xls(path)
        except Exception as exc:
            raise SyncError(f"无法打开 Excel 文件 {relative_file}：{exc}") from exc
        try:
            decode_warnings = [0]
            for raw_sheet_name in workbook.sheet_names():
                sheet = workbook.sheet_by_name(raw_sheet_name)
                sheet_name = decode_erp_xls_cell(raw_sheet_name, workbook.encoding, decode_warnings)
                stats.sheets_scanned += 1
                raw_header_values = [
                    decode_erp_xls_cell(value, workbook.encoding, decode_warnings)
                    for value in sheet.row_values(0)
                ] if sheet.nrows else []
                if sheet.nrows <= 1:
                    callback(f"  工作表：{sheet_name}（0 条数据，跳过字段写入）")
                    continue
                raw_headers = unique_headers(raw_header_values)
                reviewed_headers = registry.canonical_headers_for(relative_file, raw_header_values)
                normalized_headers = [normalize_header(value) for value in reviewed_headers]
                is_work_order = map_work_orders and is_work_order_sheet(reviewed_headers)
                target_table = source_table_name(relative_file, sheet_name, is_work_order)
                definitions = registry.resolve_sheet(
                    target_table or "qms_work_order", relative_file, sheet_name, raw_header_values,
                )
                callback(
                    f"  工作表：{sheet_name}（{'工单映射 + 实体字段写入' if is_work_order else '实体字段写入'}，"
                    f"目标表：{target_table or 'qms_work_order / qms_production_batch'}）"
                )
                for zero_based_row in range(1, sheet.nrows):
                    values_row = [
                        decode_erp_xls_cell(value, workbook.encoding, decode_warnings)
                        for value in sheet.row_values(zero_based_row)
                    ]
                    row = {
                        normalized_headers[index]: values_row[index] if index < len(values_row) else None
                        for index in range(len(normalized_headers)) if normalized_headers[index]
                    }
                    raw_data = {
                        raw_headers[index]: xls_safe_cell(
                            values_row[index] if index < len(values_row) else None,
                            sheet.cell_type(zero_based_row, index) if index < len(values_row) else xlrd.XL_CELL_EMPTY,
                            workbook.datemode,
                        )
                        for index in range(len(raw_headers))
                    }
                    if all(is_empty(value) for value in raw_data.values()):
                        continue
                    yield from _source_record_pair(
                        relative_file, sheet_name, zero_based_row + 1, row, raw_data,
                        workbook.datemode, is_work_order, stats, target_table, definitions,
                        source_location,
                    )
            if decode_warnings[0]:
                callback(
                    f"  {relative_file} 有 {decode_warnings[0]:,} 个文本单元格的 GBK 字节被源文件截断；"
                    "无法还原的字节已保留为 \\x.. 标记。"
                )
        finally:
            workbook.release_resources()


def _source_record_pair(
    relative_file: str,
    sheet_name: str,
    row_no: int,
    row: Mapping[str, Any],
    raw_data: Mapping[str, Any],
    datemode: int,
    is_work_order: bool,
    stats: SourceScanStats,
    source_table: Optional[str],
    definitions: Sequence[ErpFieldDefinition],
    source_location: str,
) -> Iterable[Tuple[RawSourceRecord, Optional[Dict[str, Any]]]]:
    """Build a source record and, where applicable, its work-order view."""
    field_values = {
        field.database_column: database_cell_value(value)
        for field, value in zip(definitions, raw_data.values())
    }
    row_document = json.dumps(field_values or raw_data, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    table_name = source_table or "qms_work_order"
    identity = f"{table_name}\x1f{erp_row_identity(table_name, field_values or raw_data)}"
    raw = RawSourceRecord(
        source_file=source_location,
        sheet_name=sheet_name,
        source_row_no=row_no,
        business_key=raw_business_key(row, row_no),
        source_key="ERP4:" + hashlib.sha256(identity.encode("utf-8")).hexdigest()[:59],
        row_hash=hashlib.sha256(row_document.encode("utf-8")).hexdigest(),
        # Definitions and raw_data are both built in worksheet column order.
        # Pair by position so the reviewed field mapping still works when an
        # allowed daily-export header alias differs only in leading slashes.
        field_values=field_values,
        source_table=source_table,
        field_definitions={field.database_column: field for field in definitions},
    )
    stats.raw_records += 1
    payload: Optional[Dict[str, Any]] = None
    if is_work_order:
        source_order_no = as_text(row.get(normalize_header("生产指令号")))
        if source_order_no.rstrip(":：").strip() != "合计":
            try:
                payload = build_payload(row, datemode)
            except SyncError as exc:
                raise SyncError(f"{relative_file} / {sheet_name} 第 {row_no} 行：{exc}") from exc
            # Every production-instruction header gets a queryable physical
            # English field on qms_work_order, in addition to the
            # normal QMS work-order/batch mappings created above.
            payload["erpFields"] = dict(raw.field_values)
            payload["erpFieldDefinitions"] = dict(raw.field_definitions)
            payload["sourceVersion"] = payload_hash(payload)
            stats.work_order_records += 1
    yield raw, payload


def source_value(row: Mapping[str, Any], qms_field: str) -> Any:
    header = FIELD_MAP.get(qms_field)
    return row.get(normalize_header(header)) if header else None


def build_payload(row: Mapping[str, Any], datemode: int) -> Dict[str, Any]:
    payload: Dict[str, Any] = {}
    for field in DATE_FIELDS:
        payload[field] = excel_date(source_value(row, field), datemode)
    for field in INTEGER_FIELDS:
        payload[field] = as_integer(source_value(row, field))
    for field in DECIMAL_FIELDS:
        payload[field] = as_decimal(source_value(row, field))
    for field in set(FIELD_MAP) - DATE_FIELDS - INTEGER_FIELDS - DECIMAL_FIELDS:
        payload[field] = as_text(source_value(row, field)) or None

    payload["specification"] = " / ".join(
        part for part in (payload.get("material"), payload.get("boardThickness"), payload.get("copperThickness")) if part
    ) or None
    payload["warehouseStatus"] = warehouse_status(row.get(normalize_header("入库/已结批")))
    payload["releasedAt"] = payload["materialInputDate"]
    payload["priority"] = "URGENT" if truthy(row.get(normalize_header("加急订单"))) else "NORMAL"

    total_panels = as_integer(row.get(normalize_header("本卡工作板数")))
    if total_panels is None:
        panel_values = [
            as_integer(row.get(normalize_header(header))) or 0
            for header in ("A板总PNL", "B板总PNL", "C板总PNL")
        ]
        total_panels = sum(panel_values) if any(panel_values) else None
    payload["totalPanelQuantity"] = total_panels
    payload["panelizationNo"] = None
    payload["processRouteVersion"] = None
    payload["miVersion"] = None

    work_order_no = payload.get("workOrderNo")
    if not work_order_no:
        raise SyncError("发现缺少“生产指令号”的数据行，无法作为 QMS 工单唯一键。")
    if not payload.get("productCode"):
        raise SyncError(f"生产指令号 {work_order_no} 缺少“厂内编号”。")
    if not payload.get("currentProcessCode"):
        raise SyncError(f"生产指令号 {work_order_no} 缺少“工艺”。")
    if payload.get("plannedQuantity") is None or payload["plannedQuantity"] < 0:
        raise SyncError(f"生产指令号 {work_order_no} 的“投料数量”无效。")

    payload["sourceKey"] = f"{SOURCE_KEY_PREFIX}{work_order_no}"
    payload["sourceVersion"] = payload_hash(payload)
    return payload


def payload_hash(payload: Mapping[str, Any]) -> str:
    # Definitions describe schema, not business values, and are not JSON data.
    values = {key: value for key, value in payload.items() if key != "erpFieldDefinitions"}
    document = json.dumps(values, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(document.encode("utf-8")).hexdigest()


def read_source_records(config: Mapping[str, Any], callback: Callable[[str], None]) -> Tuple[Path, Dict[str, Dict[str, Any]], int]:
    source = find_source_file(config)
    callback(f"读取生产指示文件：{source.name}")
    datemode, rows = iter_excel_rows(source)
    records: Dict[str, Dict[str, Any]] = {}
    count = 0
    for count, row in enumerate(rows, start=1):
        if all(is_empty(value) for value in row.values()):
            continue
        # ERP exports append a non-empty “合计” row after the detail rows.
        # It is not a production instruction and has no product columns.
        source_order_no = as_text(row.get(normalize_header("生产指令号")))
        if source_order_no.rstrip(":：").strip() == "合计":
            continue
        try:
            payload = build_payload(row, datemode)
        except SyncError as exc:
            raise SyncError(f"{source.name} 第 {count + 1} 行：{exc}") from exc
        source_key = payload["sourceKey"]
        existing = records.get(source_key)
        if existing is not None and payload_hash(existing) != payload_hash(payload):
            raise SyncError(f"{source.name} 中的生产指令号重复且内容不一致：{payload['workOrderNo']}")
        records[source_key] = payload
        if count % 1000 == 0:
            callback(f"已读取 {count:,} 行…")
    if not records:
        raise SyncError(f"{source.name} 没有可导入的生产指示数据。")
    callback(f"读取完成：{len(records):,} 条有效生产指令。")
    return source, records, count


class QmsDatabaseClient:
    """Direct MySQL writer for the QMS business and ERP source tables."""

    def __init__(self, config: Mapping[str, Any]):
        self.host = str(config.get("database_host", "")).strip()
        self.port = str(config.get("database_port", "")).strip()
        self.database = str(config.get("database_name", "")).strip()
        self.username = str(config.get("database_username", "")).strip()
        self.password = str(config.get("database_password", ""))
        self.tenant = str(config.get("tenant_code", "")).strip()
        self.timeout = int(config.get("request_timeout_seconds", 30))
        self._table_columns: Dict[str, Dict[str, str]] = {}
        self._legacy_json_checked: set[str] = set()
        self._identity_checked: set[str] = set()
        self._source_table_ready: set[str] = set()
        if not all((self.host, self.port, self.database, self.username, self.tenant)):
            raise SyncError("请完整填写数据库主机、端口、库名、账号和 QMS 租户编码。")
        try:
            int(self.port)
        except ValueError as exc:
            raise SyncError("数据库端口必须是数字。") from exc

    def _connect(self):
        try:
            return pymysql.connect(
                host=self.host,
                port=int(self.port),
                database=self.database,
                user=self.username,
                password=self.password,
                connect_timeout=self.timeout,
                charset="utf8mb4",
                autocommit=False,
            )
        except MySQLError as exc:
            raise SyncError(f"无法连接 QMS MySQL 数据库：{exc}") from exc

    @staticmethod
    def _table_name(table_name: str) -> str:
        """Quote a controlled MySQL identifier after rejecting unsafe names."""
        if table_name not in BUSINESS_SOURCE_TABLES and table_name not in {
            "qms_work_order", "qms_production_batch",
        }:
            raise SyncError(f"不允许的目标表名：{table_name}")
        return f"`{table_name}`"

    @staticmethod
    def _column_name(column_name: str) -> str:
        """Quote only an ASCII English field accepted by the registry."""
        if (
            not isinstance(column_name, str)
            or not ERP_FIELD_NAME_PATTERN.fullmatch(column_name)
            or len(column_name.encode("utf-8")) > MYSQL_IDENTIFIER_LIMIT
        ):
            raise SyncError(f"不允许的 ERP 字段名：{column_name}")
        return f"`{column_name}`"

    @classmethod
    def _parameterized_column_name(cls, column_name: str) -> str:
        """Validated English identifiers contain no percent-format characters."""
        return cls._column_name(column_name)

    def _read_table_columns(self, cursor, table_name: str) -> Dict[str, str]:
        cached = self._table_columns.get(table_name)
        if cached is not None:
            return cached
        cursor.execute(
            """
            SELECT column_name, column_comment
            FROM information_schema.columns
            WHERE table_schema = DATABASE() AND table_name = %s
            """,
            (table_name,),
        )
        columns = {str(row[0]): str(row[1] or "") for row in cursor.fetchall()}
        self._table_columns[table_name] = columns
        return columns

    @staticmethod
    def _validate_erp_field_definitions(table_name: str, fields: Mapping[str, ErpFieldDefinition]) -> None:
        if not isinstance(fields, Mapping):
            raise SyncError("ERP 字段定义格式无效。")
        for name, field in fields.items():
            if (not isinstance(field, ErpFieldDefinition) or name != field.database_column
                    or field.table_name != table_name):
                raise SyncError(f"ERP 字段定义与目标表或字段名不一致：{table_name} / {name}")
        ErpFieldRegistry(fields.values())

    def _ensure_erp_columns(self, cursor, table_name: str, fields: Mapping[str, ErpFieldDefinition]) -> None:
        """Add actual ERP fields as nullable text columns, never as JSON.

        Text keeps an ERP export's identifiers, leading zeroes and occasional
        non-numeric exception values intact.  The QMS native fields retain
        their existing date/number types and conversions.
        """
        self._validate_erp_field_definitions(table_name, fields)
        desired = sorted(fields)
        if not desired:
            return
        table = self._table_name(table_name)
        existing = self._read_table_columns(cursor, table_name)
        changed = [name for name in desired if existing.get(name) != fields[name].column_comment]
        for offset in range(0, len(changed), 50):
            batch = changed[offset:offset + 50]
            alterations = ", ".join(
                f"{'MODIFY' if name in existing else 'ADD'} COLUMN {self._column_name(name)} "
                "LONGTEXT NULL COMMENT %s" for name in batch
            )
            try:
                cursor.execute(
                    f"ALTER TABLE {table} {alterations}",
                    tuple(fields[name].column_comment for name in batch),
                )
            except MySQLError as exc:
                self._table_columns.pop(table_name, None)
                raise SyncError(
                    f"无法在 {table_name} 创建 ERP 业务字段或更新字段注释。"
                    "请使用拥有 ALTER TABLE 权限的 MySQL 账号运行同步。\n"
                    f"{exc}"
                ) from exc
            existing.update((name, fields[name].column_comment) for name in batch)

    def _ensure_source_table_schema(self, cursor, table_name: str, fields: Mapping[str, ErpFieldDefinition]) -> None:
        """Create a fixed ERP business table in MySQL when it is first needed."""
        table = self._table_name(table_name)
        if table_name not in self._source_table_ready:
            digest = hashlib.sha256(table_name.encode("utf-8")).hexdigest()[:16]
            try:
                cursor.execute(
                    f"""
                    CREATE TABLE IF NOT EXISTS {table} (
                            id CHAR(36) NOT NULL,
                            tenant_code VARCHAR(64) NOT NULL,
                            source_key VARCHAR(64) NOT NULL,
                            source_file VARCHAR(500) NOT NULL,
                            sheet_name VARCHAR(255) NOT NULL,
                            source_row_no INTEGER NOT NULL,
                            business_key VARCHAR(600) NOT NULL,
                            row_hash VARCHAR(64) NOT NULL,
                            status VARCHAR(24) NOT NULL DEFAULT 'ACTIVE',
                            created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
                            updated_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
                            PRIMARY KEY (id),
                            UNIQUE KEY `uq_{digest}_source` (tenant_code, source_key),
                            KEY `idx_{digest}_lookup` (tenant_code, source_file(128), sheet_name(64), status)
                        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                    """
                )
            except MySQLError as exc:
                raise SyncError(
                    f"无法初始化 ERP 源数据表 {table_name}。"
                    "请使用拥有 MySQL 建表和建索引权限的账号运行同步。\n"
                    f"{exc}"
                ) from exc
            self._source_table_ready.add(table_name)
        # Earlier versions had a required row_data_json field.  Do not erase
        # historic JSON, but make the legacy column optional so new rows are
        # stored only in actual ERP fields.
        existing = self._read_table_columns(cursor, table_name)
        if table_name not in self._legacy_json_checked:
            if "row_data_json" in existing:
                try:
                    cursor.execute(f"ALTER TABLE {table} MODIFY COLUMN `row_data_json` LONGTEXT NULL")
                    existing["row_data_json"] = ""
                except MySQLError as exc:
                    raise SyncError(
                        f"无法将 {table_name} 的旧 row_data_json 字段改为可空。"
                        "请使用拥有 ALTER TABLE 权限的 MySQL 账号运行同步。\n"
                        f"{exc}"
                    ) from exc
            self._legacy_json_checked.add(table_name)
        self._ensure_erp_columns(cursor, table_name, fields)

    def _upsert_source_records(
        self, cursor, table_name: str, records: Sequence[RawSourceRecord], *, ensure_schema: bool = True,
    ) -> None:
        """Idempotently write a batch without trusting the local cache as truth."""
        if not records:
            return
        fields: Dict[str, ErpFieldDefinition] = {}
        for record in records:
            if record.source_table != table_name or set(record.field_values) != set(record.field_definitions):
                raise SyncError("ERP 源记录的字段值、字段定义或目标表不一致。")
            for name, field in record.field_definitions.items():
                if name in fields and fields[name] != field:
                    raise SyncError(f"ERP 源记录的字段定义冲突：{table_name} / {name}")
                fields[name] = field
        self._validate_erp_field_definitions(table_name, fields)
        erp_columns = sorted(fields)
        if ensure_schema:
            self._ensure_source_table_schema(cursor, table_name, fields)
        table = self._table_name(table_name)
        if ensure_schema and table_name not in self._identity_checked:
            cursor.execute(f"SELECT 1 FROM {table} WHERE `source_key` NOT LIKE 'ERP4:%' LIMIT 1")
            if cursor.fetchone():
                raise SyncError("数据库中仍有旧版来源键；请先使用“清空并重新初始化”。")
            self._identity_checked.add(table_name)
        value_columns = [
            "id", "tenant_code", "source_key", "source_file", "sheet_name", "source_row_no",
            "business_key", "row_hash", *erp_columns,
        ]
        quoted_columns = [f"`{column}`" if not column.startswith(ERP_FIELD_PREFIX) else self._parameterized_column_name(column)
                          for column in value_columns]
        placeholders = ", ".join(["%s"] * len(value_columns) + ["'ACTIVE'", "CURRENT_TIMESTAMP(6)", "CURRENT_TIMESTAMP(6)"])
        update_columns = [
            "`source_file` = VALUES(`source_file`)",
            "`sheet_name` = VALUES(`sheet_name`)",
            "`source_row_no` = VALUES(`source_row_no`)",
            "`business_key` = VALUES(`business_key`)",
            "`row_hash` = VALUES(`row_hash`)",
            *(
                f"{self._parameterized_column_name(column)} = VALUES("
                f"{self._parameterized_column_name(column)})"
                for column in erp_columns
            ),
            "`status` = 'ACTIVE'",
            "`updated_at` = CURRENT_TIMESTAMP(6)",
        ]
        statement = f"""
            INSERT INTO {table} (
                {", ".join(quoted_columns)}, `status`, `created_at`, `updated_at`
            ) VALUES ({placeholders})
            ON DUPLICATE KEY UPDATE
                {", ".join(update_columns)}
        """
        cursor.executemany(
            statement,
            [
                (
                    str(uuid.uuid4()), self.tenant, record.source_key, record.source_file,
                    record.sheet_name, record.source_row_no, record.business_key, record.row_hash,
                    *(record.field_values.get(column) for column in erp_columns),
                )
                for record in records
            ],
        )

    def _deactivate_removed_file_records(self, cursor, removed: Mapping[str, Any]) -> int:
        """Deactivate only keys known to have belonged to an overwritten file."""
        total = 0
        for table_name, source_keys in removed["raw"].items():
            table = self._table_name(table_name)
            for offset in range(0, len(source_keys), 500):
                batch = source_keys[offset:offset + 500]
                placeholders = ", ".join(["%s"] * len(batch))
                cursor.execute(
                    f"UPDATE {table} SET `status` = 'INACTIVE', `updated_at` = CURRENT_TIMESTAMP(6) "
                    f"WHERE `tenant_code` = %s AND `status` IN ('ACTIVE', 'SUPERSEDED') "
                    f"AND `source_key` IN ({placeholders})",
                    (self.tenant, *batch),
                )
                total += cursor.rowcount
        for offset in range(0, len(removed["work_orders"]), 500):
            batch = removed["work_orders"][offset:offset + 500]
            placeholders = ", ".join(["%s"] * len(batch))
            cursor.execute(
                "UPDATE `qms_work_order` SET `status` = 'INACTIVE', "
                "`updated_at` = CURRENT_TIMESTAMP(6) "
                "WHERE `tenant_code` = %s AND `source_system` = 'ERP_EXCEL' "
                f"AND `status` = 'ACTIVE' AND `source_key` IN ({placeholders})",
                (self.tenant, *batch),
            )
            total += cursor.rowcount
        for offset in range(0, len(removed["batches"]), 500):
            batch = removed["batches"][offset:offset + 500]
            placeholders = ", ".join(["%s"] * len(batch))
            cursor.execute(
                "UPDATE `qms_production_batch` AS batch "
                "JOIN `qms_work_order` AS work_order "
                "ON work_order.`id` = batch.`work_order_id` "
                "AND work_order.`tenant_code` = batch.`tenant_code` "
                "SET batch.`status` = 'INACTIVE', batch.`updated_at` = CURRENT_TIMESTAMP(6) "
                "WHERE batch.`tenant_code` = %s AND work_order.`source_system` = 'ERP_EXCEL' "
                f"AND batch.`status` = 'ACTIVE' AND batch.`batch_no` IN ({placeholders})",
                (self.tenant, *batch),
            )
            total += cursor.rowcount
        return total

    def _existing_source_tables(self, cursor) -> set[str]:
        placeholders = ", ".join(["%s"] * len(BUSINESS_SOURCE_TABLES))
        cursor.execute(
            f"""
            SELECT table_name FROM information_schema.tables
            WHERE table_schema = DATABASE() AND table_name IN ({placeholders})
            """,
            tuple(BUSINESS_SOURCE_TABLES),
        )
        return {str(row[0]) for row in cursor.fetchall()}

    def _clear_target_tables(self, cursor) -> None:
        """Delete every tenant's rows inside the full-rebuild transaction."""
        self._assert_safe_clear(cursor)
        cursor.execute("DELETE FROM `qms_production_batch`")
        cursor.execute("DELETE FROM `qms_work_order`")
        for table_name in sorted(self._existing_source_tables(cursor)):
            cursor.execute(f"DELETE FROM {self._table_name(table_name)}")

    def _assert_safe_clear(self, cursor) -> None:
        targets = BUSINESS_SOURCE_TABLES | {"qms_work_order", "qms_production_batch"}
        names = sorted(targets)
        placeholders = ", ".join(["%s"] * len(names))
        cursor.execute(
            f"SELECT table_name, engine FROM information_schema.tables "
            f"WHERE table_schema = DATABASE() AND table_name IN ({placeholders})",
            tuple(names),
        )
        unsafe = [name for name, engine in cursor.fetchall() if str(engine).upper() != "INNODB"]
        if unsafe:
            raise SyncError("目标表不是 InnoDB，无法保证初始化失败后回滚：" + ", ".join(unsafe))
        cursor.execute(
            f"SELECT DISTINCT CONCAT(table_schema, '.', table_name) FROM information_schema.key_column_usage "
            f"WHERE referenced_table_schema = DATABASE() "
            f"AND referenced_table_name IN ({placeholders}) "
            f"AND NOT (table_schema = DATABASE() AND table_name IN ({placeholders}))",
            tuple(names) * 2,
        )
        dependents = [name for (name,) in cursor.fetchall()]
        if dependents:
            raise SyncError("有范围外的表引用目标表，初始化可能级联删除：" + ", ".join(dependents))

    def _reconcile_customer_order_latest(self, cursor) -> int:
        """Overwrite the original row with the latest row for each order and material."""
        cursor.execute(
            "SELECT `id`, `source_key`, `source_file`, `source_row_no`, `status`, "
            "`erp_order_no`, `erp_internal_product_no`, `created_at` "
            "FROM `qms_customer_order` WHERE `tenant_code` = %s",
            (self.tenant,),
        )
        groups: Dict[Tuple[str, str], List[Tuple[Any, ...]]] = {}
        for row in cursor.fetchall():
            key = tuple(as_text(value).strip() for value in row[5:7])
            if all(key):
                groups.setdefault(key, []).append(row)

        def source_date(row: Tuple[Any, ...]) -> date:
            created = row[7]
            if isinstance(created, str):
                created = datetime.fromisoformat(created)
            year = created.year if isinstance(created, (date, datetime)) else date.today().year
            for part in reversed(str(row[2]).replace("\\", "/").split("/")[:-1]):
                full = re.fullmatch(r"(20\d{2})-(\d{1,2})-(\d{1,2})", part)
                short = re.fullmatch(r"(\d{1,2})-(\d{1,2})", part)
                try:
                    if full:
                        return date(*(int(value) for value in full.groups()))
                    if short:
                        return date(year, *(int(value) for value in short.groups()))
                except ValueError:
                    continue
            return date.min

        changed = 0
        copy_columns: Optional[List[str]] = None
        for rows in groups.values():
            current_rows = [row for row in rows if row[4] != "INACTIVE"]
            candidates = current_rows or rows
            latest = max(candidates, key=lambda row: (
                source_date(row), str(row[7]), int(row[3]), str(row[1]),
            ))
            original = min(rows, key=lambda row: (str(row[7]), str(row[0])))
            status = "ACTIVE" if current_rows else "INACTIVE"
            if len(rows) > 1:
                if copy_columns is None:
                    copy_columns = [column for column in self._read_table_columns(
                        cursor, "qms_customer_order",
                    ) if column not in {
                        "id", "tenant_code", "source_key", "status", "created_at", "updated_at",
                    }]
                if original is not latest:
                    assignments = ", ".join(
                        f"original.`{column.replace('`', '``')}` = latest.`{column.replace('`', '``')}`"
                        for column in copy_columns
                    )
                    cursor.execute(
                        "UPDATE `qms_customer_order` AS original "
                        "JOIN `qms_customer_order` AS latest ON latest.`id` = %s "
                        f"SET {assignments}, original.`updated_at` = CURRENT_TIMESTAMP(6) "
                        "WHERE original.`tenant_code` = %s AND original.`id` = %s "
                        "AND latest.`tenant_code` = %s",
                        (latest[0], self.tenant, original[0], self.tenant),
                    )
                duplicates = [row[0] for row in rows if row is not original]
                for offset in range(0, len(duplicates), 500):
                    batch = duplicates[offset:offset + 500]
                    placeholders = ", ".join(["%s"] * len(batch))
                    cursor.execute(
                        f"DELETE FROM `qms_customer_order` WHERE `tenant_code` = %s "
                        f"AND `id` IN ({placeholders})",
                        (self.tenant, *batch),
                    )
                    changed += cursor.rowcount
            if original[1] != latest[1] or original[4] != status:
                cursor.execute(
                    "UPDATE `qms_customer_order` SET `source_key` = %s, `status` = %s, "
                    "`updated_at` = CURRENT_TIMESTAMP(6) "
                    "WHERE `tenant_code` = %s AND `id` = %s",
                    (latest[1], status, self.tenant, original[0]),
                )
                if len(rows) == 1:
                    changed += cursor.rowcount
        return changed

    def _source_records_for_file(
        self, cursor, table_name: str, relative_file: str, absolute_file: str,
    ) -> Dict[str, Tuple[str, str]]:
        """Find earlier rows for this file without reading another tenant's data."""
        cursor.execute(
            f"SELECT source_key, source_file, row_hash FROM {self._table_name(table_name)} "
            "WHERE tenant_code = %s AND source_file IN (%s, %s)",
            (self.tenant, relative_file, absolute_file),
        )
        return {str(key): (str(source_file), str(row_hash))
                for key, source_file, row_hash in cursor.fetchall()}

    def _reconcile_source_snapshot(
        self, cursor, source_keys_by_table: Mapping[str, Sequence[str]], existing_tables: set[str],
    ) -> int:
        """Soft-delete only after every source worksheet was read successfully."""
        deactivated = 0
        for table_name, source_keys in source_keys_by_table.items():
            table = self._table_name(table_name)
            placeholders = ", ".join(["%s"] * len(source_keys))
            cursor.execute(
                f"""
                UPDATE {table}
                SET status = 'INACTIVE', updated_at = CURRENT_TIMESTAMP(6)
                WHERE tenant_code = %s AND status = 'ACTIVE' AND source_key NOT IN ({placeholders})
                """,
                (self.tenant, *source_keys),
            )
            deactivated += cursor.rowcount
        for table_name in existing_tables - set(source_keys_by_table):
            table = self._table_name(table_name)
            cursor.execute(
                f"""
                UPDATE {table}
                SET status = 'INACTIVE', updated_at = CURRENT_TIMESTAMP(6)
                WHERE tenant_code = %s AND status = 'ACTIVE'
                """,
                (self.tenant,),
            )
            deactivated += cursor.rowcount
        return deactivated

    def test_connection(self) -> None:
        connection = self._connect()
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT count(*) FROM qms_work_order")
                cursor.fetchone()
                cursor.execute("SHOW GRANTS")
                grants = " ".join(str(row) for row in cursor.fetchall()).upper()
                if "ALL PRIVILEGES" not in grants and "CREATE" not in grants:
                    raise SyncError("数据库账号没有创建 ERP 业务表的 MySQL CREATE 权限。")
            connection.rollback()
        except MySQLError as exc:
            raise SyncError(
                "数据库已连接，但无法读取 QMS 工单表。请确认 MySQL 账号权限、表结构和库名。\n"
                f"{exc}"
            ) from exc
        finally:
            connection.close()

    def synchronize(
        self,
        changed: Sequence[Tuple[str, Dict[str, Any]]],
        source_keys: Sequence[str],
        deactivate_missing: bool,
        callback: Callable[[str], None],
    ) -> int:
        """Compatibility entry point for callers syncing only mapped work orders."""
        connection = self._connect()
        try:
            with connection.cursor() as cursor:
                total = len(changed)
                for index, (_, payload) in enumerate(changed, start=1):
                    work_order_id = self._upsert_work_order(cursor, payload)
                    self._upsert_batch(cursor, payload, work_order_id)
                    if index == total or index % 100 == 0:
                        callback(f"已直接写入 MySQL {index:,}/{total:,} 条变更…")
                deactivated = 0
                if deactivate_missing:
                    callback("正在对照完整数据源，停用 MySQL 中已从 ERP 删除的生产指令…")
                    placeholders = ", ".join(["%s"] * len(source_keys))
                    if source_keys:
                        cursor.execute(
                            f"""
                            UPDATE qms_work_order
                            SET status = 'INACTIVE', updated_at = CURRENT_TIMESTAMP(6)
                            WHERE tenant_code = %s
                              AND source_system = 'ERP_EXCEL'
                              AND source_key LIKE %s
                              AND status = 'ACTIVE'
                              AND source_key NOT IN ({placeholders})
                            """,
                            (self.tenant, f"{SOURCE_KEY_PREFIX}%", *source_keys),
                        )
                        deactivated = cursor.rowcount
                connection.commit()
            return deactivated
        except MySQLError as exc:
            connection.rollback()
            raise SyncError(f"QMS MySQL 数据库写入失败，整批事务已回滚：{exc}") from exc
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def _upsert_work_order(
        self, cursor, payload: Mapping[str, Any], *, ensure_schema: bool = True,
    ) -> str:
        mapped_columns = [column for column, _ in WORK_ORDER_DB_FIELDS]
        raw_erp_fields = payload.get("erpFields", {})
        if not isinstance(raw_erp_fields, Mapping):
            raise SyncError("生产指示资料的 ERP 字段格式无效。")
        fields = payload.get("erpFieldDefinitions", {})
        if not isinstance(fields, Mapping) or set(raw_erp_fields) != set(fields):
            raise SyncError("生产指示资料的 ERP 字段值与字段定义不一致。")
        if ensure_schema:
            self._ensure_erp_columns(cursor, "qms_work_order", fields)
        erp_columns = sorted(fields)
        columns = [
            "id", "tenant_code", "work_order_no", *mapped_columns, *erp_columns,
            "released_at", "completed_quantity", "source_system", "source_key", "source_version",
            "source_payload_hash", "status", "quality_status", "created_at", "updated_at",
        ]
        quoted_columns = [
            self._parameterized_column_name(column) if column.startswith(ERP_FIELD_PREFIX) else f"`{column}`"
            for column in columns
        ]
        update_columns = [
            "`status` = IF(`source_key` LIKE 'ERP-EXCEL:%%', 'ACTIVE', `status`)",
            *(f"`{column}` = VALUES(`{column}`)" for column in mapped_columns),
            *(
                f"{self._parameterized_column_name(column)} = VALUES("
                f"{self._parameterized_column_name(column)})"
                for column in erp_columns
            ),
            "`released_at` = COALESCE(VALUES(`released_at`), `released_at`, CURRENT_DATE())",
            "`source_system` = VALUES(`source_system`)",
            "`source_key` = VALUES(`source_key`)",
            "`source_version` = VALUES(`source_version`)",
            "`source_payload_hash` = VALUES(`source_payload_hash`)",
            "`updated_at` = CURRENT_TIMESTAMP(6)",
        ]
        placeholders = ", ".join(["%s"] * (len(columns) - 2) + ["CURRENT_TIMESTAMP(6)", "CURRENT_TIMESTAMP(6)"])
        statement = f"""
            INSERT INTO `qms_work_order` ({", ".join(quoted_columns)})
            VALUES ({placeholders})
            ON DUPLICATE KEY UPDATE
                {", ".join(update_columns)}
        """
        values: List[Any] = [
            str(uuid.uuid4()), self.tenant, payload["workOrderNo"],
            *(payload.get(field) for _, field in WORK_ORDER_DB_FIELDS),
            *(raw_erp_fields.get(column) for column in erp_columns),
            payload.get("releasedAt"), 0, "ERP_EXCEL", payload["sourceKey"], payload.get("sourceVersion"),
            payload_hash(payload), "ACTIVE", "UNASSESSED",
        ]
        cursor.execute(statement, values)
        cursor.execute(
            "SELECT `id` FROM `qms_work_order` WHERE `tenant_code` = %s AND `work_order_no` = %s",
            (self.tenant, payload["workOrderNo"]),
        )
        row = cursor.fetchone()
        if not row:
            raise SyncError(f"生产指令号 {payload['workOrderNo']} 写入后未返回 QMS 工单标识。")
        return str(row[0])

    def _upsert_batch(self, cursor, payload: Mapping[str, Any], work_order_id: str) -> None:
        batch_no = as_text(payload.get("batchNo"))
        if not batch_no:
            return
        cursor.execute(
            """
            INSERT INTO `qms_production_batch` (
                `id`, `tenant_code`, `work_order_id`, `batch_no`, `planned_quantity`, `status`, `created_at`, `updated_at`
            ) VALUES (%s, %s, %s, %s, %s, 'ACTIVE', CURRENT_TIMESTAMP(6), CURRENT_TIMESTAMP(6))
            ON DUPLICATE KEY UPDATE
                `work_order_id` = VALUES(`work_order_id`),
                `planned_quantity` = VALUES(`planned_quantity`),
                `status` = 'ACTIVE',
                `updated_at` = CURRENT_TIMESTAMP(6)
            """,
            (str(uuid.uuid4()), self.tenant, work_order_id, batch_no, payload["plannedQuantity"]),
        )


class QmsGatewayClient:
    def __init__(self, config: Mapping[str, Any]):
        base_url = str(config.get("qms_base_url", "")).strip().rstrip("/")
        token = str(config.get("gateway_token", ""))
        tenant = str(config.get("tenant_code", "")).strip()
        if not base_url.startswith(("http://", "https://")):
            raise SyncError("QMS 地址必须以 http:// 或 https:// 开头。")
        if not token:
            raise SyncError("请填写 QMS 网关令牌。")
        if not tenant:
            raise SyncError("请填写 QMS 租户编码。")
        self.base_url = base_url
        self.token = token
        self.tenant = tenant
        self.timeout = int(config.get("request_timeout_seconds", 30))

    def _request(self, path: str, body: Mapping[str, Any], accepted_statuses: Sequence[int] = (200, 201)) -> Dict[str, Any]:
        encoded = json.dumps(body, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        request = urllib.request.Request(
            self.base_url + path,
            data=encoded,
            method="POST",
            headers={
                "Content-Type": "application/json; charset=utf-8",
                "Accept": "application/json",
                "X-Gateway-Token": self.token,
                "X-Tenant-Code": self.tenant,
                "X-QMS-Actor": "erp-excel-sync",
            },
        )
        last_error: Optional[BaseException] = None
        for attempt in range(3):
            try:
                with urllib.request.urlopen(request, timeout=self.timeout) as response:
                    response_body = response.read().decode("utf-8", errors="replace")
                    if response.status not in accepted_statuses:
                        raise SyncError(f"QMS 返回 HTTP {response.status}：{response_body[:500]}")
                    return json.loads(response_body) if response_body.strip() else {}
            except urllib.error.HTTPError as exc:
                detail = exc.read().decode("utf-8", errors="replace")
                if 400 <= exc.code < 500 and exc.code != 429:
                    if exc.code == 404 and path == SNAPSHOT_API_PATH:
                        raise SyncError("当前 QMS 后端未部署快照停用接口，无法执行软删除。请先部署本工具配套的 QMS 后端更新。") from exc
                    raise SyncError(f"QMS 拒绝请求（HTTP {exc.code}）：{detail[:500]}") from exc
                last_error = exc
            except (urllib.error.URLError, TimeoutError, OSError) as exc:
                last_error = exc
            if attempt < 2:
                threading.Event().wait(1.5 * (attempt + 1))
        raise SyncError(f"无法连接 QMS：{last_error}") from last_error

    def upsert_work_order(self, payload: Mapping[str, Any]) -> None:
        self._request(API_PATH, payload)

    def reconcile_snapshot(self, source_keys: Sequence[str]) -> int:
        response = self._request(
            SNAPSHOT_API_PATH,
            {"sourceKeyPrefix": SOURCE_KEY_PREFIX, "sourceKeys": list(source_keys)},
        )
        data = response.get("data", response)
        if isinstance(data, dict):
            return int(data.get("deactivated", 0))
        return 0

    def test_connection(self) -> None:
        request = urllib.request.Request(self.base_url + "/actuator/health", headers={"Accept": "application/json"})
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                if response.status != 200:
                    raise SyncError(f"QMS 健康检查返回 HTTP {response.status}。")
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            raise SyncError(f"无法连接 QMS：{exc}") from exc


def synchronize_database_directory(
    config: Mapping[str, Any], dry_run: bool, callback: Callable[[str], None], *, initialize: bool = False,
) -> SyncSummary:
    """Commit one workbook at a time and resume after the last committed file."""
    if initialize and bool(config.get("skip_initialization", False)):
        raise SyncError("清空并重新初始化需要选择初始化数据目录，不能勾选“跳过初始化”。")
    loaded_state = {} if initialize else load_state()
    if not initialize and not dry_run and loaded_state.get(SOURCE_IDENTITY_VERSION_STATE_KEY) != "4":
        raise SyncError("来源键规则已更新；请先使用“清空并重新初始化”重建数据和断点。")
    previous = loaded_state
    next_state: Dict[str, str] = dict(previous)
    scan_groups, _ = build_source_scan_plan(config, previous, force_all=initialize)
    initialization, incremental, _ = configured_source_directories(config)
    source_description = f"初始化={initialization or '已跳过'}；增量={incremental or '未配置'}"
    stats = SourceScanStats()
    added = updated = unchanged = written_raw = written_work_orders = deactivated = 0
    work_order_hashes: Dict[str, str] = {}
    work_order_sources: Dict[str, str] = {}
    source_tables: set[str] = set()
    customer_order_touched = False
    customer_order_preexisting = False
    client = None if dry_run or not scan_groups else QmsDatabaseClient(config)

    def reconcile_customer_orders() -> int:
        nonlocal client
        if client is None:
            client = QmsDatabaseClient(config)
        connection = client._connect()
        try:
            try:
                with connection.cursor() as cursor:
                    changed = (
                        client._reconcile_customer_order_latest(cursor)
                        if "qms_customer_order" in client._existing_source_tables(cursor) else 0
                    )
                connection.commit()
                return changed
            except Exception:
                connection.rollback()
                raise
        finally:
            connection.close()

    if not scan_groups:
        if not dry_run and previous.get(CUSTOMER_ORDER_RECONCILE_STATE_KEY) != CUSTOMER_ORDER_RECONCILE_VERSION:
            changed = reconcile_customer_orders()
            previous[CUSTOMER_ORDER_RECONCILE_STATE_KEY] = CUSTOMER_ORDER_RECONCILE_VERSION
            save_state(previous)
            callback(f"已整理存量客户订单：合并或更新 {changed:,} 条记录。")
        elif not dry_run and progress_directory().is_dir():
            save_state(previous)
        if not dry_run:
            clear_file_progress()
        callback("未发现需要处理的新增或变更 Excel 文件。")
        return SyncSummary(
            source_file=source_description, rows_read=0, added=0, updated=0,
            unchanged=0, deactivated=0, dry_run=dry_run, source_files=0,
            raw_records=0, work_orders=0, source_tables=0, raw_written=0,
            work_orders_written=0,
        )

    def process_file(group: SourceScanGroup, path: Path, cursor) -> Tuple[Dict[str, str], Dict[str, Any]]:
        nonlocal added, updated, unchanged, written_raw, written_work_orders
        nonlocal customer_order_preexisting
        pending_table: Optional[str] = None
        pending_records: List[RawSourceRecord] = []
        file_state: Dict[str, str] = {}
        raw_keys: Dict[str, set[str]] = {}
        seen_raw_keys: set[Tuple[str, str]] = set()
        order_keys: set[str] = set()
        batch_keys: set[str] = set()
        relative_file = path.relative_to(group.directory).as_posix()
        if cursor is not None:
            customer_order_preexisting |= "qms_customer_order" in client._existing_source_tables(cursor)

        def flush_raw_records() -> None:
            nonlocal pending_table, pending_records, written_raw
            if cursor is None or not pending_records:
                return
            assert client is not None and pending_table is not None
            if initialize:
                client._upsert_source_records(cursor, pending_table, pending_records, ensure_schema=False)
            else:
                client._upsert_source_records(cursor, pending_table, pending_records)
            written_raw += len(pending_records)
            if written_raw % 500 == 0:
                callback(f"已写入或核验 {written_raw:,} 条 ERP 源记录…")
            pending_table = None
            pending_records = []

        for raw, payload in iter_all_source_records(
            config, callback, stats, source_directory=group.directory, selected_files=(path,),
        ):
            if raw.source_table:
                duplicate = (raw.source_table, raw.source_key)
                if duplicate in seen_raw_keys:
                    raise SyncError(
                        f"同一 Excel 中有无法区分的重复明细：{relative_file} / {raw.sheet_name} "
                        f"第 {raw.source_row_no} 行；请提供明细编号。"
                    )
                seen_raw_keys.add(duplicate)
                source_tables.add(raw.source_table)
                raw_keys.setdefault(raw.source_table, set()).add(raw.source_key)
            raw_state_key = f"raw:{raw.source_key}"
            previous_hash = previous.get(raw_state_key)
            file_state[raw_state_key] = raw.row_hash
            if previous_hash is None:
                added += 1
            elif previous_hash != raw.row_hash:
                updated += 1
            else:
                unchanged += 1
            # The database remains authoritative if this PC's cache is lost.
            if cursor is not None and raw.source_table:
                if pending_table is not None and pending_table != raw.source_table:
                    flush_raw_records()
                pending_table = raw.source_table
                pending_records.append(raw)
                if len(pending_records) >= 500:
                    flush_raw_records()

            if payload is not None:
                source_key = str(payload["sourceKey"])
                value_hash = payload_hash(payload)
                duplicate_hash = work_order_hashes.get(source_key)
                if duplicate_hash is not None and duplicate_hash != value_hash \
                        and work_order_sources[source_key] == raw.source_file:
                    raise SyncError(
                        f"生产指令号重复且内容不一致：{payload['workOrderNo']}"
                        f"（来源 {raw.source_file} / {raw.sheet_name}）"
                    )
                work_order_hashes[source_key] = value_hash
                work_order_sources[source_key] = raw.source_file
                file_state[f"work-order:{source_key}"] = value_hash
                order_keys.add(source_key)
                batch_no = as_text(payload.get("batchNo"))
                if batch_no:
                    batch_keys.add(batch_no)
                if cursor is not None:
                    assert client is not None
                    if initialize:
                        work_order_id = client._upsert_work_order(cursor, payload, ensure_schema=False)
                    else:
                        work_order_id = client._upsert_work_order(cursor, payload)
                    client._upsert_batch(cursor, payload, work_order_id)
                    written_work_orders += 1
                    if written_work_orders % 100 == 0:
                        callback(f"已写入或核验 {written_work_orders:,} 条 QMS 工单…")

            if stats.raw_records % 5000 == 0:
                callback(f"已读取 {stats.raw_records:,} 条 ERP 原始记录…")
        flush_raw_records()
        membership = {
            "raw": {table: sorted(keys) for table, keys in raw_keys.items()},
            "work_orders": sorted(order_keys),
            "batches": sorted(batch_keys),
        }
        return file_state, membership

    if initialize and not dry_run:
        assert client is not None
        callback("正在预检全部 Excel，并准备数据库字段；预检通过后才清空目标表。")
        fields_by_table: Dict[str, Dict[str, ErpFieldDefinition]] = {}
        checked_files: Dict[str, str] = {}
        for group in scan_groups:
            for path in group.files:
                checked_files[str(path)] = source_file_checkpoint(path)
                for raw, payload in iter_all_source_records(
                    config, callback, SourceScanStats(),
                    source_directory=group.directory, selected_files=(path,),
                ):
                    if raw.source_table:
                        fields_by_table.setdefault(raw.source_table, {}).update(raw.field_definitions)
                    if payload is not None:
                        fields_by_table.setdefault("qms_work_order", {}).update(payload["erpFieldDefinitions"])
                if source_file_checkpoint(path) != checked_files[str(path)]:
                    raise SyncError(f"源文件预检期间发生覆盖：{path}；请重试。")
        connection = client._connect()
        try:
            with connection.cursor() as cursor:
                for table_name, fields in fields_by_table.items():
                    if table_name == "qms_work_order":
                        client._ensure_erp_columns(cursor, table_name, fields)
                    else:
                        client._ensure_source_table_schema(cursor, table_name, fields)
            connection.commit()
            with connection.cursor() as cursor:
                if any(source_file_checkpoint(path) != checked_files[str(path)]
                       for group in scan_groups for path in group.files):
                    raise SyncError("源文件在预检后发生变化；数据库未清空，请重试。")
                client._clear_target_tables(cursor)
                for group in scan_groups:
                    callback(f"开始处理{'初始化' if group.role == 'initialization' else '增量'}数据目录：{group.directory}")
                    for path in group.files:
                        file_key = source_file_state_key(group.role, group.directory, path)
                        file_state, membership = process_file(group, path, cursor)
                        if source_file_checkpoint(path) != checked_files[str(path)]:
                            raise SyncError(f"源文件处理期间发生覆盖：{path}；数据库清理和导入已回滚。")
                        file_state[file_key] = checked_files[str(path)]
                        file_state[file_membership_state_key(file_key)] = json.dumps(
                            membership, ensure_ascii=False, separators=(",", ":"),
                        )
                        next_state.update(file_state)
                        customer_order_touched |= "qms_customer_order" in membership["raw"]
                if customer_order_touched:
                    client._reconcile_customer_order_latest(cursor)
            connection.commit()
        except Exception as exc:
            connection.rollback()
            if isinstance(exc, MySQLError):
                raise SyncError(f"重新初始化失败，数据库清理和导入已回滚：{exc}") from exc
            raise
        finally:
            connection.close()
        next_state[SOURCE_IDENTITY_VERSION_STATE_KEY] = "4"
        next_state[CUSTOMER_ORDER_RECONCILE_STATE_KEY] = CUSTOMER_ORDER_RECONCILE_VERSION

    for group in (() if initialize and not dry_run else scan_groups):
        label = "初始化数据" if group.role == "initialization" else "增量数据"
        callback(f"开始处理{label}目录：{group.directory}")
        for path in group.files:
            file_key = source_file_state_key(group.role, group.directory, path)
            relative_file = path.relative_to(group.directory).as_posix()
            try:
                checkpoint = source_file_checkpoint(path)
            except OSError as exc:
                raise SyncError(f"无法读取源文件 {relative_file}：{exc}") from exc
            if dry_run:
                process_file(group, path, None)
                if source_file_checkpoint(path) != checkpoint:
                    raise SyncError(f"源文件处理期间发生覆盖：{relative_file}；请重试。")
                continue

            assert client is not None
            connection = client._connect()
            try:
                try:
                    with connection.cursor() as cursor:
                        file_state, membership = process_file(group, path, cursor)
                        if source_file_checkpoint(path) != checkpoint:
                            raise SyncError(f"源文件处理期间发生覆盖：{relative_file}；请重试。")
                        removed = removed_file_membership(next_state, file_key, membership)
                        deactivated_for_file = client._deactivate_removed_file_records(cursor, removed)
                        customer_order_in_file = (
                            "qms_customer_order" in membership["raw"]
                            or "qms_customer_order" in removed["raw"]
                        )
                        reconciled_for_file = (
                            client._reconcile_customer_order_latest(cursor)
                            if customer_order_in_file else 0
                        )
                    connection.commit()
                except Exception as exc:
                    try:
                        connection.rollback()
                    except Exception:
                        # A disconnected MySQL socket cannot be rolled back locally.
                        pass
                    if isinstance(exc, MySQLError):
                        raise SyncError(
                            f"处理 {relative_file} 时数据库连接中断或写入失败；"
                            f"已完成文件保留进度，下次重试当前文件。原始错误：{exc}"
                        ) from exc
                    raise
            finally:
                try:
                    connection.close()
                except Exception:
                    pass
            file_state[file_key] = checkpoint
            file_state[SOURCE_IDENTITY_VERSION_STATE_KEY] = "4"
            if group.role == "initialization" and any(
                planned.role == "incremental" for planned in scan_groups
            ):
                file_state[BASELINE_REPLAY_STATE_KEY] = "1"
            file_state[file_membership_state_key(file_key)] = json.dumps(
                membership, ensure_ascii=False, separators=(",", ":"),
            )
            try:
                save_file_progress(file_key, file_state)
            except OSError as exc:
                raise SyncError(
                    f"{relative_file} 已提交到数据库，但本机断点保存失败；请修复磁盘权限后重新同步。"
                ) from exc
            next_state.update(file_state)
            deactivated += deactivated_for_file
            customer_order_touched |= customer_order_in_file
            if customer_order_in_file:
                callback(f"已合并或更新 {reconciled_for_file:,} 条客户订单记录。")
            callback(f"已提交并保存断点：{relative_file}。")

    work_order_added = work_order_updated = 0
    for source_key, value_hash in work_order_hashes.items():
        old_hash = previous.get(f"work-order:{source_key}", previous.get(source_key))
        if old_hash is None:
            work_order_added += 1
        elif old_hash != value_hash:
            work_order_updated += 1
    callback(f"变更分析（与本机上次扫描相比）：新增 {added:,}，修改 {updated:,}，未变 {unchanged:,}。")
    callback(f"工单映射：{stats.work_order_records:,} 条，新增 {work_order_added:,}，修改 {work_order_updated:,}。")
    if dry_run:
        callback("预演模式：已遍历全部 Excel 文件和工作表，未向 QMS 写入任何数据。")
    else:
        if not initialize and previous.get(CUSTOMER_ORDER_RECONCILE_STATE_KEY) != CUSTOMER_ORDER_RECONCILE_VERSION:
            changed = reconcile_customer_orders() if customer_order_preexisting and not customer_order_touched else 0
            next_state[CUSTOMER_ORDER_RECONCILE_STATE_KEY] = CUSTOMER_ORDER_RECONCILE_VERSION
            if customer_order_preexisting and not customer_order_touched:
                callback(f"已整理客户订单：合并或更新 {changed:,} 条记录。")
        if any(group.role == "incremental" for group in scan_groups):
            next_state[BASELINE_REPLAY_STATE_KEY] = "0"
        try:
            save_state(next_state)
        except OSError as exc:
            raise SyncError("数据库已提交，但本机同步断点保存失败；请修复磁盘权限后重新初始化。") from exc
        clear_file_progress()
        callback("文件处理状态已保存；后续只处理新增或变更的 Excel 文件。")

    summary = SyncSummary(
        source_file=source_description, rows_read=stats.raw_records, added=added, updated=updated,
        unchanged=unchanged, deactivated=deactivated, dry_run=dry_run,
        source_files=stats.files_scanned, raw_records=stats.raw_records, work_orders=stats.work_order_records,
        source_tables=len(source_tables), raw_written=written_raw, work_orders_written=written_work_orders,
    )
    log_line(
        f"同步{'预演' if dry_run else '完成'}：{source_description}，文件={stats.files_scanned}，"
        f"工作表={stats.sheets_scanned}，源表={len(source_tables)}，原始记录={stats.raw_records}，"
        f"源记录写入/核验={written_raw}，工单={stats.work_order_records}，工单写入/核验={written_work_orders}，"
        f"新增={added}，更新={updated}，未变={unchanged}，停用={deactivated}"
    )
    return summary


def synchronize(
    config: Mapping[str, Any], dry_run: bool, callback: Optional[Callable[[str], None]] = None,
    *, initialize: bool = False,
) -> SyncSummary:
    callback = callback or (lambda message: None)
    sync_mode = str(config.get("sync_mode", "database")).strip().lower()
    if sync_mode == "database":
        return synchronize_database_directory(config, dry_run, callback, initialize=initialize)
    if sync_mode != "api":
        raise SyncError("同步方式无效。请选择“数据库直连”或“QMS 接口”。")
    raise SyncError(
        "全目录 ERP 数据归档需要“数据库直连”模式。QMS 接口当前只提供生产指示工单接口，"
        "无法安全接收目录中其他 Excel 的原始数据。"
    )


class SyncApplication(ttk.Frame):
    def __init__(self, master: tk.Tk, initial_config: Mapping[str, Any]):
        super().__init__(master, padding=16)
        self.master = master
        self.config_values = dict(initial_config)
        self.events: "queue.Queue[Tuple[str, Any]]" = queue.Queue()
        self.running = False
        self.directory_monitor: Optional[DirectoryChangeMonitor] = None
        self._monitor_generation = 0
        self._build()
        self.pack(fill="both", expand=True)
        self.after(100, self._drain_events)
        self._restart_monitor()

    def _build(self) -> None:
        self.master.title(APP_NAME)
        self.master.minsize(800, 680)
        self.columnconfigure(1, weight=1)

        initialization, incremental, skip_initialization = configured_source_directories(self.config_values)
        self.initialization_var = tk.StringVar(value=initialization)
        self.incremental_var = tk.StringVar(value=incremental)
        self.skip_initialization_var = tk.BooleanVar(value=skip_initialization)
        self.auto_sync_var = tk.BooleanVar(value=bool(self.config_values.get("auto_sync_enabled", False)))
        self.auto_interval_var = tk.StringVar(
            value=str(self.config_values.get("auto_sync_interval_minutes", AUTO_SYNC_DEFAULT_INTERVAL_MINUTES))
        )
        self.status_var = tk.StringVar(value="数据库连接信息请在配置文件中维护。")

        ttk.Label(self, text="初始化数据目录").grid(row=0, column=0, sticky="w", pady=(0, 8), padx=(0, 10))
        self.initialization_entry = ttk.Entry(self, textvariable=self.initialization_var)
        self.initialization_entry.grid(row=0, column=1, sticky="ew", pady=(0, 8))
        self.initialization_button = ttk.Button(self, text="选择…", command=self._choose_initialization)
        self.initialization_button.grid(row=0, column=2, padx=(8, 0), pady=(0, 8))

        ttk.Label(self, text="增量同步目录").grid(row=1, column=0, sticky="w", pady=(0, 8), padx=(0, 10))
        self.incremental_entry = ttk.Entry(self, textvariable=self.incremental_var)
        self.incremental_entry.grid(row=1, column=1, sticky="ew", pady=(0, 8))
        self.incremental_button = ttk.Button(self, text="选择…", command=self._choose_incremental)
        self.incremental_button.grid(row=1, column=2, padx=(8, 0), pady=(0, 8))

        self.skip_initialization_button = ttk.Checkbutton(
            self, text="跳过初始化（只处理增量同步目录）",
            variable=self.skip_initialization_var,
        )
        self.skip_initialization_button.grid(row=2, column=0, columnspan=3, sticky="w", pady=(0, 8))

        self.auto_sync_button = ttk.Checkbutton(
            self, text="启用自动监控", variable=self.auto_sync_var, command=self._auto_monitor_changed,
        )
        self.auto_sync_button.grid(row=3, column=0, sticky="w", pady=(0, 8))
        monitor_options = ttk.Frame(self)
        monitor_options.grid(row=3, column=1, columnspan=2, sticky="w", pady=(0, 8))
        ttk.Label(monitor_options, text="检查间隔（分钟）").pack(side="left")
        self.auto_interval_input = ttk.Spinbox(
            monitor_options, from_=AUTO_SYNC_MIN_INTERVAL_MINUTES,
            to=AUTO_SYNC_MAX_INTERVAL_MINUTES, width=7, textvariable=self.auto_interval_var,
        )
        self.auto_interval_input.pack(side="left", padx=(8, 0))

        ttk.Label(
            self, foreground="#5a5a5a",
            text=f"数据库连接等高级配置请编辑：{config_path()}",
        ).grid(row=4, column=0, columnspan=3, sticky="w", pady=(0, 12))

        controls = ttk.Frame(self)
        controls.grid(row=5, column=0, columnspan=3, sticky="ew", pady=(0, 10))
        self.save_button = ttk.Button(controls, text="保存配置", command=self._save_configuration)
        self.test_button = ttk.Button(controls, text="测试数据库连接", command=self._test_connection)
        self.sync_button = ttk.Button(controls, text="开始同步", command=self._run_sync)
        self.initialize_button = ttk.Button(
            controls, text="清空并重新初始化", command=lambda: self._run_sync(initialize=True),
        )
        for button in (self.save_button, self.test_button, self.sync_button, self.initialize_button):
            button.pack(side="left", padx=(0, 8))

        self.progress = ttk.Progressbar(self, mode="indeterminate")
        self.progress.grid(row=6, column=0, columnspan=3, sticky="ew", pady=(0, 8))
        ttk.Label(self, textvariable=self.status_var).grid(row=7, column=0, columnspan=3, sticky="w", pady=(0, 6))
        self.log = tk.Text(self, height=20, wrap="word", state="disabled")
        self.log.grid(row=8, column=0, columnspan=3, sticky="nsew")
        self.rowconfigure(8, weight=1)

    def _choose_initialization(self) -> None:
        selected = filedialog.askdirectory(
            title="选择初始化全量数据目录", initialdir=self.initialization_var.get() or None,
        )
        if selected:
            self.initialization_var.set(selected)

    def _choose_incremental(self) -> None:
        selected = filedialog.askdirectory(
            title="选择增量同步根目录", initialdir=self.incremental_var.get() or None,
        )
        if selected:
            self.incremental_var.set(selected)

    def _current_config(self) -> Dict[str, Any]:
        # Reload from disk before every operation so a user can change DB
        # details in qms_erp_sync_config.json without restarting the desktop app.
        base_config = load_config()
        config = build_desktop_config(
            base_config,
            initialization_directory=self.initialization_var.get(),
            incremental_directory=self.incremental_var.get(),
            skip_initialization=self.skip_initialization_var.get(),
            auto_sync_enabled=self.auto_sync_var.get(),
            auto_sync_interval_minutes=self.auto_interval_var.get(),
        )
        self.config_values = dict(config)
        return config

    def _save_configuration(self) -> None:
        try:
            config = self._current_config()
            initialization, incremental, skip_initialization = configured_source_directories(config)
            if not skip_initialization and not initialization:
                raise SyncError("请选择初始化数据目录，或勾选“跳过初始化”。")
            if skip_initialization and not incremental:
                raise SyncError("已勾选“跳过初始化”，请选择增量同步目录。")
            if config["auto_sync_enabled"] and not incremental:
                raise SyncError("启用自动监控前请选择增量同步目录。")
            if config["auto_sync_enabled"] and not config.get("last_source_fingerprint"):
                config["last_source_fingerprint"] = directory_fingerprint(Path(incremental))
            save_config(config)
            self.config_values = dict(config)
            self._restart_monitor(config)
            self._write_log(f"配置已保存：{config_path()}")
            self.status_var.set("配置已保存。")
        except Exception as exc:
            messagebox.showerror(APP_NAME, str(exc))

    def _test_connection(self) -> None:
        try:
            config = self._current_config()
            QmsDatabaseClient(config).test_connection()
            self.status_var.set("QMS MySQL 数据库连接和表权限正常。")
            self._write_log("QMS MySQL 数据库连接正常。")
        except Exception as exc:
            messagebox.showerror("连接失败", str(exc))

    def _set_running(self, value: bool) -> None:
        self.running = value
        state = "disabled" if value else "normal"
        for button in (
            self.initialization_entry, self.initialization_button,
            self.incremental_entry, self.incremental_button, self.skip_initialization_button,
            self.auto_sync_button, self.auto_interval_input,
            self.save_button, self.test_button, self.sync_button, self.initialize_button,
        ):
            button.configure(state=state)
        if value:
            self.progress.start(12)
        else:
            self.progress.stop()

    def _auto_monitor_changed(self) -> None:
        try:
            config = self._current_config()
            self._restart_monitor(config)
            status = "自动监控已启用；点击“保存配置”后下次打开也会生效。" if config["auto_sync_enabled"] else "自动监控已关闭。"
            self.status_var.set(status)
            self._write_log(status)
        except Exception as exc:
            messagebox.showerror(APP_NAME, str(exc))

    def _restart_monitor(self, config: Optional[Mapping[str, Any]] = None) -> None:
        self._monitor_generation += 1
        config = dict(config or self._current_config())
        if not config.get("auto_sync_enabled"):
            self.directory_monitor = None
            return
        _, incremental, _ = configured_source_directories(config)
        if not incremental:
            self.directory_monitor = None
            return
        self.directory_monitor = DirectoryChangeMonitor(
            Path(incremental), str(config.get("last_source_fingerprint", "")),
        )
        generation = self._monitor_generation
        self.after(500, lambda: self._monitor_tick(generation))

    def _monitor_tick(self, generation: int) -> None:
        if generation != self._monitor_generation:
            return
        try:
            config = self._current_config()
            if not config.get("auto_sync_enabled"):
                return
            _, incremental, _ = configured_source_directories(config)
            if not incremental:
                raise SyncError("自动监控缺少增量同步目录。")
            source_directory = Path(incremental)
            if self.directory_monitor is None or self.directory_monitor.source_directory != source_directory:
                self.directory_monitor = DirectoryChangeMonitor(
                    source_directory, str(config.get("last_source_fingerprint", "")),
                )
            if not self.running and self.directory_monitor.has_changed():
                self._write_log("检测到 ERP Excel 目录变更，开始自动增量同步…")
                self._run_sync(automatic=True, source_fingerprint=self.directory_monitor.capture_sync_start())
        except Exception as exc:
            self._write_log(f"自动监控检查失败：{exc}")
            self.status_var.set("自动监控检查失败；请检查数据目录和配置文件。")
        finally:
            if generation == self._monitor_generation:
                interval_ms = normalize_auto_sync_interval(self.auto_interval_var.get()) * 60 * 1000
                self.after(interval_ms, lambda: self._monitor_tick(generation))

    def _record_successful_snapshot(self, source_fingerprint: str) -> None:
        config = self._current_config()
        config["last_source_fingerprint"] = source_fingerprint
        save_config(config)
        self.config_values = dict(config)
        if self.directory_monitor is not None:
            self.directory_monitor.mark_synchronized(source_fingerprint)

    def _run_sync(
        self, automatic: bool = False, source_fingerprint: Optional[str] = None, initialize: bool = False,
    ) -> None:
        if self.running:
            return
        try:
            config = self._current_config()
            initialization, incremental, skip_initialization = configured_source_directories(config)
            if not skip_initialization and not initialization:
                raise SyncError("请选择初始化数据目录，或勾选“跳过初始化”。")
            if skip_initialization and not incremental:
                raise SyncError("已勾选“跳过初始化”，请选择增量同步目录。")
            if initialize and skip_initialization:
                raise SyncError("请取消“跳过初始化”，再执行清空并重新初始化。")
            if source_fingerprint is None and incremental:
                source_fingerprint = directory_fingerprint(Path(incremental))
            source_fingerprint = source_fingerprint or ""
            save_config(config)
        except Exception as exc:
            self._write_log("自动同步无法启动：" + str(exc)) if automatic else messagebox.showerror(APP_NAME, str(exc))
            return
        if initialize and not messagebox.askyesno(
            "确认清空全部目标表",
            "将删除所有租户在 ERP 源数据表、qms_work_order 和 qms_production_batch 中的数据，"
            "再导入初始化及增量目录。该操作无法撤销，是否继续？",
        ):
            return
        self._set_running(True)
        self.status_var.set(("自动" if automatic else "手动") + "同步正在运行，请勿关闭窗口。")
        self._write_log("开始" + ("自动" if automatic else "手动") + "同步…")

        def worker() -> None:
            try:
                result = synchronize(
                    config, False, lambda text: self.events.put(("log", text)), initialize=initialize,
                )
                self.events.put(("done", (result, automatic, source_fingerprint)))
            except Exception as exc:
                self.events.put(("error", (str(exc), traceback.format_exc(), automatic)))

        threading.Thread(target=worker, daemon=True, name="qms-erp-sync").start()

    def _drain_events(self) -> None:
        try:
            while True:
                event, value = self.events.get_nowait()
                if event == "log":
                    self._write_log(str(value))
                    self.status_var.set(str(value))
                elif event == "done":
                    result, automatic, source_fingerprint = value
                    self._record_successful_snapshot(source_fingerprint)
                    message = (
                        f"{'自动' if automatic else '手动'}同步完成：遍历 {result.source_files:,} 个文件、"
                        f"生成/核验 {result.source_tables:,} 张源表、{result.raw_records:,} 条源记录"
                        f"（本次写入/核验 {result.raw_written:,} 条），工单映射 {result.work_orders:,} 条"
                        f"（本次写入/核验 {result.work_orders_written:,} 条）；"
                        f"新增 {result.added:,}，修改 {result.updated:,}，未变 {result.unchanged:,}。"
                    )
                    self._write_log(message)
                    self.status_var.set(message)
                    self._set_running(False)
                    if not automatic:
                        messagebox.showinfo(APP_NAME, message)
                elif event == "error":
                    message, details, automatic = value
                    self._write_log("失败：" + message)
                    log_line(details)
                    self.status_var.set("同步失败。请查看窗口日志或 logs 目录。")
                    self._set_running(False)
                    if not automatic:
                        messagebox.showerror("同步失败", message)
        except queue.Empty:
            pass
        self.after(100, self._drain_events)

    def _write_log(self, text: str) -> None:
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log.configure(state="normal")
        self.log.insert("end", f"[{timestamp}] {text}\n")
        self.log.see("end")
        self.log.configure(state="disabled")


def run_gui() -> int:
    try:
        initial = load_config()
    except SyncError as exc:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(APP_NAME, str(exc))
        return 1
    root = tk.Tk()
    try:
        ttk.Style(root).theme_use("vista")
    except tk.TclError:
        pass
    SyncApplication(root, initial)
    root.mainloop()
    return 0


def run_headless(arguments: argparse.Namespace) -> int:
    config = load_config()
    if arguments.config:
        supplied = json.loads(Path(arguments.config).read_text(encoding="utf-8"))
        config.update(supplied)
    if arguments.source_directory:
        config["source_directory"] = arguments.source_directory
        config["initialization_directory"] = arguments.source_directory
    if arguments.initialization_directory:
        config["source_directory"] = arguments.initialization_directory
        config["initialization_directory"] = arguments.initialization_directory
    if arguments.incremental_directory:
        config["incremental_directory"] = arguments.incremental_directory
    if arguments.skip_initialization:
        config["skip_initialization"] = True
    if arguments.qms_url:
        config["qms_base_url"] = arguments.qms_url
    if arguments.sync_mode:
        config["sync_mode"] = arguments.sync_mode
    try:
        result = synchronize(config, arguments.dry_run, print)
        print(json.dumps(result.__dict__, ensure_ascii=False, indent=2))
        return 0
    except Exception as exc:
        print(f"同步失败：{exc}", file=sys.stderr)
        return 1


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=APP_NAME)
    parser.add_argument("--headless", action="store_true", help="无界面运行，适合任务计划程序")
    parser.add_argument("--dry-run", action="store_true", help="只分析数据，不写入 QMS")
    parser.add_argument("--config", help="覆盖默认配置的 JSON 文件")
    parser.add_argument("--source-directory", help="兼容旧版：本次运行使用的初始化数据目录")
    parser.add_argument("--initialization-directory", help="本次运行使用的初始化全量数据目录")
    parser.add_argument("--incremental-directory", help="本次运行使用的增量同步根目录")
    parser.add_argument("--skip-initialization", action="store_true", help="跳过初始化目录，只处理增量目录")
    parser.add_argument("--qms-url", help="接口模式下本次运行使用的 QMS 服务地址")
    parser.add_argument("--sync-mode", choices=("database", "api"), help="本次运行的同步方式")
    return parser.parse_args()


def main() -> int:
    arguments = parse_arguments()
    return run_headless(arguments) if arguments.headless else run_gui()


if __name__ == "__main__":
    raise SystemExit(main())
