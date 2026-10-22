# QMS ERP 数据同步工具

## 客户分支

- `zsh`：卓思涵的分支，用于卓思涵客户的开发和部署。
- `gy`：共赢的分支，从 `main` 创建，用于共赢客户的开发和部署。
- `main`：基础分支；客户专属变更应提交到对应的 `zsh` 或 `gy` 分支。

两客户的真实配置、数据库连接、同步状态及源数据应分别维护，部署前确认所用分支和客户配置。

## 文件布局

- `qms_erp_sync.py`、`flying_probe_sync.py`、`run_device_raw_receiver.py`：运行入口。
- `device_raw_receiver/`、`ini_share_sync/`：设备接收与共享同步模块。
- `docs/guides/`：设备接收和飞针同步使用说明。文档中的命令均在项目根目录执行。
- `packaging/specs/`：PyInstaller 规格文件；打包脚本保留在根目录，新生成的规格也写入此目录。
- `sql/`：字段迁移 SQL 与 `bi_dashboard_queries.sql` 查询。
- `tests/`：自动化测试；`releases/`：已发布版本。
- `data/BI数据源/`、`data/zsh-数据源/`：两套本地 ERP 源数据，独立保存，不合并、不纳入 Git。已有部署配置如使用旧目录，请重新选择移动后的目录。

根目录的配置模板、字段注册表和生成脚本保留原路径，以兼容运行时资源定位与现有测试。真实配置、同步状态和业务数据保留在本地，不纳入 Git。

这是一个可双击运行的 Windows 工具。它会递归读取 ERP BI 目录内全部 `.xls` / `.xlsx` 文件及其全部工作表，将数据初始化或增量同步到 QMS 的 MySQL 数据库。

默认使用 **MySQL 数据库直连**，不需要 QMS 网关 Token。同步采用 InnoDB 事务、`utf8mb4` 和 MySQL 幂等更新；保留来源文件、工作表、Excel 行号和数据指纹，便于追溯。

## 固定业务表与字段命名

每个 ERP 文件会写入固定、可读的业务表，而不是创建随机动态表名。例如：

| ERP 文件 | QMS 业务表 |
| --- | --- |
| 客户订单资料 | `qms_customer_order` |
| 客户料号资料 | `qms_customer_part` |
| 工程资料资料 | `qms_engineering_data` |
| 采购订单资料 | `qms_purchase_order` |
| 原料资料明细 | `qms_material` |
| 原料入库单资料 | `qms_material_receipt` |
| 原料出库单资料、补料资料 | `qms_material_issue` |
| 成品入库单资料 | `qms_finished_goods_receipt` |
| 送货单资料 | `qms_delivery_note` |
| 各工段出数汇总资料 | `qms_process_output_summary` |
| 生产指示资料 | `qms_work_order`、`qms_production_batch` |

所有 Excel 原始列都直接写入数据库实体字段，不再存入 `row_data_json`。动态字段统一使用英文 `erp_<english_snake_case>`，例如 Excel 列“采购单号”对应 `erp_purchase_order_no`。原始中文列名写入 MySQL 字段注释，例如 `Excel列名：采购单号`，可供 BI 查询和 Navicat 查看。

客户订单以“订单编号、厂内编号”识别同一订单物料。再次导出时，最新行的所有字段覆盖原记录，保留原记录的 `id`，并清除同订单同物料的重复行；不同物料仍为独立记录。同一文件内若出现多行同订单同物料，以靠后的行作为最新数据。首次运行新版同步会整理已有客户订单，即使 Excel 文件没有变化。

字段定义以项目根目录的 `erp_field_registry.json` 为准。发现新增、改名或调整顺序的 Excel 列时，同步会停止并提示更新注册表；它**不会**自动创建 `erp_中文字段`。新增字段的正确流程是：更新并审核注册表 → 重新生成字段对照与迁移 SQL → 由 DBA 执行迁移验证 → 部署新版 EXE。

`outputs\ERP_Excel_数据库字段对照表-实体字段版.xlsx` 会列出 Excel 列、英文数据库字段、中文字段注释、旧字段名及业务映射，供业务和 BI 人员核对。

## 运行 EXE

1. 只分享或下载干净的 `dist\QMS-ERP数据同步工具-英文字段版-发布包` 目录；不要分享整个 `dist` 目录。
2. 在目标服务器的受控本机目录中复制该发布包，再将 `qms_erp_sync_config.example.json` 复制并重命名为 `qms_erp_sync_config.json`。
3. 仅在这个本机部署副本中填写 MySQL 主机、端口、库名、账号、密码和租户编码；界面不显示这些敏感配置。不要把实际配置文件放回、打包或分享给其它人。
4. 打开 `QMS-ERP数据同步工具-英文字段版.exe`，分别选择初始化全量目录（例如 `D:\project\hr_sync\data\BI数据源`）和增量根目录（例如 `D:\项目文档\rpa华软ERP导出`）。
5. 点击“测试数据库连接”，确认无误后点击“开始同步”。

数据库账号应使用 QMS 的 MySQL 应用账号，并至少具备固定业务表的 `SELECT`、`INSERT`、`UPDATE`、`CREATE TABLE`、`CREATE INDEX`、`ALTER TABLE` 权限。不要把 MySQL `root` 账号作为日常同步账号。

配置、增量状态和运行日志会保存到 EXE 同目录；若该目录不可写，则保存到 `%APPDATA%\QmsErpSync`。配置文件可能包含数据库密码，请只保存在受控的本机目录。

## 从旧中文字段迁移到英文字段

新版 EXE 不会自动执行旧 `erp_中文字段` 到英文字段的迁移/改名 SQL，也不会重命名旧中文字段。正常同步会根据已审核的 `erp_field_registry.json` 创建缺失的英文字段，或修正这些已审核英文字段的中文字段注释；这不替代历史数据迁移，也不会自动回填或删除旧中文字段。对于已经存在旧字段的生产数据库，发布前仍必须由 DBA 按以下顺序执行，并在每一步确认无误后再继续：

1. 停止正在运行的同步工具，并完成数据库备份。
2. 以目标数据库执行 `erp_field_rename_preflight.sql`，处理所有预检异常。
3. 执行 `erp_field_rename_apply.sql`。
4. 执行 `erp_field_rename_verify.sql`，确认没有缺列、字段注释不一致或数据回填异常。
5. 部署并运行 `QMS-ERP数据同步工具-英文字段版.exe`。
6. 仅当验证结果和业务抽查均无误时，才可选择执行 `erp_field_rename_contract.sql` 清理可收尾的旧共享字段。

上述 SQL 会生成到项目的 `sql` 目录，也会随新版 EXE 复制到干净的发布包目录。它们是供 DBA 审核和手动执行的文件；同步工具不会连接数据库执行这些迁移 SQL。`erp_field_rename_manifest.json` 记录每一个旧字段、新字段、来源文件和工作表的对应关系。

## 初始化与增量同步

“初始化数据目录”用于完整基线；“增量同步目录”用于 RPA 每日导出。增量目录会递归识别 `2026-9-17\*.XLS` 这类按日期分类的子目录，并按日期从旧到新处理。勾选“跳过初始化”后，完全不扫描全量目录，只处理增量目录。

“清空并重新初始化”是独立操作：确认后预检全部 Excel，清空全部 ERP 目标源表以及 `qms_production_batch`、`qms_work_order` 中**所有租户的数据**，再导入初始化和增量目录。删除和导入处于同一数据库事务；如果导入失败会回滚。清理前会拒绝非 InnoDB 目标表及范围外的外键引用。运行前请备份数据库，并确认没有其它服务依赖这些表中的旧记录。普通“开始同步”和自动监控不会清空表。新版按 ERP 业务编号及可用的明细编号或物料编号识别记录，金额、数量变化时更新原记录；不同明细分别保留。缺少可区分明细的编号且同一文件发生冲突时会停止导入。升级后必须先使用此操作建立新版断点，普通同步不会混用旧来源键。

程序按单个 Excel 文件提交数据库事务，并在每个文件提交后保存断点。运行中断或数据库断线后，下次启动会跳过已完成且内容未变的文件，重试中断时正在处理的文件。文件校验使用 SHA-256 内容哈希；当天同名文件即使大小、修改时间未变，只要内容改变也会重读。覆盖期间内容再次变化时，本次处理会报错并等待下一次重试。全量基线文件变更后，为保证先基线后增量的顺序，增量文件会重放。

源记录优先使用目标表、业务编号和明细标识作为身份；同一数据出现在不同导出文件时会复用一行，内容变化会覆盖该行。缺少可用编号的报表仍按规范化后的字段内容识别。同一文件中无法区分的重复明细会报错，需在字段注册表中补充明细编号。升级后请先使用独立的“清空并重新初始化”操作。

同名文件覆盖时，新版文件中删除的源记录、工单及批次会按本工具记录的文件归属停用；其他文件仍包含的记录不会被停用。首次使用新版时会建立文件归属记录，因此迁移旧版时请保留本机同步状态；若旧状态没有归属记录，首次重读只会建立归属，后续覆盖才可准确识别删行。直接从增量目录删除整个文件不会自动停用历史记录。一个文件在两次扫描之间被连续覆盖多次时，程序只能同步扫描到的最新版本，无法恢复未留存的中间版本。

界面可启用“自动监控”，并设置检查间隔（1 至 1440 分钟，默认 5 分钟）。自动监控只监视增量同步目录；同步期间如果文件再次变化，下一轮检查会再处理。断点保存在 `qms_erp_sync_state_progress` 目录，完整状态保存在 `qms_erp_sync_state.json`；迁移部署目录时应一起复制。

配置文件的自动监控项目如下：

```json
{
  "initialization_directory": "D:\\project\\hr_sync\\data\\BI数据源",
  "incremental_directory": "D:\\项目文档\\rpa华软ERP导出",
  "skip_initialization": false,
  "auto_sync_enabled": true,
  "auto_sync_interval_minutes": 5
}
```

每次同步前都会重新读取配置文件，因此修改数据库连接信息后不需要重启工具。

## 在 Navicat 查看数据

MySQL 没有 PostgreSQL 原生 RLS。工具会在每个业务表中保存 `tenant_code`，请使用受限的 MySQL 应用账号，并在查询时按租户筛选：

```sql
SELECT tenant_code, COUNT(*) AS row_count
FROM qms_purchase_order
GROUP BY tenant_code;
```

查看明细时使用实际租户编码，例如 `WHERE tenant_code = 'customer-b'`。

## 打包

在项目目录执行：

```powershell
.\build_exe.ps1 -Name 'QMS-ERP数据同步工具-英文字段版'
```

打包会在共享构建目录生成 `dist\QMS-ERP数据同步工具-英文字段版.exe`，并在其下生成唯一允许对外分享的干净发布包目录：

`dist\QMS-ERP数据同步工具-英文字段版-发布包`

发布包只包含以下白名单文件：

- `QMS-ERP数据同步工具-英文字段版.exe`
- `erp_field_registry.json`
- `erp_field_rename_manifest.json`
- `erp_field_rename_preflight.sql`
- `erp_field_rename_apply.sql`
- `erp_field_rename_verify.sql`
- `erp_field_rename_contract.sql`
- `qms_erp_raw_schema.sql`
- `qms_erp_sync_config.example.json`（无密码的配置模板）

字段注册表同时会被嵌入单文件 EXE 的 PyInstaller 资源目录，确保 EXE 运行时能读取经审核的映射。构建脚本会先检查发布包目录；如果其中已有任何非白名单文件（尤其是 `qms_erp_sync_config.json` 或 `qms_erp_sync_state.json`），构建会拒绝继续，绝不会把这些文件复制到发布包。

如需覆盖构建命令的 `-Name`，只可使用由英文、数字、下划线、连字符和中文组成的安全文件基名。空名称、盘符或网络绝对路径、`..`、斜杠/反斜杠、空格、冒号和 Windows 保留设备名会在创建任何发布路径前被拒绝。

实际的 `qms_erp_sync_config.json`、`qms_erp_sync_state.json` 和 `qms_erp_sync_state_progress` 只应存在于受控的本机部署目录。它们可能包含密码或业务状态，不能随发布包、压缩包或工单附件传播。

命令行或 Windows 任务计划程序可使用：

```powershell
.\QMS-ERP数据同步工具-英文字段版.exe --headless
.\QMS-ERP数据同步工具-英文字段版.exe --headless --dry-run
```
