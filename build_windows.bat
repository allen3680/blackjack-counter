@echo off
REM Build script for Windows users
REM 建立 Blackjack Counter Windows 執行檔

echo === Blackjack Counter Windows Build ===
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.8 or later
    pause
    exit /b 1
)

REM Run the build script
python build_windows.py

pause