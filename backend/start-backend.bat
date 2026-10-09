@echo off
chcp 65001 >nul
title Backend - Smart Expense Tracker
cd /d "%~dp0"

echo.
echo ========================================
echo   Starting Backend Server ...
echo ========================================
echo.

if not exist "venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment not found!
    echo Run these commands once:
    echo   python -m venv venv
    echo   venv\Scripts\activate
    echo   pip install -r requirements.txt
    echo   python seed_demo_data.py
    pause
    exit /b 1
)

call venv\Scripts\activate.bat
echo Server running at: http://127.0.0.1:8000
echo Docs:              http://127.0.0.1:8000/docs
echo.
echo Press Ctrl+C to stop.
echo.

uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
pause
