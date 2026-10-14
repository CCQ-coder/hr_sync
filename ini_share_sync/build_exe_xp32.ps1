$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSCommandPath
$python = Join-Path $projectRoot ".tools\python34-x86\python.exe"
$entryPoint = Join-Path $projectRoot "run_ini_share_sync.py"
$distPath = Join-Path $projectRoot "dist-xp32"
$buildPath = Join-Path $projectRoot "build-xp32"
$bundlePath = Join-Path $distPath "IniShareSync"
$env:PYINSTALLER_CONFIG_DIR = Join-Path $projectRoot ".tools\pyinstaller-cache-xp32"

if (-not (Test-Path -LiteralPath $python -PathType Leaf)) {
    throw "未找到 XP 打包所需的 32 位 Python 3.4：$python"
}

$pointerBits = (& $python -c "import struct; print(struct.calcsize('P') * 8)").Trim()
if ($pointerBits -ne "32") {
    throw "构建解释器必须是 32 位 Python，实际为：$pointerBits 位"
}

& $python -m PyInstaller --noconfirm --clean --onedir --noconsole --name IniShareSync `
    --paths (Join-Path $projectRoot "src") `
    --distpath $distPath `
    --workpath $buildPath `
    --specpath $buildPath `
    $entryPoint

if ($LASTEXITCODE -ne 0) {
    throw "Windows XP 32 位 PyInstaller 打包失败，退出码：$LASTEXITCODE"
}

$configPath = Join-Path $projectRoot "sync_config.json"
Copy-Item -LiteralPath $configPath -Destination (Join-Path $bundlePath "sync_config.json") -Force

$executablePath = Join-Path $bundlePath "IniShareSync.exe"
$executableBytes = [System.IO.File]::ReadAllBytes($executablePath)
$peOffset = [System.BitConverter]::ToInt32($executableBytes, 0x3C)
$machine = [System.BitConverter]::ToUInt16($executableBytes, $peOffset + 4)
if ($machine -ne 0x014C) {
    throw "打包产物不是 x86 PE 文件，Machine=0x$($machine.ToString('X4'))"
}

Write-Host "Windows XP 32 位打包完成：$executablePath"
