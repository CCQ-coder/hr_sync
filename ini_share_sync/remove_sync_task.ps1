[CmdletBinding(SupportsShouldProcess = $true)]
param(
    [string]$SchtasksPath = (Join-Path $env:WINDIR "System32\schtasks.exe")
)

$ErrorActionPreference = "Stop"
$taskName = "IniShareSync"
$startupTaskName = "IniShareSyncStartup"
$statusTaskName = "IniShareSyncStatus"

if (-not (Test-Path -LiteralPath $SchtasksPath -PathType Leaf)) {
    throw "未找到 Windows 计划任务工具：$SchtasksPath"
}

if ($PSCmdlet.ShouldProcess($taskName, "删除本工具创建的计划任务")) {
    foreach ($name in @($taskName, $startupTaskName, $statusTaskName)) {
        & $SchtasksPath /Query /TN $name | Out-Null
        if ($LASTEXITCODE -ne 0) {
            Write-Host "计划任务不存在：$name"
            continue
        }

        & $SchtasksPath /Delete /TN $name /F
        if ($LASTEXITCODE -ne 0) {
            throw "计划任务删除失败，schtasks 退出码：$LASTEXITCODE"
        }
        Write-Host "已删除计划任务：$name"
    }
}
