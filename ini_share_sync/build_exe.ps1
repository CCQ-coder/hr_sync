$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSCommandPath
$python = (Get-Command python -ErrorAction Stop).Source
$entryPoint = Join-Path $projectRoot "run_ini_share_sync.py"
$distPath = Join-Path $projectRoot "dist"
$buildPath = Join-Path $projectRoot "build"
$env:PYINSTALLER_CONFIG_DIR = Join-Path $projectRoot ".tools\pyinstaller-cache-win64"

& $python -m PyInstaller --noconfirm --clean --onefile --name IniShareSync `
    --paths (Join-Path $projectRoot "src") `
    --distpath $distPath `
    --workpath $buildPath `
    --specpath $buildPath `
    $entryPoint

if ($LASTEXITCODE -ne 0) {
    throw "PyInstaller 打包失败，退出码：$LASTEXITCODE"
}

$configPath = Join-Path $projectRoot "sync_config.json"
Copy-Item -LiteralPath $configPath -Destination (Join-Path $distPath "sync_config.json") -Force

Write-Host "打包完成：$(Join-Path $distPath 'IniShareSync.exe')"
