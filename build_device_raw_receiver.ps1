[CmdletBinding()]
param(
    [string]$PythonPath
)

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSCommandPath
$distRoot = Join-Path $projectRoot "dist"
$releasePath = Join-Path $distRoot "DeviceRawReceiver"
$stagingPath = Join-Path $distRoot "DeviceRawReceiver.staging"
$workPath = Join-Path $projectRoot "build\DeviceRawReceiver"
$pyInstallerHome = Join-Path $projectRoot ".tools\pyinstaller-home"

if ([string]::IsNullOrWhiteSpace($PythonPath)) {
    $virtualEnvironmentPython = Join-Path $projectRoot ".venv\Scripts\python.exe"
    if (Test-Path -LiteralPath $virtualEnvironmentPython -PathType Leaf) {
        $PythonPath = $virtualEnvironmentPython
    } else {
        $PythonPath = (Get-Command python -ErrorAction Stop).Source
    }
}

if (-not (Test-Path -LiteralPath $PythonPath -PathType Leaf)) {
    throw "未找到 Python: $PythonPath"
}
if (Test-Path -LiteralPath (Join-Path $releasePath "device_receiver_config.json") -PathType Leaf) {
    throw "发布目录含有实际配置，拒绝覆盖: $releasePath"
}
if (Test-Path -LiteralPath $releasePath) {
    throw "发布目录已存在。请先确认其内容安全后手动移走: $releasePath"
}
if (Test-Path -LiteralPath $stagingPath) {
    throw "发现未完成的暂存目录，请先检查后手动移走: $stagingPath"
}

New-Item -ItemType Directory -Path $distRoot -Force | Out-Null
New-Item -ItemType Directory -Path $stagingPath -Force | Out-Null
New-Item -ItemType Directory -Path $pyInstallerHome -Force | Out-Null
$env:PYINSTALLER_CONFIG_DIR = $pyInstallerHome
$env:USERPROFILE = $pyInstallerHome
$env:PYTHONUSERBASE = $pyInstallerHome

Push-Location $projectRoot
try {
    & $PythonPath -m PyInstaller --noconfirm --clean --distpath $stagingPath --workpath $workPath `
        (Join-Path $projectRoot "packaging\specs\DeviceRawReceiver.spec")
    if ($LASTEXITCODE -ne 0) {
        throw "PyInstaller 打包失败，退出码: $LASTEXITCODE"
    }
} finally {
    Pop-Location
}

$allowlist = @(
    "DeviceRawReceiver.exe",
    "device_receiver_config.example.json",
    "install_device_raw_receiver_task.ps1",
    "remove_device_raw_receiver_task.ps1",
    "README_device_raw_receiver.md"
)
$sourceFiles = @{
    "DeviceRawReceiver.exe" = (Join-Path $stagingPath "DeviceRawReceiver.exe")
    "device_receiver_config.example.json" = (Join-Path $projectRoot "device_receiver_config.example.json")
    "install_device_raw_receiver_task.ps1" = (Join-Path $projectRoot "install_device_raw_receiver_task.ps1")
    "remove_device_raw_receiver_task.ps1" = (Join-Path $projectRoot "remove_device_raw_receiver_task.ps1")
    "README_device_raw_receiver.md" = (Join-Path $projectRoot "docs\guides\README_device_raw_receiver.md")
}
foreach ($name in $allowlist) {
    if (-not (Test-Path -LiteralPath $sourceFiles[$name] -PathType Leaf)) {
        throw "打包所需文件不存在: $name"
    }
    $destination = Join-Path $stagingPath $name
    if (([System.IO.Path]::GetFullPath($sourceFiles[$name])) -ne ([System.IO.Path]::GetFullPath($destination))) {
        Copy-Item -LiteralPath $sourceFiles[$name] -Destination $destination
    }
}
if (Test-Path -LiteralPath (Join-Path $stagingPath "device_receiver_config.json") -PathType Leaf) {
    throw "暂存目录含有实际配置，拒绝发布"
}

Move-Item -LiteralPath $stagingPath -Destination $releasePath
Write-Host "已生成干净发布包: $releasePath"
