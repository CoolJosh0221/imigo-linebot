@echo off
REM Development startup script for IMIGO LINE Bot (Windows)
REM This script:
REM 1. Starts ngrok in the background
REM 2. Waits for ngrok to be ready
REM 3. Automatically updates the LINE webhook URL
REM 4. Starts the FastAPI development server

echo ========================================
echo IMIGO LINE Bot - Development Startup
echo ========================================

REM Check if .env file exists
if not exist .env (
    echo Error: .env file not found
    echo Please create .env file from .env.example
    pause
    exit /b 1
)

REM Kill any existing ngrok processes
echo.
echo Cleaning up existing ngrok processes...
taskkill /F /IM ngrok.exe >nul 2>&1
timeout /t 2 >nul

REM Start ngrok in the background
echo.
echo Starting ngrok tunnel...
start /B ngrok http 8000
timeout /t 5

REM Update LINE webhook
echo.
echo Updating LINE webhook URL...
python scripts\update_line_webhook.py

if %ERRORLEVEL% neq 0 (
    echo Failed to update webhook
    taskkill /F /IM ngrok.exe >nul 2>&1
    pause
    exit /b 1
)

REM Start the FastAPI server
echo.
echo Starting FastAPI server...
echo ========================================
echo Development environment ready!
echo ========================================
echo FastAPI: http://localhost:8000
echo ngrok Inspector: http://localhost:4040
echo API Docs: http://localhost:8000/api/docs
echo ========================================
echo Press Ctrl+C to stop
echo.

python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
