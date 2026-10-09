@echo off
chcp 65001 >nul
title Backend - Smart Expense Tracker
cd /d "%~dp0"

echo.
echo ========================================
echo   در حال اجرای سرور Backend ...
echo ========================================
echo.

if not exist "venv\Scripts\activate.bat" (
    echo [خطا] محیط مجازی پیدا نشد!
    echo اول این دستورات را یکبار اجرا کن:
    echo   python -m venv venv
    echo   venv\Scripts\activate
    echo   pip install -r requirements.txt
    echo   python seed_demo_data.py
    pause
    exit /b 1
)

call venv\Scripts\activate.bat
echo سرور در آدرس زیر اجرا می‌شود:
echo http://127.0.0.1:8000
echo.
echo برای توقف، Ctrl+C را بزنید.
echo.

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
pause
