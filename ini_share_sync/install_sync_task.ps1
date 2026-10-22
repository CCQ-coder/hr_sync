[CmdletBinding(SupportsShouldProcess = $true)]
param(
    [ValidateSet("dist", "dist-win32", "dist-xp32")]
    [string]$PackageDirectory = "dist",
    [string]$SchtasksPath = (Join-Path $env:WINDIR "System32\schtasks.exe")
)

$ErrorActionPreference = "Stop"
$taskName = "IniShareSync"
$startupTaskName = "IniShareSyncStartup"
$statusTaskName = "IniShareSyncStatus"
$projectRoot = Split-Path -Parent $PSCommandPath
$exeRelativePath = "$PackageDirectory\IniShareSync.exe"
if ($PackageDirectory -eq "dist-win32" -or $PackageDirectory -eq "dist-xp32") {
    $exeRelativePath = "$PackageDirectory\IniShareSync\IniShareSync.exe"
}
$exePath = Join-Path $projectRoot $exeRelativePath
$packageRoot = Split-Path -Parent $exePath

if (-not (Test-Path -LiteralPath $exePath -PathType Leaf)) {
    throw "未找到 $exePath。请先运行对应的打包脚本。"
}

if (-not (Test-Path -LiteralPath $SchtasksPath -PathType Leaf)) {
    throw "未找到 Windows 计划任务工具：$SchtasksPath"
}

if ($PSCmdlet.ShouldProcess($taskName, "创建或更新每 5 分钟执行一次的计划任务")) {
    if ($PackageDirectory -eq "dist-xp32") {
        # Windows XP has Task Scheduler 1.0: it cannot import the XML used by
        # the Windows 7 scheduler.  Its schtasks.exe supports this native form.
        $taskCommand = '"' + $exePath + '"'
        & $SchtasksPath /Create /SC MINUTE /MO 5 /TN $taskName /TR $taskCommand /F
        if ($LASTEXITCODE -ne 0) {
            throw "Windows XP 计划任务创建失败，schtasks 退出码：$LASTEXITCODE"
        }
        & $SchtasksPath /Create /SC ONSTART /TN $startupTaskName /TR $taskCommand /F
        if ($LASTEXITCODE -ne 0) {
            throw "Windows XP 开机同步任务创建失败，schtasks 退出码：$LASTEXITCODE"
        }
        $statusCommand = $taskCommand + ' --status-only'
        & $SchtasksPath /Create /SC MINUTE /MO 1 /TN $statusTaskName /TR $statusCommand /F
        if ($LASTEXITCODE -ne 0) {
            throw "Windows XP 状态采集任务创建失败，schtasks 退出码：$LASTEXITCODE"
        }
        Write-Host "Windows XP 计划任务已创建或更新：$taskName"
        return
    }

    $xmlEscape = {
        param([string]$Value)
        return [System.Security.SecurityElement]::Escape($Value)
    }
    $currentUser = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
    $startBoundary = (Get-Date).AddMinutes(1).ToString("yyyy-MM-dd'T'HH:mm:ss")
    $xml = @"
<?xml version="1.0" encoding="UTF-8"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Description>INI LAN share synchronization</Description>
  </RegistrationInfo>
  <Triggers>
    <CalendarTrigger>
      <StartBoundary>$startBoundary</StartBoundary>
      <Enabled>true</Enabled>
      <Repetition>
        <Interval>PT5M</Interval>
        <Duration>P1D</Duration>
        <StopAtDurationEnd>false</StopAtDurationEnd>
      </Repetition>
      <ScheduleByDay>
        <DaysInterval>1</DaysInterval>
      </ScheduleByDay>
    </CalendarTrigger>
  </Triggers>
  <Principals>
    <Principal id="Author">
      <UserId>$(& $xmlEscape $currentUser)</UserId>
      <LogonType>InteractiveToken</LogonType>
      <RunLevel>LeastPrivilege</RunLevel>
    </Principal>
  </Principals>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <AllowHardTerminate>true</AllowHardTerminate>
    <StartWhenAvailable>true</StartWhenAvailable>
    <RunOnlyIfNetworkAvailable>false</RunOnlyIfNetworkAvailable>
    <AllowStartOnDemand>true</AllowStartOnDemand>
    <Enabled>true</Enabled>
    <Hidden>false</Hidden>
    <RunOnlyIfIdle>false</RunOnlyIfIdle>
    <WakeToRun>false</WakeToRun>
    <ExecutionTimeLimit>PT0S</ExecutionTimeLimit>
    <Priority>7</Priority>
  </Settings>
  <Actions Context="Author">
    <Exec>
      <Command>$(& $xmlEscape $exePath)</Command>
      <WorkingDirectory>$(& $xmlEscape $packageRoot)</WorkingDirectory>
    </Exec>
  </Actions>
</Task>
"@

    $statusXml = $xml.Replace("<Interval>PT5M</Interval>", "<Interval>PT1M</Interval>").Replace(
        "</Command>",
        "</Command>`n      <Arguments>--status-only</Arguments>"
    )

    $xmlPath = [System.IO.Path]::GetTempFileName()
    try {
        foreach ($task in @(@{ Name = $taskName; Xml = $xml }, @{ Name = $statusTaskName; Xml = $statusXml })) {
            Set-Content -LiteralPath $xmlPath -Value $task.Xml -Encoding UTF8
            & $SchtasksPath /Create /TN $task.Name /XML $xmlPath /F
            if ($LASTEXITCODE -ne 0) {
                throw "计划任务创建失败：$($task.Name)，schtasks 退出码：$LASTEXITCODE"
            }
            Write-Host "计划任务已创建或更新：$($task.Name)"
        }
    }
    finally {
        Remove-Item -LiteralPath $xmlPath -Force -ErrorAction SilentlyContinue
    }
}
