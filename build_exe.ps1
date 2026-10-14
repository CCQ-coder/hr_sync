param(
    [switch]$Clean,
    [string]$Name = 'QMS-ERP数据同步工具-英文字段版'
)

$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Python = Join-Path $Root '.venv\Scripts\python.exe'
$Dist = Join-Path $Root 'dist'
$ReleaseHelper = Join-Path $Root 'prepare_release_package.py'
if (-not (Test-Path $Python)) {
    throw "未找到 $Python。请先执行：python -m venv .venv"
}
if (-not (Test-Path $ReleaseHelper)) {
    throw "未找到发布包白名单工具：$ReleaseHelper"
}

# Refuse a polluted release directory before building.  In particular, never
# mix a real qms_erp_sync_config.json or qms_erp_sync_state.json into a shareable package.
& $Python $ReleaseHelper '--root' $Root '--dist' $Dist '--exe-name' $Name '--validate-only'
if ($LASTEXITCODE -ne 0) { throw '发布目录安全检查失败。' }

& $Python -m pip install -r (Join-Path $Root 'requirements.txt')
if ($LASTEXITCODE -ne 0) { throw '依赖安装失败。' }

$arguments = @(
    '-m', 'PyInstaller', '--noconfirm', '--clean', '--onefile', '--windowed',
    '--name', $Name,
    '--specpath', (Join-Path $Root 'packaging\specs'),
    '--add-data', ((Join-Path $Root 'erp_field_registry.json') + ';.'),
    '--collect-submodules', 'openpyxl',
    '--collect-all', 'cryptography',
    (Join-Path $Root 'qms_erp_sync.py')
)
& $Python @arguments
if ($LASTEXITCODE -ne 0) { throw 'EXE 打包失败。' }

& $Python $ReleaseHelper '--root' $Root '--dist' $Dist '--exe-name' $Name
if ($LASTEXITCODE -ne 0) { throw '安全发布包生成失败。' }
Write-Host "已生成：$(Join-Path $Root ('dist\' + $Name + '.exe'))"
Write-Host "可分享的无敏感配置发布包：$(Join-Path $Dist ($Name + '-发布包'))"
