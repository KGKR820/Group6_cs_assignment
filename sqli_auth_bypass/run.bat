@echo off
title SQL Injection - Authentication Bypass Lab (Port 5001)

echo ========================================================
echo   Setting up SQL Injection Lab for Windows
echo ========================================================
echo.

where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python is not found in your PATH!
    echo Please install Python from python.org and make sure to check "Add Python to PATH".
    pause
    exit /b 1
)

if not exist venv (
    echo [1/3] Creating virtual environment...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
) else (
    echo [1/3] Virtual environment already exists.
)

echo [2/3] Installing dependencies (Flask)...
call venv\Scripts\python.exe -m pip install -r requirements.txt --quiet

echo [3/3] Initializing SQLite database...
call venv\Scripts\python.exe init_db.py

echo.
echo ========================================================
echo   Lab Server is starting on http://127.0.0.1:5001
echo ========================================================
echo.
echo Opening browser in 2 seconds...
start "" http://127.0.0.1:5001/

echo Press Ctrl+C in this window anytime to stop the server.
echo.
call venv\Scripts\python.exe app.py

pause
