@echo on
setlocal

REM Ensure UTF-8 for logs
chcp 65001 >nul 2>&1
set "PYTHONUTF8=1"
set "PYTHONIOENCODING=utf-8"

REM Switch to repo root
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

echo [INFO] Launching API only (%_PY% -m app.api.run_api)...
if not exist "logs" mkdir "logs"
set "_LOG=logs\api_run.log"
echo ==== %DATE% %TIME% ==== > "%_LOG%"
"%_PY%" -m app.api.run_api 1>>"%_LOG%" 2>&1
set "_EXIT=%ERRORLEVEL%"

REM If launched by double-click (/c present), keep window open on exit
echo %CMDCMDLINE% | find /I "/c" >nul 2>&1
if not errorlevel 1 (
    echo.
    echo Press any key to close... (see %_LOG% for details)
    pause >nul
)

exit /b %_EXIT%
