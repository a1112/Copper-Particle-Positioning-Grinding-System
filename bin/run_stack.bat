@echo on
setlocal EnableDelayedExpansion

REM Ensure UTF-8 output
chcp 65001 >nul 2>&1
set "PYTHONUTF8=1"
set "PYTHONIOENCODING=utf-8"

REM Resolve project root (one level above /bin)
set "SCRIPT_DIR=%~dp0"
set "ROOT_DIR=%SCRIPT_DIR%.."
for %%I in ("%ROOT_DIR%") do set "ROOT_DIR=%%~fI"
cd /d "%ROOT_DIR%"

REM Locate Python interpreter (prefer E:\Python313)
set "_PYTHON="
if exist "E:\Python313\python.exe" (
    set "_PYTHON=E:\Python313\python.exe"
) else (
    for /f "delims=" %%P in ('where python 2^>nul') do (
        set "_PYTHON=%%P"
        goto :py_found
    )
)
:py_found
if not defined _PYTHON (
    echo [ERROR] python.exe not found. Please install Python 3.11+ or update PATH.
    exit /b 1
)
echo [INFO] Using Python: %_PYTHON%

REM Prepare logs directory
if not exist "logs" mkdir "logs"

set "API_TITLE=API Server"
set "HTTP_TITLE=HTTP Prod Bridge"
set "UI_TITLE=UI Main"

echo [INFO] Launching %API_TITLE%
start "%API_TITLE%" cmd /k "pushd "%ROOT_DIR%" && "%_PYTHON%" -m app.server.run_api"

echo [INFO] Launching %HTTP_TITLE%
start "%HTTP_TITLE%" cmd /k "pushd "%ROOT_DIR%" && "%_PYTHON%" -m app.controller.http_prod"

echo [INFO] Launching %UI_TITLE%
start "%UI_TITLE%" cmd /k "pushd "%ROOT_DIR%" && "%_PYTHON%" -m app.ui.main"

echo.
echo [INFO] Launch commands issued. Each component is running in its own window.
echo [INFO] Close this window to finish. Child windows stay active until you exit them.

