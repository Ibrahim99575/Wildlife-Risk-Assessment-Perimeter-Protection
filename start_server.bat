@echo off
REM Wildlife Risk Assessment System - Quick Start Script
REM This script starts the backend server

echo ============================================================
echo    Wildlife Risk Assessment System v2.0
echo    Starting Backend Server...
echo ============================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher
    pause
    exit /b 1
)

REM Check if dependencies are installed
echo Checking dependencies...
python -c "import flask" >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo WARNING: Dependencies not installed
    echo Installing dependencies...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
)

echo.
echo ============================================================
echo    Backend Server Starting...
echo    URL: http://localhost:5000
echo    Press Ctrl+C to stop the server
echo ============================================================
echo.

REM Create necessary directories
if not exist "logs" mkdir logs
if not exist "recordings" mkdir recordings
if not exist "snapshots" mkdir snapshots
if not exist "database" mkdir database
if not exist "uploads" mkdir uploads

REM Set Python path and start server
set PYTHONPATH=backend
python backend/app.py

pause
