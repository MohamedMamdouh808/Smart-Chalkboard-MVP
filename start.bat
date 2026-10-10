@echo off
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo Run setup.bat first.
    pause
    exit /b 1
)

set PYTHONPATH=src
.venv\Scripts\python.exe -m smartboard.app.main

if errorlevel 1 (
    echo.
    echo The app closed with an error. Read the message above.
    pause
)