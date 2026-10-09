@echo off
chcp 65001 >nul
title Dashboard - Smart Expense Tracker
cd /d "%~dp0"

echo.
echo ========================================
echo   در حال اجرای داشبورد ...
echo ========================================
echo.
echo آدرس داشبورد: http://localhost:8501
echo.
echo برای توقف، Ctrl+C را بزنید.
echo.

streamlit run app.py
pause
