# INI 局域网同步工具

该工具每次运行时扫描 `D:\WTD\JOBS` 的第一层任务目录。仅当子目录 `<任务名>` 中存在同名文件 `<任务名>.ini` 时，才会把它的原始字节复制为：

```text
\\Scbgx\数字化\飞针机\<设备编号>\<任务名>.txt
```

它不递归扫描更深的目录，不同步其它文件；源文件删除也不会删除共享目录中的既有 TXT。首次运行传输所有符合规则的文件，之后仅在文件内容发生变化时同步。

每次上传成功后，目标 TXT 的创建时间和修改时间都会与源 INI 保持一致；源内容未变时不会重新复制或修改目标时间。

## 1. 配置

编辑同目录的 [sync_config.json](sync_config.json)：

```json
{
  "source_root": "D:\\WTD\\JOBS",
  "target_root": "\\\\Scbgx\\数字化\\飞针机",
  "device_id": "飞针机01"
}
```

将 `device_id` 改为本机实际设备编号。每台飞针机必须使用不同编号；忽略首尾空格和英文大小写后仍须唯一，并在 QMS 设备网关映射中绑定到对应设备。编号会成为共享目录下的子文件夹名，不能使用 Windows 保留名称（如 `CON`、`AUX`）、尾部句点或文件名禁用字符。`target_root` 必须保持 UNC 共享路径，不要改为映射盘符。

运行计划任务的 Windows 账户必须有权限创建并写入 `\\Scbgx\数字化\飞针机\<设备编号>`。可先在资源管理器用同一账户打开该共享目录并创建一个测试文件，确认网络和权限都正常。

## 2. 手动运行

在此目录打开 PowerShell，执行：

```powershell
$env:PYTHONPATH = "$PWD\src"
python -m ini_share_sync.main
```

每次执行结束后会退出。也可使用 `python .\run_ini_share_sync.py` 运行同一命令。日志保存在 `logs\sync-YYYY-MM-DD.log`；每个成功同步的文件会在 `sync_state.json` 中记录 SHA-256 指纹和成功时间。共享目录临时不可用或写入失败时，该文件不会被标记为成功，下一次运行会自动重试。

仅采集本机电脑状态可运行 `python -m ini_share_sync.main --status-only`，打包后运行 `IniShareSync.exe --status-only`。它不读取 `D:\WTD\JOBS`，而是每次更新共享目录中的 `<设备编号>\host-status.json`；文件只包含本机 CPU、内存、系统盘、开机时长及采样时间，不含 QMS 凭据。状态日志写在 `logs\host-status-YYYY-MM-DD.log`。SCBGX 监听程序会读取该文件并转发到 QMS。

## 3. 打包与安装每 5 分钟任务

先完成配置，然后打包：

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\build_exe.ps1
```

成功后会生成 `dist\IniShareSync.exe`，并把当前的 `sync_config.json` 复制到同一目录。计划任务和 EXE 都读取这份 `dist\sync_config.json`；修改配置后请再次运行 `build_exe.ps1`。接着创建或更新文件同步及状态采集计划任务：

```powershell
.\install_sync_task.ps1
```

## Windows 7 32 位版本

若目标电脑是 32 位 Windows 7，在构建电脑运行：

```powershell
.\build_exe_win32.ps1
```

该脚本使用项目内的 32 位 Python 3.8.10 打包，产物位于 `dist-win32\IniShareSync\IniShareSync.exe`，并检查 EXE 的 PE 架构为 x86。该版本是文件夹包，Python 运行时文件已放在 EXE 同目录，启动时不再向 Windows 临时目录解压，适用于遇到 `fopen: Permission denied` 的 Win7 电脑。配置文件位于 `dist-win32\IniShareSync\sync_config.json`；创建计划任务时指定 Win32 包：

```powershell
.\install_sync_task.ps1 -PackageDirectory dist-win32
```

部署到 Windows 7 时，完整复制 `dist-win32` 文件夹（不要只复制 EXE），以及 `install_sync_task.ps1`、`remove_sync_task.ps1` 和本说明即可。新电脑不需要安装 Python。

安装和卸载脚本使用 Windows 自带的 `schtasks.exe`，兼容 Windows 7。`IniShareSync` 每 5 分钟同步文件；独立的 `IniShareSyncStatus` 每 1 分钟采集状态，上一轮尚未结束时忽略新的状态运行请求。任务设置为“用户登录时运行”；请保持该账户已登录，才能让计划任务按时执行。

## Windows XP 32 位版本

若目标机实际是 Windows XP（桌面为蓝天草地样式，或报错 `DeleteProcThreadAttributeList` / `KERNEL32.dll`），不能使用上面的 Win7 包。请在构建电脑执行：

```powershell
.\build_exe_xp32.ps1
```

该脚本使用项目内的 32 位 Python 3.4 和 PyInstaller 3.4，生成 XP 可启动的文件夹包：`dist-xp32\IniShareSync\IniShareSync.exe`。EXE 使用静默模式，双击和计划任务执行时不显示黑色窗口；日志仍保存在同目录的 `logs` 文件夹。请完整复制 `dist-xp32` 文件夹，不能只复制 EXE；目标电脑无需安装 Python。

编辑 `dist-xp32\IniShareSync\sync_config.json` 中的 `device_id` 后，在部署目录运行：

```powershell
.\install_sync_task.ps1 -PackageDirectory dist-xp32
```

XP 自带的是旧版计划任务，安装脚本会创建三个任务：`IniShareSync` 每 5 分钟同步文件，`IniShareSyncStartup` 在电脑启动时同步一次，`IniShareSyncStatus` 每 1 分钟采集状态。它们以执行安装命令的当前 Windows 账户运行。因此该账户需保持登录，且必须对共享目录有写入权限。若刚开机时网络共享尚未可用，会记录失败，下一次计划任务会重试。XP 的开机时长计数约每 49.7 天回绕一次，此时 QMS 显示的开机时长会重新从零计起。

若 XP 没有安装 PowerShell，可在管理员 CMD 中进入部署目录后直接创建任务（将示例路径替换为实际路径）：

```bat
schtasks /Create /SC MINUTE /MO 5 /TN IniShareSync /TR D:\ini_share_sync\dist-xp32\IniShareSync\IniShareSync.exe /F
schtasks /Create /SC ONSTART /TN IniShareSyncStartup /TR D:\ini_share_sync\dist-xp32\IniShareSync\IniShareSync.exe /F
schtasks /Create /SC MINUTE /MO 1 /TN IniShareSyncStatus /TR "D:\ini_share_sync\dist-xp32\IniShareSync\IniShareSync.exe --status-only" /F
```

需要删除该任务时运行：

```bat
schtasks /Delete /TN IniShareSync /F
schtasks /Delete /TN IniShareSyncStartup /F
schtasks /Delete /TN IniShareSyncStatus /F
```

安装前可进行无修改演练：

```powershell
.\install_sync_task.ps1 -WhatIf
```

## 4. 一键删除计划任务

执行以下命令即可删除本工具创建的计划任务：

```powershell
.\remove_sync_task.ps1
```

它会移除每 5 分钟文件同步、开机同步和每 1 分钟状态采集任务；不会删除配置、日志、状态文件、源 INI、共享目录中的 TXT 或 `host-status.json`。要回退设备端程序，先卸载任务，再恢复备份的 EXE 包和配置，最后用旧版脚本重装原任务。删除前同样可以使用 `-WhatIf` 预览：

```powershell
.\remove_sync_task.ps1 -WhatIf
```

## 常见问题

- **日志显示共享目录不可访问**：检查 `Scbgx` 是否能解析、局域网连接是否正常，以及当前账户是否有共享目录写入权限。
- **文件没有同步**：确认文件位于 `D:\WTD\JOBS` 的第一层子目录内，且 INI 文件名和子目录名完全相同（扩展名大小写不敏感）。
- **需要重新全量同步**：在确认允许覆盖远端 TXT 后，停止任务并删除本工具目录内的 `sync_state.json`，然后手动运行一次；这不会删除远端文件。
