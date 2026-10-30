param(
    [switch]$DryRun,
    [switch]$Install
)

$ErrorActionPreference = 'Stop'
$taskName = 'TempCleanup80'
$workDir = Join-Path $env:LOCALAPPDATA $taskName
New-Item -ItemType Directory -Path $workDir -Force | Out-Null
$logPath = Join-Path $workDir 'cleanup.log'

function Write-Log([string]$message) {
    $line = '{0} {1}' -f (Get-Date -Format s), $message
    Add-Content -LiteralPath $logPath -Value $line
    Write-Output $line
}

if ($Install) {
    $scriptPath = $MyInvocation.MyCommand.Path
    $action = New-ScheduledTaskAction -Execute (Join-Path $PSHOME 'powershell.exe') -Argument ('-NoProfile -ExecutionPolicy Bypass -File "{0}"' -f $scriptPath)
    $trigger = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(5) -RepetitionInterval (New-TimeSpan -Minutes 10) -RepetitionDuration (New-TimeSpan -Days 3650)
    $principal = New-ScheduledTaskPrincipal -UserId ([Security.Principal.WindowsIdentity]::GetCurrent().Name) -LogonType Interactive -RunLevel Limited
    $settings = New-ScheduledTaskSettingsSet -MultipleInstances IgnoreNew -StartWhenAvailable -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
    Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Force | Out-Null
    Write-Log "installed 10-minute task for $($principal.UserId): $scriptPath"
    return
}

try {
    $temp = [IO.Path]::GetFullPath($env:TEMP).TrimEnd('\')
    $expectedTemp = (Join-Path $env:LOCALAPPDATA 'Temp').TrimEnd('\')
    if (-not $temp.Equals($expectedTemp, [StringComparison]::OrdinalIgnoreCase) -or
        -not (Test-Path -LiteralPath $temp -PathType Container) -or
        ((Get-Item -LiteralPath $temp).Attributes -band [IO.FileAttributes]::ReparsePoint)) {
        throw "Unsafe TEMP path: $temp"
    }

    $root = [IO.Path]::GetPathRoot($temp)
    $disk = [IO.DriveInfo]::new($root)
    $used = 100 * (1 - $disk.AvailableFreeSpace / $disk.TotalSize)
    if ($used -lt 80 -and -not $DryRun) {
        Write-Log ('skip: {0} used {1:N1}% (<80%)' -f $root, $used)
        return
    }

    $removed = 0
    $skippedLocked = 0
    $skippedRuntime = 0
    $bytes = [long]0
    $dirs = New-Object 'System.Collections.Generic.List[string]'
    $pending = New-Object 'System.Collections.Generic.Stack[string]'
    $pending.Push($temp)

    while ($pending.Count -gt 0) {
        $folder = $pending.Pop()
        foreach ($item in Get-ChildItem -LiteralPath $folder -Force -ErrorAction SilentlyContinue) {
            if ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) { continue }
            if ($item.PSIsContainer) {
                # A running PyInstaller app can read unlocked files from this directory later.
                if ($folder -eq $temp -and $item.Name -match '^_MEI[0-9]+$') { $skippedRuntime++; continue }
                $dirs.Add($item.FullName)
                $pending.Push($item.FullName)
                continue
            }
            $stream = $null
            try {
                $stream = [IO.File]::Open($item.FullName, [IO.FileMode]::Open, [IO.FileAccess]::Read, [IO.FileShare]::None)
            } catch { $skippedLocked++; continue }
            finally { if ($stream) { $stream.Dispose() } }
            if ($DryRun) { $removed++; $bytes += $item.Length; continue }
            try {
                Remove-Item -LiteralPath $item.FullName -Force -ErrorAction Stop
                $removed++
                $bytes += $item.Length
            } catch { $skippedLocked++ }
        }
    }

    if (-not $DryRun) {
        foreach ($folder in $dirs | Sort-Object Length -Descending) {
            try { [IO.Directory]::Delete($folder, $false) } catch { } # Empty folders only.
        }
        try {
            Clear-RecycleBin -Force -ErrorAction Stop
            Write-Log 'current-user Recycle Bin cleared'
        } catch {
            Write-Log ("Recycle Bin cleanup failed: {0}" -f $_.Exception.Message)
        }
    }

    $after = [IO.DriveInfo]::new($root)
    $afterUsed = 100 * (1 - $after.AvailableFreeSpace / $after.TotalSize)
    $mode = if ($DryRun) { 'dry-run' } else { 'clean' }
    Write-Log ('{0}: {1} used {2:N1}% -> {3:N1}%; files {4}; bytes {5}; locked/inaccessible skipped {6}; runtime directories skipped {7}' -f $mode, $root, $used, $afterUsed, $removed, $bytes, $skippedLocked, $skippedRuntime)
} catch {
    Write-Log ("FAILED: {0}" -f $_.Exception.Message)
    throw
}
