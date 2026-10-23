@echo off
setlocal

if not exist "%~dp0IniShareSync.exe" (
    echo Missing IniShareSync.exe. Copy the whole package first.
    exit /b 2
)
if not exist "%~dp0sync_config.json" (
    echo Missing sync_config.json. Copy and edit sync_config.example.json first.
    exit /b 2
)

for %%I in ("%~dp0IniShareSync.exe") do set "APP=%%~sI"
if not exist "%APP%" (
    echo Cannot resolve the installed program path.
    exit /b 2
)

rem XP cannot use schtasks /Create /F; remove only this tool's task names first.
schtasks /Delete /TN IniShareSyncStartup /F >nul 2>&1
schtasks /Delete /TN IniShareSyncStatus /F >nul 2>&1
schtasks /Delete /TN IniShareSync /F >nul 2>&1

schtasks /Create /SC MINUTE /MO 5 /TN IniShareSync /TR "%APP%"
if errorlevel 1 goto failed
schtasks /Create /SC MINUTE /MO 1 /TN IniShareSyncStatus /TR "%APP% --status-only"
if errorlevel 1 goto failed

echo Installed: IniShareSync every 5 minutes; IniShareSyncStatus every 1 minute.
exit /b 0

:failed
echo Task setup failed. Run this file as the user who can write to the SCBGX share.
exit /b 1
