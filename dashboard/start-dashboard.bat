@echo off
chcp 65001 >nul
title Dashboard - Smart Expense Tracker
cd /d "%~dp0"

echo.
echo ========================================
echo   Starting Dashboard ...
echo ========================================
echo.
echo Address: http://127.0.0.1:8501
echo.
echo Press Ctrl+C to stop.
echo.

streamlit run app.py --server.address 127.0.0.1 --server.port 8501
pause
