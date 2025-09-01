@echo off
REM Production start script for YouTube Converter (Windows)

echo Starting YouTube Converter in production mode...

REM Check if .env file exists
if not exist ".env" (
    echo Error: .env file not found!
    echo Please copy .env.example to .env and configure your API keys.
    pause
    exit /b 1
)

REM Load environment variables from .env file
for /f "usebackq tokens=1,2 delims==" %%a in (".env") do (
    if not "%%a"=="" if not "%%a:~0,1"=="#" set "%%a=%%b"
)

REM Check required environment variables
if "%RAPIDAPI_KEY%"=="" (
    echo Error: RAPIDAPI_KEY not found in .env file!
    echo Please set RAPIDAPI_KEY in your .env file.
    pause
    exit /b 1
)

if "%APPIFY_TOKEN%"=="" (
    echo Error: APPIFY_TOKEN not found in .env file!
    echo Please set APPIFY_TOKEN in your .env file.
    pause
    exit /b 1
)

REM Create downloads directory if it doesn't exist
if not exist "downloads" mkdir downloads

REM Set default values if not provided
if "%FLASK_ENV%"=="" set FLASK_ENV=production
if "%HOST%"=="" set HOST=0.0.0.0
if "%PORT%"=="" set PORT=5000
if "%WORKERS%"=="" set WORKERS=4
if "%TIMEOUT%"=="" set TIMEOUT=120
if "%LOG_LEVEL%"=="" set LOG_LEVEL=INFO

echo Configuration:
echo   Environment: %FLASK_ENV%
echo   Host: %HOST%
echo   Port: %PORT%
echo   Workers: %WORKERS%
echo   Timeout: %TIMEOUT% seconds
echo   Log Level: %LOG_LEVEL%
echo.

REM Start the application with Gunicorn
echo Starting Gunicorn server...
gunicorn --bind %HOST%:%PORT% --workers %WORKERS% --timeout %TIMEOUT% --log-level %LOG_LEVEL% --access-logfile - --error-logfile - --preload --max-requests 1000 --max-requests-jitter 100 app:app

if errorlevel 1 (
    echo.
    echo Error: Failed to start the server!
    echo Make sure you have installed all requirements: pip install -r requirements.txt
    pause
)