@echo off
REM Run SimDock Pro 3.1 API Server
set PYTHONPATH=%~dp0

echo Starting SimDock Pro API Server...
echo Access Docs at: http://127.0.0.1:8000/docs
echo.

"C:\Users\user\Miniconda3\python.exe" -m uvicorn api.main:app --reload --host 127.0.0.1 --port 8000

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] API Server crashed.
    pause
)
