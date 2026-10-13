import fs from "node:fs/promises";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const root = "D:/project/hr_sync";
const outputDir = `${root}/outputs`;
const source = JSON.parse(await fs.readFile(`${outputDir}/excel_database_field_mapping_data.json`, "utf8"));
const outputPath = `${outputDir}/ERP_Excel_数据库字段对照表-实体字段版.xlsx`;
const font = "Arial";
const navy = "#1F4E78";
const lightBlue = "#D9EAF7";
const paleYellow = "#FFF2CC";

function columnName(index) {
  let value = index;
  let result = "";
  while (value > 0) {
    const remainder = (value - 1) % 26;
    result = String.fromCharCode(65 + remainder) + result;
    value = Math.floor((value - 1) / 26);
  }
  return result;
}

function applyHeader(range) {
  range.format = {
    fill: navy,
    font: { name: font, size: 10, bold: true, color: "#FFFFFF" },
    horizontalAlignment: "center",
    verticalAlignment: "center",
    wrapText: true,
    borders: { preset: "all", style: "thin", color: "#FFFFFF" },
  };
}

function applyTitle(range) {
  range.format = {
    font: { name: font, size: 14, bold: true, color: "#1F1F1F" },
    verticalAlignment: "center",
  };
}

const workbook = Workbook.create();
const overview = workbook.worksheets.add("说明");
const summary = workbook.worksheets.add("文件汇总");
const mapping = workbook.worksheets.add("字段对照");

for (const sheet of [overview, summary, mapping]) {
  sheet.showGridLines = false;
  sheet.tabColor = navy;
}

overview.getRange("A1:H1").merge();
overview.getRange("A1").values = [["ERP Excel 与 QMS 数据库字段对照表"]];
applyTitle(overview.getRange("A1:H1"));
overview.getRange("A3:B5").values = [
  ["文件数量", source.source_summary.length],
  ["Excel 源列数量", source.mapping_rows.length],
  ["当前同步方式", "每个 Excel 列写入对应业务表的实体字段；生产指示资料同时映射至工单和生产批次表"],
];
overview.getRange("A3:A5").format = { fill: lightBlue, font: { name: font, bold: true }, verticalAlignment: "center" };
overview.getRange("A3:B5").format.borders = { preset: "all", style: "thin", color: "#B7C9D6" };
overview.getRange("A7:H7").merge();
overview.getRange("A7").values = [["读取方式说明"]];
overview.getRange("A7:H7").format = { fill: navy, font: { name: font, bold: true, color: "#FFFFFF" } };
overview.getRange("A8:H10").merge();
overview.getRange("A8").values = [[
  "“字段对照”工作表中，每一行代表一个 Excel 源列，均对应字段注册表审核后的 erp_<english_snake_case> 实体字段。"
  + "原始中文列名保存在数据库字段注释（Excel列名：…）中；字段不再保存到 row_data_json。"
  + "生产指示资料还会按 QMS 规则写入工单与生产批次的标准字段。"
]];
overview.getRange("A8:H10").format = { fill: paleYellow, font: { name: font, size: 10 }, wrapText: true, verticalAlignment: "top" };

overview.getRange("A12:B12").values = [["固定业务表公共字段", "含义"]];
applyHeader(overview.getRange("A12:B12"));
overview.getRange(`A13:B${12 + source.source_table_columns.length}`).values = source.source_table_columns;
overview.getRange(`A13:B${12 + source.source_table_columns.length}`).format = { font: { name: font, size: 10 }, verticalAlignment: "center", borders: { preset: "all", style: "thin", color: "#D9E2F3" } };
overview.getRange("A:A").format.columnWidth = 24;
overview.getRange("B:B").format.columnWidth = 70;
overview.getRange("A1:H15").format.wrapText = true;

const summaryHeaders = ["Excel 文件", "工作表数", "列数", "固定写入表"];
summary.getRange("A1:D1").values = [summaryHeaders];
applyHeader(summary.getRange("A1:D1"));
summary.getRange(`A2:D${source.source_summary.length + 1}`).values = source.source_summary.map((item) => summaryHeaders.map((key) => item[key] ?? ""));
summary.getRange(`A2:D${source.source_summary.length + 1}`).format = { font: { name: font, size: 10 }, verticalAlignment: "center", borders: { preset: "all", style: "thin", color: "#D9E2F3" } };
summary.getRange("A:A").format.columnWidth = 32;
summary.getRange("B:C").format.columnWidth = 12;
summary.getRange("D:D").format.columnWidth = 34;
summary.freezePanes.freezeRows(1);

const mappingHeaders = [
  "Excel 文件", "工作表", "Excel 列", "Excel 原始列名", "Excel 唯一列名",
  "英文数据库字段", "数据库字段注释", "旧数据库字段",
  "当前写入表", "当前写入字段", "当前业务表", "当前业务字段", "转换规则", "说明",
];
mapping.getRange("A1:N1").values = [mappingHeaders];
applyHeader(mapping.getRange("A1:N1"));
const mappingValues = source.mapping_rows.map((item) => mappingHeaders.map((key) => item[key] ?? ""));
const finalRow = mappingValues.length + 1;
mapping.getRange(`A2:N${finalRow}`).values = mappingValues;
mapping.getRange(`A2:N${finalRow}`).format = {
  font: { name: font, size: 10 },
  verticalAlignment: "center",
  wrapText: true,
  borders: { preset: "all", style: "thin", color: "#E6E6E6" },
};
mapping.getRange(`A2:K${finalRow}`).format.rowHeight = 30;
mapping.getRange("A:A").format.columnWidth = 30;
mapping.getRange("B:B").format.columnWidth = 14;
mapping.getRange("C:C").format.columnWidth = 10;
mapping.getRange("D:E").format.columnWidth = 23;
mapping.getRange("F:F").format.columnWidth = 34;
mapping.getRange("G:G").format.columnWidth = 28;
mapping.getRange("H:H").format.columnWidth = 28;
mapping.getRange("I:I").format.columnWidth = 22;
mapping.getRange("J:J").format.columnWidth = 32;
mapping.getRange("K:L").format.columnWidth = 23;
mapping.getRange("M:M").format.columnWidth = 32;
mapping.getRange("N:N").format.columnWidth = 28;
mapping.freezePanes.freezeRows(1);
mapping.freezePanes.freezeColumns(3);

// Highlight rows that already write to a dedicated QMS business column.
const businessTableIndex = mappingHeaders.indexOf("当前业务表");
for (let row = 0; row < mappingValues.length; row += 1) {
  if (mappingValues[row][businessTableIndex]) {
    mapping.getRangeByIndexes(row + 1, businessTableIndex, 1, 3).format.fill = "#E2F0D9";
  }
}

workbook.recalculate();
const inspection = await workbook.inspect({
  kind: "table",
  range: "字段对照!A1:N12",
  include: "values",
  tableMaxRows: 12,
  tableMaxCols: 14,
});
console.log(inspection.ndjson);
const preview = await workbook.render({ sheetName: "说明", range: "A1:H22", scale: 1.5, format: "png" });
await fs.writeFile(`${outputDir}/ERP_Excel_数据库字段对照表_预览.png`, new Uint8Array(await preview.arrayBuffer()));
await fs.mkdir(outputDir, { recursive: true });
const output = await SpreadsheetFile.exportXlsx(workbook);
await output.save(outputPath);
console.log(JSON.stringify({ outputPath, mappingRows: mappingValues.length, finalRow, lastColumn: columnName(mappingHeaders.length) }));
