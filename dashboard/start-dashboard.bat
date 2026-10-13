@echo off
chcp 65001 >nul
title Dashboard - مدیریت هزینه
cd /d "%~dp0"

echo.
echo ========================================
echo   در حال اجرای داشبورد ...
echo ========================================
echo.
echo آدرس: http://127.0.0.1:8501
echo.

where streamlit >nul 2>&1
if errorlevel 1 (
    echo [خطا] streamlit نصب نیست.
    echo دستور: pip install -r requirements.txt
    pause
    exit /b 1
)

streamlit run app.py --server.address 127.0.0.1 --server.port 8501
pause
