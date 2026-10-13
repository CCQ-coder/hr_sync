# ERP 英文字段与数据库迁移设计

## 目标

将 ERP Excel 的动态实体字段从 `erp_<中文列名>` 统一改为
`erp_<english_snake_case>`，使 BI 查询可使用稳定的 ASCII 字段名。每个
字段的 MySQL `COMMENT` 保留对应的 Excel 中文列名。

本次迁移必须保留已经写入 QMS MySQL 的数据，不能在后续同步时重新创建中文
字段，也不能将未确定语义的中文列名静默写入新的物理字段。

## 范围

- 当前 12 个 ERP 工作簿、1111 个列上下文。
- 固定业务表和 `qms_work_order` 中由 ERP 动态创建的字段。
- `qms_erp_unclassified` 的 ERP 动态字段支持。
- 同步程序、字段对照产物、BI 示例 SQL 与 Windows EXE。

`qms_production_batch` 只使用已有的标准业务字段，不在本次中创建 ERP 动态字段。

## 字段注册表

新增受版本控制的 JSON 注册表，记录每一个实际目标字段。每条记录至少包括：

- `table_name`：目标业务表；
- `excel_source_header`：Excel 原始中文列名；
- `excel_unique_header`：处理重复列后的唯一列名；
- `english_name`：不含 `erp_` 的 ASCII snake_case 名称；
- `database_column`：`erp_` + `english_name`；
- `column_comment`：以 `Excel列名：` 开头的中文注释；
- `legacy_database_column`：旧版本对应的 `erp_<中文>` 字段名；
- `source_file`、`sheet_name`、`excel_column`：用于审计与生成迁移脚本。

同一目标表的英文名必须唯一，且符合 `^erp_[a-z][a-z0-9_]{0,59}$`。普通业务
字段使用可读英文，例如 `加工工艺` 对应 `erp_processing_technology`。重复列、
空列或 ERP 自定义占位列使用仍然可读且稳定的英文名，例如
`erp_purchase_category_duplicate_2`、`erp_other_17`。如果以后 Excel 新增了未登记
的列，同步将明确报出需补充注册表，而不是重新创建中文字段或猜测不稳定字段名。

## 同步数据流

1. 读取 Excel 表头后保留原始表头、唯一表头和列位置。
2. 根据目标表和唯一表头从注册表取得英文物理字段与中文注释。
3. `RawSourceRecord` 与工单扩展字段同时携带字段值和字段注释定义。
4. 新建 ERP 字段使用 `LONGTEXT NULL COMMENT 'Excel列名：<中文>'`。
5. 已有英文字段仅在注释缺失或不一致时修正注释；同一字段收到冲突的中文定义时
   同步失败，防止最后一个工作表覆盖注释。

## 历史数据库迁移

生成以下可审阅产物：

- 迁移清单：逐行列出表名、旧字段、新字段、中文注释和 Excel 来源；
- 预检 SQL：列出现有 `erp_` 字段、数据库版本和冲突状态；
- 改名 SQL：每行使用
  `ALTER TABLE ... CHANGE COLUMN <old> <new> LONGTEXT NULL COMMENT ...`；
- 校验 SQL：确认旧字段已消失、新字段和注释存在。

迁移前要停止同步并备份数据库。当前同步工具创建的 ERP 动态字段均为
`LONGTEXT NULL`，所以生成的 `CHANGE COLUMN` 语句可原样保留数据。预检发现字段
类型或可空性被人工改动、旧新字段并存、字段不存在或注释冲突时，脚本不应按默认
语句盲目执行，必须由数据库管理员复核后调整。

MySQL DDL 会隐式提交；因此迁移不承诺单事务回滚。建议在低峰期按表执行，先执行
预检，再运行改名 SQL，最后部署新 EXE 并执行一次手动同步。现有 BI SQL 中引用旧
中文字段的地方必须随迁移改为新的英文名称。

## 失败保护

- 所有标识符使用受控白名单和反引号，不以 Excel 文本直接拼接 SQL。
- 注释通过参数化 SQL 写入；注释清理控制字符并保留重复列表达信息。
- 注册表校验字段名、目标表、重复映射、64 字节 MySQL 标识符限制和注释冲突。
- 正常同步不执行数据库字段改名。改名只能通过交付的迁移 SQL 执行。

## 验证

- 为已登记、重复、空、长和未知表头测试字段解析。
- 测试新建/修正 MySQL `COMMENT` 的 SQL 与参数。
- 测试业务表和 `qms_work_order` 都写入同一英文字段名。
- 测试迁移清单与 SQL 对每条映射一一对应，且保留数据定义。
- 重新生成字段对照 JSON/XLSX，确认其中显示英文物理字段和中文注释。
- 执行全部 Python 单元测试、语法检查和 EXE 打包检查。
