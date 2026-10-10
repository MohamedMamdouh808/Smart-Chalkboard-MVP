@echo off
cd /d "%~dp0"

py -3.11 --version >nul 2>&1
if errorlevel 1 (
    echo Python 3.11 is required. Install it from python.org and tick "Add to PATH".
    pause
    exit /b 1
)

if not exist ".venv" py -3.11 -m venv .venv
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

if not exist ".env" copy ".env.example" ".env" >nul

echo.
echo Setup done. Open .env, paste your GROQ_API_KEY, then double-click start.bat
pause