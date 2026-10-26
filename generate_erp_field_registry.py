"""Generate reviewed English ERP fields from workbook headers only.

Run explicitly after reviewing vocabulary changes. Runtime synchronization never
calls this generator. Longest business-term matching composes semantic names;
unknown Chinese fails closed. Literal ERP codes remain ASCII, while punctuation
becomes token boundaries. Same-table name collisions suffix *every* participant
with a stable source tag and a hash of table/file/sheet/unique-header, independent
of traversal order. The JSON records these resolutions for human review.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter
from dataclasses import asdict, replace
from pathlib import Path
from typing import List

from generate_field_mapping_data import SOURCE_DIRECTORY, iter_workbook_headers
from qms_erp_sync import (
    ErpFieldDefinition, ErpFieldRegistry, SyncError, excel_header_identity, erp_column_comment,
    canonical_source_file_name, is_work_order_sheet, legacy_database_column_name,
    load_erp_field_registry, source_table_name, unique_headers,
)


# Controlled business vocabulary. Whole phrases take precedence over individual
# terms, so familiar concepts such as purchase_order_no remain natural English.
BUSINESS_TERMS = {
    "采购单号": "purchase_order_no", "生产指令号": "production_order_no",
    "生产指令": "production_order", "制令单号": "production_order_no",
    "工单号": "work_order_no", "生产通知单号": "production_notice_no",
    "生产通知单": "production_notice", "管制卡号": "control_card_no",
    "客户料号": "customer_part_no", "厂内编号": "internal_product_no",
    "条形码": "barcode", "过数": "quantity_transfer", "收板": "board_receipt",
    "操作员": "operator", "生产停留小时": "production_dwell_hours",
    "旧厂内编号": "old_internal_product_no", "原订单编号": "original_order_no",
    "客户订单": "customer_order", "采购单": "purchase_order",
    "送货单号": "delivery_note_no", "入库单号": "receipt_no",
    "领料单号": "material_issue_no", "请购单号": "purchase_requisition_no",
    "出库单": "material_issue", "入库单": "receipt",
    "客户编号": "customer_code", "客户代号": "customer_code",
    "原料编号": "material_no", "原料名称": "material_name",
    "原物料名称": "original_material_name", "材质": "material",
    "板厚": "board_thickness", "铜箔": "copper_foil",
    "工艺": "process_technology", "成型方式": "forming_method",
    "成型要求": "forming_requirements", "结构工艺": "structure_technology",
    "税率": "tax_rate", "达成率": "achievement_rate", "不良率": "defect_rate",
    "率": "rate",
    "号码": "no", "可交": "available_delivery", "表头": "header",
    "存货": "inventory", "变更": "change", "包装": "packaging",
    "最新版": "latest_version", "量": "quantity", "型号": "model",
    "每箱数量": "quantity_per_carton", "批号": "batch_no", "调入": "transfer_in",
    "报废率": "scrap_rate", "毛利润率": "gross_margin_rate",
    "单价": "unit_price", "金额": "amount", "数量": "quantity",
    "本位币": "local_currency", "本币": "local_currency", "原币": "original_currency",
    "不含税": "tax_exclusive", "未含税": "tax_exclusive", "含税": "tax_inclusive",
    "未税": "tax_exclusive", "含时分": "with_time", "利用率": "utilization_rate",
    "投料": "material_input", "计划": "planned", "累计": "cumulative",
    "入库": "receipt", "领料": "material_issue", "还入": "returned",
    "退仓": "warehouse_return", "出库": "issue", "出货": "shipment",
    "补料": "material_replenishment", "补货": "replenishment", "补交": "additional_delivery",
    "备品": "spare", "备货": "stock_preparation", "订单": "order",
    "客户": "customer", "采购": "purchase", "物料": "material",
    "厂外": "external", "半成品仓": "semi_finished_goods_warehouse",
    "原料": "raw_material", "板材": "board_material", "板料": "board_material",
    "工作板": "panel", "成品": "finished_goods", "零品": "loose_pieces",
    "废品": "scrap", "良品": "good_units", "不良": "defect", "报废": "scrap",
    "投单": "order_input", "厂商": "supplier", "板厂": "board_supplier",
    "厂牌": "brand", "工厂": "factory", "厂内": "internal",
    "生产": "production", "工程": "engineering", "加工": "processing",
    "外包": "subcontract", "外发": "outsourcing", "代工": "contract_manufacturing",
    "销售": "sales", "财务": "finance", "业务员": "salesperson",
    "业务": "sales", "跟单员": "order_coordinator", "跟单文员": "order_clerk",
    "跟单": "order_tracking", "跟催": "expediting", "人员": "staff",
    "日期": "date", "时间": "time", "年月": "year_month", "月份": "month",
    "天数": "days", "交期": "delivery_date", "交货": "delivery",
    "送货": "delivery", "下单": "order_placed", "开单": "order_issued",
    "需求": "required", "要求": "required", "最新": "latest",
    "最后一次": "last", "第一次": "first", "最后": "last",
    "最早": "earliest", "最晚": "latest", "上次": "previous", "本次": "current",
    "目前": "current", "期初": "opening", "到期": "expiry", "有效期": "valid_until",
    "保质期": "shelf_life", "保质": "shelf_life", "过期": "expired",
    "预上线": "planned_start", "预交货": "scheduled_delivery", "预": "planned",
    "最终": "final", "周期": "cycle", "盘点": "stocktaking", "所属": "associated",
    "库存": "inventory", "结余": "balance", "安全": "safety", "最大": "maximum",
    "最小": "minimum", "代管仓": "consignment_warehouse", "仓库": "warehouse",
    "仓位": "bin", "储位": "storage_location", "存储": "storage",
    "单号": "document_no", "编号": "no", "编码": "code", "代号": "code",
    "名称": "name", "全称": "full_name", "简称": "short_name", "别名": "alias",
    "料号": "part_no", "规格": "specification", "类型": "type", "类别": "category",
    "大类": "major_category", "小类": "minor_category", "子类": "subcategory",
    "备注": "remarks", "说明": "description", "明细": "detail", "详情": "details",
    "附件": "attachments", "状态": "status", "信息": "information",
    "单位": "unit", "面积": "area", "平方数": "area", "平方": "square_meters",
    "平米数": "square_meters", "平米": "square_meters", "重量": "weight",
    "单重": "unit_weight", "层数": "layer_count", "长度": "length",
    "宽度": "width", "厚度": "thickness", "铜厚": "copper_thickness",
    "高度": "height", "长": "length", "宽": "width", "厚": "thickness",
    "板": "board", "块数": "piece_count", "张数": "sheet_count",
    "内层": "inner_layer", "屏蔽层": "shielding_layer", "导电胶": "conductive_adhesive",
    "硬度": "hardness", "用途": "usage", "阻燃": "flame_retardant",
    "环保": "environmental_compliance", "无卤素": "halogen_free",
    "连片": "array", "排版": "panelization", "拼板": "panelization",
    "合拼": "combined_panel", "套板": "panel_set", "主": "main",
    "开料": "cutting", "标准": "standard", "换算": "conversion",
    "用量": "consumption", "损耗": "loss", "总": "total", "含": "containing",
    "数": "count", "值": "value", "每": "per", "单": "single",
    "税": "tax", "汇率": "exchange_rate", "币别": "currency",
    "欠交货": "outstanding_delivery", "欠交": "outstanding_delivery",
    "欠": "outstanding", "报价": "quotation", "调价": "price_adjustment",
    "价格": "price", "价": "price", "成本": "cost", "加权": "weighted",
    "平均": "average", "耗时": "elapsed_time", "款数": "model_count",
    "款": "model", "班次": "shift", "白班": "day_shift", "晚班": "night_shift",
    "全天": "full_day", "出勤": "attendance", "人数": "headcount",
    "工时": "labor_hours", "效率": "efficiency", "工段": "process_section",
    "工序": "process", "线别": "line", "在线": "in_process",
    "存板": "board_inventory", "产值": "output_value", "目标": "target",
    "计件": "piecework", "总额": "total_amount", "合计": "total", "日": "day", "时": "hour",
    "输入者": "entered_by", "输入": "entry", "创建者": "created_by",
    "创建": "creation", "审核者": "reviewed_by", "审核": "review",
    "审批": "approval", "批准": "approval", "签名": "signature",
    "确认者": "confirmed_by", "确认": "confirmation", "签收": "acknowledgement",
    "登记": "registration", "部门": "department", "主管": "supervisor",
    "申请": "request", "使用": "usage", "责任": "responsible",
    "请购": "purchase_requisition", "领料人": "material_recipient",
    "凭证": "voucher", "目的": "purpose", "明细号": "detail_no",
    "联系人": "contact_person", "负责人": "responsible_person",
    "电话": "phone", "手机": "mobile_phone", "地址": "address",
    "人": "person", "者": "by", "号": "no",
    "停止": "stop", "停交": "delivery_stopped", "冻结": "frozen",
    "暂停": "paused", "修改": "revision", "次数": "count", "次": "count",
    "取消": "cancel", "允许": "allow", "是否": "is", "有无": "has",
    "未": "not", "已": "already", "需": "required", "可": "available",
    "转用": "reallocation", "被替代": "replaced", "被": "by",
    "口头": "verbal", "不含停交": "excluding_stopped_deliveries",
    "不补不换": "no_replacement", "入帐": "posting", "发票": "invoice",
    "开票": "invoicing", "收款": "collection", "付款": "payment",
    "收费": "charged", "免费": "free", "费用": "expense", "费": "fee", "各项": "itemized",
    "小计": "subtotal", "其他": "other", "其它": "other",
    "退货": "return", "退单": "rejected_order", "出口": "export",
    "不出口": "not_export", "贸易": "trade", "增值税": "vat",
    "工艺水印": "process_watermark", "水印": "watermark",
    "指定": "designated", "标记": "marking", "打印": "printing",
    "列印": "printing", "印次": "print_cycles", "冲次": "punch_cycles",
    "加急": "urgent", "特殊": "special", "正常": "normal", "异常": "abnormal",
    "制作": "manufacturing", "本卡": "current_card", "结批": "batch_closed",
    "测试": "testing", "检验": "inspection", "质量": "quality",
    "发放": "release", "判退": "rejection", "原因": "reason",
    "版本号": "version", "版本": "version", "资料": "data",
    "英文": "english", "方式": "method", "产品": "product",
    "颜色": "color", "阻焊": "solder_mask", "文字": "legend",
    "油墨": "ink", "镀金": "gold_plating", "级别": "grade",
    "电镀": "electroplating", "镍": "nickel", "金": "gold",
    "菲林": "film", "线路": "circuit", "字符": "legend",
    "钻带": "drill_tape", "模具": "mold", "治具": "fixture", "模治具": "tooling",
    "终端": "end_customer", "海关": "customs", "商品": "commodity",
    "整箱": "full_carton", "尾箱": "partial_carton", "尾数": "remainder",
    "箱号": "carton_no", "箱数": "carton_count", "箱": "carton",
    "外箱": "outer_carton", "条码": "barcode", "净重": "net_weight",
    "毛重": "gross_weight", "位置": "position", "序号": "sequence_no",
    "不": "not", "卷料": "roll_material", "标准料": "standard_material",
    "公司": "company", "营销模式": "business_model", "模式": "mode",
    "本厂": "this_factory", "货物": "goods", "暂存": "temporary_storage",
    "合作": "cooperation", "处理": "handling", "意见": "feedback",
    "回复": "reply", "组别": "group", "业务组别": "sales_group",
    "到货": "arrival", "供应": "supply",
    "大陆": "mainland", "香港": "hong_kong", "识别号码": "identifier",
    "借料": "borrowed_material", "入": "in", "出": "out",
    "打叉板": "crossed_board", "打x板": "crossed_board", "叉板": "crossed_board",
    "接收": "accepted", "大料": "full_size_material", "边料": "offcuts",
    "原": "original", "旧": "old", "新单": "new_order",
    "返单": "repeat_order", "新": "new",
    "人工": "labor", "水费": "water", "电费": "electricity",
    "制费": "manufacturing_overhead", "折旧": "depreciation", "化工": "chemical",
    "压合": "lamination", "干膜": "dry_film", "间接工资": "indirect_labor",
    "间接": "indirect", "摊销": "amortization", "包线": "line_contract",
    "合成": "composite", "待": "pending", "返工": "rework",
    "固定资产": "fixed_asset", "资产": "asset", "科目": "account",
    "难易程度": "difficulty", "参考": "reference", "改": "change",
    "首选": "preferred", "图": "drawing", "转码": "conversion",
    "月结": "monthly_settlement", "帐期": "payment_term", "产地": "origin",
    "附板": "supplemental_board", "样板": "sample", "最": "most",
    "审": "review", "发行": "issue", "评审": "review", "综合": "combined",
    "板宽": "board_width", "的": "of", "有": "with", "克": "grams",
    "双面": "double_sided", "单双面": "single_double_sided",
    "一仓": "warehouse_1", "二仓": "warehouse_2", "三仓": "warehouse_3",
    "四仓": "warehouse_4", "一厂": "factory_1", "二厂": "factory_2",
    "五厂": "factory_5", "六厂": "factory_6", "七厂": "factory_7",
    "一铜": "first_copper", "二铜": "second_copper",
    "孔铜": "hole_copper", "铜": "copper", "仓": "warehouse",
    "验收": "acceptance", "结果": "result", "打折": "discount",
    "扣款": "deduction", "判定": "determination", "额外": "extra",
    "免检": "inspection_exempt", "还出": "return_out",
    "借出": "loan_out", "借入": "loan_in", "延期": "extension",
    "报关核销": "customs_writeoff", "报关": "customs_declaration",
    "订购内容": "order_content", "平方米": "square_meters",
    "预投": "planned_material_input",
    "完成": "completion", "流程": "workflow", "因打X板": "due_to_crossed_board",
    "多": "excess", "比例": "ratio", "当前": "current",
    "尺寸": "dimensions", "检查": "inspection",
    "%": "percent", "‰": "per_mille", "≥": "minimum",
}
ORDERED_TERMS = sorted(BUSINESS_TERMS, key=lambda term: (-len(term), term))
OUTPUT = Path(__file__).resolve().with_name("erp_field_registry.json")


def english_column_name(source_header: str, unique_header: str, column_index: int) -> str:
    """Translate controlled terms without silently discarding unfamiliar text."""
    duplicate = re.search(r"（重复列(\d+)）$", unique_header)
    suffix = f"_duplicate_{duplicate.group(1)}" if duplicate else ""
    if not source_header:
        return f"erp_blank_column_{column_index}{suffix}"
    placeholder = re.fullmatch(r"其[他它]([A-Za-z]*)(\d+)", source_header)
    if placeholder:
        return f"erp_{placeholder.group(1).lower() or 'other'}_{placeholder.group(2)}{suffix}"
    if re.fullmatch(r"\d{1,2}:\d{2}-\d{1,2}:\d{2}", source_header):
        return "erp_time_" + re.sub(r"\D+", "_", source_header) + suffix
    tokens = []
    remaining = source_header
    while remaining:
        term = next((term for term in ORDERED_TERMS if remaining.startswith(term)), None)
        if term is not None:
            tokens.append(BUSINESS_TERMS[term])
            remaining = remaining[len(term):]
            continue
        ascii_word = re.match(r"[A-Za-z]+|[0-9]+", remaining)
        if ascii_word:
            tokens.append(ascii_word.group().lower())
            remaining = remaining[ascii_word.end():]
            continue
        if re.match(r"[\s\x00-\x1f\x7f-\x9f_\-/\\()（）<>:：.,，、+&\[\]]", remaining):
            remaining = remaining[1:]
            continue
        raise SyncError(f"字段注册表词典缺少业务术语：{source_header!r}，未识别部分 {remaining!r}")
    stem = "_".join(tokens)
    if not stem:
        raise SyncError(f"字段注册表词典无法命名表头：{source_header!r}")
    if not stem[0].isalpha():
        stem = "column_" + stem
    candidate = "erp_" + stem + suffix
    if len(candidate) > 64:
        digest = hashlib.sha256(candidate.encode("utf-8")).hexdigest()[:10]
        candidate = candidate[:53].rstrip("_") + "_" + digest
    return candidate


def disambiguate_fields(fields: List[ErpFieldDefinition]) -> List[ErpFieldDefinition]:
    counts = Counter((field.table_name, field.database_column) for field in fields)
    result = []
    for field in fields:
        if counts[(field.table_name, field.database_column)] > 1:
            scope = [field.table_name, field.source_file, field.sheet_name, field.excel_unique_header]
            digest = hashlib.sha256(json.dumps(scope, ensure_ascii=False).encode("utf-8")).hexdigest()[:10]
            # This business label makes same-table material issue sources legible.
            tag = "replenishment" if "补料" in field.source_file else "source"
            suffix = f"_{tag}_{digest}"
            field = replace(field, database_column=field.database_column[:64 - len(suffix)].rstrip("_") + suffix)
        result.append(field)
    ErpFieldRegistry(result)  # Reject even an unlikely truncated/hash collision.
    return result


def build_registry(source_directory: Path = SOURCE_DIRECTORY) -> dict:
    fields = []
    files = sorted(
        (path for path in source_directory.rglob("*")
         if path.is_file() and path.suffix.lower() in (".xls", ".xlsx") and not path.name.startswith("~$")),
        key=lambda path: path.relative_to(source_directory).as_posix(),
    )
    for path in files:
        source_file = path.relative_to(source_directory).as_posix()
        for sheet, raw_headers in iter_workbook_headers(path):
            work_order = "生产指示资料" in path.name and is_work_order_sheet(raw_headers)
            table = "qms_work_order" if work_order else source_table_name(source_file, sheet, False)
            for index, unique in enumerate(unique_headers(raw_headers), 1):
                source = excel_header_identity(raw_headers[index - 1])
                fields.append(ErpFieldDefinition(
                    table, source_file, sheet, source, unique,
                    english_column_name(source, unique, index), legacy_database_column_name(unique),
                    erp_column_comment(source), index,
                ))
    resolved = disambiguate_fields(fields)
    collisions = [
        {"table_name": old.table_name, "source_file": old.source_file,
         "sheet_name": old.sheet_name, "excel_unique_header": old.excel_unique_header,
         "base_column": old.database_column, "database_column": new.database_column}
        for old, new in zip(fields, resolved) if old.database_column != new.database_column
    ]
    return {"schema_version": 1, "fields": [asdict(field) for field in resolved], "collision_resolutions": collisions}


def merge_registry_data(generated: dict, base_registry: ErpFieldRegistry) -> dict:
    """Preserve reviewed names and sources absent from the current export."""
    def scope(field: ErpFieldDefinition) -> tuple:
        return (field.table_name, canonical_source_file_name(field.source_file),
                field.sheet_name, field.excel_unique_header)

    previous_by_scope = {scope(field): field for field in base_registry.fields}
    generated_by_file = {}
    for row in generated["fields"]:
        field = ErpFieldDefinition(**row)
        previous = previous_by_scope.get(scope(field))
        if previous and previous.excel_source_header == field.excel_source_header:
            field = replace(
                field, database_column=previous.database_column,
                source_file=previous.source_file,
            )
        generated_by_file.setdefault(canonical_source_file_name(field.source_file), []).append(field)
    merged = []
    emitted_files = set()
    for field in base_registry.fields:
        source = canonical_source_file_name(field.source_file)
        if source in generated_by_file:
            if source not in emitted_files:
                merged.extend(generated_by_file[source])
                emitted_files.add(source)
        else:
            merged.append(field)
    for source, fields in generated_by_file.items():
        if source not in emitted_files:
            merged.extend(fields)
    ErpFieldRegistry(merged)
    resolutions = []
    for field in merged:
        base_name = english_column_name(
            field.excel_source_header, field.excel_unique_header, field.column_index)
        if field.database_column != base_name:
            resolutions.append({
                "table_name": field.table_name, "source_file": field.source_file,
                "sheet_name": field.sheet_name, "excel_unique_header": field.excel_unique_header,
                "base_column": base_name, "database_column": field.database_column,
            })
    result = {"schema_version": 1, "fields": [asdict(field) for field in merged],
              "collision_resolutions": resolutions}
    if base_registry.source_layouts:
        result["source_layouts"] = list(base_registry.source_layouts)
    return result


def registry_text(data: dict) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-directory", type=Path, default=SOURCE_DIRECTORY)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--base-registry", type=Path,
                        help="Preserve reviewed columns and absent source files from this registry")
    parser.add_argument("--check", action="store_true", help="Read-only comparison with the reviewed JSON")
    args = parser.parse_args()
    data = build_registry(args.source_directory)
    if args.base_registry:
        data = merge_registry_data(data, load_erp_field_registry(args.base_registry))
    if not data["fields"]:
        raise SyncError("字段注册表未找到 Excel 表头，拒绝写入空注册表。")
    text = registry_text(data)
    if args.check:
        if not args.output.exists() or args.output.read_text(encoding="utf-8") != text:
            raise SyncError("字段注册表与源表头/词典不一致，请重新生成并审核。")
    else:
        args.output.write_text(text, encoding="utf-8")
    print(f"Registry {'verified' if args.check else 'generated'}: {len(data['fields'])} fields; "
          f"{len(data['collision_resolutions'])} source-scoped collision resolutions.")


if __name__ == "__main__":
    main()
