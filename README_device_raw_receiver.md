# 标特福设备原始数据接收服务

本程序在 Windows 10 上监听一个局域网 TCP 端口，并把每条 TCP 连接收到的全部字节按原始顺序保存。它不会将接收缓冲、分卷或连接空闲误判为业务请求；首版不解析 `.rot`、不访问 QMS/MySQL，也不调用外部 API。

## 发布和配置

1. 在构建电脑的项目目录运行 `powershell -ExecutionPolicy Bypass -File .\build_device_raw_receiver.ps1`。
2. 将 `dist\DeviceRawReceiver` 整个目录复制到受控本机目录，例如 `D:\DeviceRawReceiver`。不要将接收数据目录放在临时目录、桌面同步盘或发布目录内。
3. 在部署目录将 `device_receiver_config.example.json` 复制为 `device_receiver_config.json`，填写设备实际要连接的 TCP 端口、保存路径和可信局域网 CIDR。不要把实际配置放回构建目录或发给他人。
4. 以管理员 PowerShell 在部署目录运行 ` .\install_device_raw_receiver_task.ps1`。可先使用 `-WhatIf` 演练。
5. 在 Windows 防火墙手动创建入站 TCP 规则，仅开放配置端口给相同的可信 CIDR。例如实际端口为 9100、网段为 `192.168.10.0/24` 时：

```powershell
New-NetFirewallRule -DisplayName "DeviceRawReceiver TCP 9100" -Direction Inbound -Action Allow -Protocol TCP -LocalPort 9100 -RemoteAddress 192.168.10.0/24
```

计划任务以 `SYSTEM` 账户在开机后运行。安装前确认该账户可创建 `storage_root` 中的目录和文件。

不带参数启动（包括双击 EXE）时，程序默认读取 EXE 同目录的 `device_receiver_config.json`。如果配置缺失或无效，程序不会开始监听，并在同目录追加 `startup-error.log` 以便排查。

## 原始数据目录

每条连接创建一个目录：

```text
<storage_root>\incoming\YYYY\MM\DD\<session-id>\
  session.json
  events.jsonl
  payload-000001.bin
```

将同一会话的 `payload-*.bin` 依名称顺序拼接，即为该 TCP 连接实际收到的原始字节流。`events.jsonl` 只记录偏移、长度和时间，不保存负载正文。异常中断或程序重启后，已有字节不变，会话会标记为 `interrupted`。

## 状态、日志与卸载

- 应用日志在 `<storage_root>\logs\receiver.log`，不会记录原始数据正文。
- 使用 `schtasks /Query /TN DeviceRawReceiver /V /FO LIST` 查看任务状态。
- 使用 ` .\remove_device_raw_receiver_task.ps1` 删除任务；它不会删除配置、日志或原始数据。可先使用 `-WhatIf`。

## 当前限制

设备的真实 TCP 帧格式尚未获得，因此不能从未知连续字节流推断“一个业务请求”的边界。拿到抓包或样本后，可在不改动 `payload-*.bin` 的前提下增加解析器、会话查询 API 或入库处理器。UDP、FTP、HTTP 服务和 `.rot` 参数解析不在此版本范围内。
