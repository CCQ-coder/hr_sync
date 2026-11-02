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

rem Keep the old task's account and trigger; XP cannot use schtasks /Create /F.
echo Setting up IniShareSync...
if exist "%WINDIR%\Tasks\IniShareSync.job" (
    schtasks /Change /TN IniShareSync /TR "%APP%"
) else (
    schtasks /Create /SC MINUTE /MO 5 /TN IniShareSync /TR "%APP%"
)
if errorlevel 1 goto failed
echo Setting up IniShareSyncStatus...
if exist "%WINDIR%\Tasks\IniShareSyncStatus.job" (
    schtasks /Change /TN IniShareSyncStatus /TR "%APP% --status-only"
) else (
    schtasks /Create /SC MINUTE /MO 1 /TN IniShareSyncStatus /TR "%APP% --status-only"
)
if errorlevel 1 goto failed
if exist "%WINDIR%\Tasks\IniShareSyncStartup.job" (
    echo Updating IniShareSyncStartup...
    schtasks /Change /TN IniShareSyncStartup /TR "%APP%"
    if errorlevel 1 goto failed
)

echo Tasks ready. Existing schedules and accounts were preserved.
exit /b 0

:failed
echo Task setup failed. Existing tasks were not deleted.
exit /b 1
