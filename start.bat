@echo off
cd /d "%~dp0"

set PYTHONPATH=src;C:\sblibs
set SMARTBOARD_DEV_INPUT=1

py -3.11 -m smartboard.app.main

if errorlevel 1 (
    echo.
    echo The app closed with an error. Read the message above.
    pause
)