@echo off
setlocal

chcp 65001 >nul 2>&1
set "PYTHONUTF8=1"
set "PYTHONIOENCODING=utf-8"

cd /d "%~dp0\.."

REM Resolve Python interpreter: prefer E:\Python313, then E:\Python311, else PATH
set "_PY="
if exist "E:\Python313\python.exe" set "_PY=E:\Python313\python.exe"
if not defined _PY if exist "E:\Python311\python.exe" set "_PY=E:\Python311\python.exe"
if not defined _PY for /f "delims=" %%P in ('where python 2^>nul') do ( set "_PY=%%P" & goto :py_found )
:py_found
if not defined _PY (
    echo [ERROR] python.exe not found. Please install Python 3.11+.
    exit /b 1
)

echo [INFO] Using Python: %_PY%
echo [INFO] Exporting LZPP paths to logs\exports (JSON + CSV)
"%_PY%" scripts/export_lzpp_from_log.py %*
set "_EXIT=%ERRORLEVEL%"

echo.
echo Press any key to close...
pause >nul

exit /b %_EXIT%

