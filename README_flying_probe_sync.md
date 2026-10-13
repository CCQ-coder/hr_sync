# QMS 飞针 TXT 数据同步工具

该工具读取 `\\Scbgx\数字化\飞针机` 下各设备子目录中的万通达 TXT，先按固定 11 行格式校验，再写入 QMS MySQL。它不处理 ERP Excel，也不把多个设备的原始业务记录混入同一张表。

## 已审核的设备表

| 共享目录 | QMS 业务表 |
| --- | --- |
| `25-EP-427` | `qms_flyprobe_25_ep_427` |
| `27-EP-428` | `qms_flyprobe_27_ep_428` |
| `测试设备1` | `qms_flyprobe_test_device_1` |

公共表 `qms_flyprobe_file_version` 只保存文件版本、哈希、源文本和校验状态；`qms_flyprobe_sync_error` 只保存格式校验审计。两者不承载混合的设备业务数据。

同一设备、同一路径且内容相同的文件不会重复写入。同一路径内容变化时会保留旧版本并新增当前版本。文件名中的 `-0`、`-1` 也会原样保留，不能被当作可覆盖的同一料号。

## 先校验格式

使用实际的 QMS MySQL 配置文件执行无写入预检：

```powershell
.\.venv\Scripts\python.exe .\flying_probe_sync.py `
  --source-directory '\\Scbgx\数字化\飞针机' `
  --database-config .\dist\qms_erp_sync_config.json `
  --dry-run
```

预检会输出 `VALID`、`WARNING`、`INVALID` 数量以及每类问题。默认规则包括：11 条固定字段、字段顺序和数量、坐标范围、整数/小数格式、方向值、测试总数等式，以及测试时长上限（默认 72 小时）。

`WARNING` 会同步并保留原始值；`INVALID` 默认仅进入文件版本和错误审计表，不写入设备业务表。需要审计性地保存无效文件时，显式增加 `--include-invalid`。

## 写入 QMS

确认预检后，去掉 `--dry-run`：

```powershell
.\.venv\Scripts\python.exe .\flying_probe_sync.py `
  --source-directory '\\Scbgx\数字化\飞针机' `
  --database-config .\dist\qms_erp_sync_config.json
```

首次写入会创建上述专用表。建议部署时使用具备这些表的 `SELECT`、`INSERT`、`UPDATE`、`CREATE TABLE`、`CREATE INDEX` 权限的受限 QMS 应用账号，而不是 MySQL `root`。
