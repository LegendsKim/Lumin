@echo off
REM Lumin Development Setup Script for Windows
REM This script automates the setup of Docker containers and Django backend

echo.
echo ========================================
echo   Lumin Development Setup (Windows)
echo   Setting up Docker + Django
echo ========================================
echo.

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not running!
    echo Please start Docker Desktop and try again.
    pause
    exit /b 1
)

echo [1/6] Starting Docker containers...
docker-compose up -d
if errorlevel 1 (
    echo [ERROR] Failed to start Docker containers
    pause
    exit /b 1
)

echo [2/6] Waiting for services to be ready...
timeout /t 10 /nobreak >nul

echo [3/6] Checking PostgreSQL health...
docker exec lumin-postgres pg_isready -U lumin_user >nul 2>&1
if errorlevel 1 (
    echo [WARNING] PostgreSQL not ready yet, waiting...
    timeout /t 5 /nobreak >nul
)

echo [4/6] Creating database (if not exists)...
docker exec lumin-postgres psql -U lumin_user -tc "SELECT 1 FROM pg_database WHERE datname = 'lumin_db'" | findstr /C:"1" >nul
if errorlevel 1 (
    docker exec lumin-postgres psql -U lumin_user -c "CREATE DATABASE lumin_db;"
    echo Database 'lumin_db' created successfully!
) else (
    echo Database 'lumin_db' already exists.
)

echo [5/6] Running Django migrations...
cd lumin-backend
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
    python manage.py migrate
    if errorlevel 1 (
        echo [ERROR] Migrations failed
        pause
        exit /b 1
    )
) else (
    echo [WARNING] Virtual environment not found at lumin-backend\venv
    echo Please create it with: python -m venv venv
    echo Then run: venv\Scripts\activate.bat
    echo And: pip install -r requirements.txt
)

echo.
echo [6/6] Setup complete!
echo.
echo ========================================
echo   Services Status:
echo ========================================
docker-compose ps

echo.
echo ========================================
echo   Next Steps:
echo ========================================
echo 1. Create superuser: python manage.py createsuperuser
echo 2. Start backend: python manage.py runserver
echo 3. Start frontend: cd lumin-frontend ^&^& npm run dev
echo 4. Start Celery (optional): celery -A config worker -l info
echo.
echo ========================================
echo   Useful Commands:
echo ========================================
echo - Stop containers: docker-compose stop
echo - View logs: docker-compose logs -f
echo - Restart: docker-compose restart
echo.
echo Press any key to exit...
pause >nul
