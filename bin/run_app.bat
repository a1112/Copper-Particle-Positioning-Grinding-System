@echo off
setlocal

REM Ensure UTF-8 for logs
chcp 65001 >nul 2>&1
set "PYTHONUTF8=1"
set "PYTHONIOENCODING=utf-8"

REM Switch to script directory
cd /d "%~dp0\.."

REM Require system Python in PATH
where python >nul 2>&1
if errorlevel 1 (
    echo [ERROR] python.exe not found in PATH. Please install Python 3.11+ and add to PATH.
    exit /b 1
)

echo [INFO] Launching application (python -m app.main)...
python -m app.main
set "_EXIT=%ERRORLEVEL%"

REM If launched by double-click (/c present), keep window open on exit
echo %CMDCMDLINE% | find /I "/c" >nul 2>&1
if not errorlevel 1 (
    echo.
    echo Press any key to close...
    pause >nul
)

exit /b %_EXIT%

