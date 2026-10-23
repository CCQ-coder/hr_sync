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
if not "%APP%"=="%APP: =%" (
    echo Install path contains spaces and has no short path. Use C:\IniShareSync.
    exit /b 2
)

start "" /wait "%APP%" --status-only >nul 2>&1
if errorlevel 1 (
    echo Status preflight failed. Check sync_config.json and the SCBGX share.
    exit /b 2
)

rem Keep the old task's account and trigger; XP cannot use schtasks /Create /F.
schtasks /Change /TN IniShareSync /TR "%APP%" >nul 2>&1
if errorlevel 1 (
    schtasks /Create /SC MINUTE /MO 5 /TN IniShareSync /TR "%APP%"
    if errorlevel 1 goto failed
)
schtasks /Change /TN IniShareSyncStatus /TR "%APP% --status-only" >nul 2>&1
if errorlevel 1 (
    schtasks /Create /SC MINUTE /MO 1 /TN IniShareSyncStatus /TR "%APP% --status-only"
    if errorlevel 1 goto failed
)
schtasks /Query /TN IniShareSyncStartup >nul 2>&1
if not errorlevel 1 (
    schtasks /Change /TN IniShareSyncStartup /TR "%APP%" >nul 2>&1
    if errorlevel 1 goto failed
)

echo Tasks ready. Existing schedules and accounts were preserved.
exit /b 0

:failed
echo Task setup failed. Existing tasks were not deleted.
exit /b 1
