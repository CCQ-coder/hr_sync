[CmdletBinding(SupportsShouldProcess = $true)]
param(
    [string]$PackageDirectory = (Split-Path -Parent $PSCommandPath),
    [string]$TaskName = "DeviceRawReceiver"
)

$ErrorActionPreference = "Stop"
if ($TaskName -ne "DeviceRawReceiver") {
    throw "只允许管理 DeviceRawReceiver 计划任务"
}

$packagePath = (Resolve-Path -LiteralPath $PackageDirectory -ErrorAction Stop).Path
$executable = Join-Path $packagePath "DeviceRawReceiver.exe"
$configuration = Join-Path $packagePath "device_receiver_config.json"
if (-not (Test-Path -LiteralPath $executable -PathType Leaf)) {
    throw "发布包中缺少 DeviceRawReceiver.exe"
}
if (-not (Test-Path -LiteralPath $configuration -PathType Leaf)) {
    throw "发布包中缺少实际配置 device_receiver_config.json"
}

$taskCommand = '"{0}" --config "{1}"' -f $executable, $configuration
if ($PSCmdlet.ShouldProcess($TaskName, "创建开机启动的 SYSTEM 接收任务")) {
    & schtasks.exe /Create /TN $TaskName /TR $taskCommand /SC ONSTART /RU SYSTEM /RL HIGHEST /F
    if ($LASTEXITCODE -ne 0) {
        throw "创建计划任务失败，退出码: $LASTEXITCODE"
    }
}
