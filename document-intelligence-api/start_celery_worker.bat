@echo off
title Celery Worker - Document Intelligence API

echo Starting Celery Worker...
echo.

REM Activate virtual environment if it exists
if exist "venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
)

echo Worker starting with configuration:
echo - Broker: %REDIS_URL%
echo - Concurrency: 1
echo - Log level: info
echo.

REM Start Celery worker
celery -A app.tasks.document_tasks worker -Q default --loglevel=info --concurrency=1

pause