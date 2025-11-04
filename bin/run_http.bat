@echo on
setlocal

chcp 65001 >nul 2>&1
set "PYTHONUTF8=1"
set "PYTHONIOENCODING=utf-8"

set "SCRIPT_DIR=%~dp0"
set "ROOT_DIR=%SCRIPT_DIR%.."
for %%I in ("%ROOT_DIR%") do set "ROOT_DIR=%%~fI"
cd /d "%ROOT_DIR%"

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

if not exist "logs" mkdir "logs"

pushd "%ROOT_DIR%"
"%_PYTHON%" -m app.controller.http_prod
set "EXIT_CODE=%ERRORLEVEL%"
popd

if %EXIT_CODE% neq 0 (
    echo.
    echo [ERROR] HTTP Prod exited with code %EXIT_CODE%.
) else (
    echo.
    echo [INFO] HTTP Prod exited normally.
)

echo.
echo Press any key to close...
pause >nul
exit /b %EXIT_CODE%
