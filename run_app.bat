@echo off
echo ==============================================================================
echo Launching CampusFind: Modern Web Application
echo ==============================================================================

cd /d "%~dp0"

IF EXIST ".venv\Scripts\python.exe" (
    echo Starting server with virtual environment...
    ".venv\Scripts\python.exe" server.py
) ELSE (
    echo Starting server with system Python...
    python server.py
)

pause
