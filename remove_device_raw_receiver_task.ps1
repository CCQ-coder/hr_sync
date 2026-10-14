[CmdletBinding(SupportsShouldProcess = $true)]
param(
    [string]$PackageDirectory,
    [string]$TaskName = "DeviceRawReceiver"
)

$ErrorActionPreference = "Stop"
if ($TaskName -ne "DeviceRawReceiver") {
    throw "只允许管理 DeviceRawReceiver 计划任务"
}
if ($PSCmdlet.ShouldProcess($TaskName, "删除接收服务计划任务")) {
    & schtasks.exe /Delete /TN $TaskName /F
    if ($LASTEXITCODE -ne 0) {
        throw "删除计划任务失败，退出码: $LASTEXITCODE"
    }
}
