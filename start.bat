@echo off
REM Startup script for PDF Validator Web App (Windows)

echo ======================================
echo PDF Validator ^& Processor Web App
echo ======================================
echo.

REM Check if docker is installed
docker --version >nul 2>&1
if errorlevel 1 (
    echo Error: Docker is not installed
    echo Please install Docker Desktop from https://docs.docker.com/desktop/install/windows-install/
    pause
    exit /b 1
)

REM Check if docker-compose is installed
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo Error: docker-compose is not installed
    echo Please install docker-compose or use Docker Desktop which includes it
    pause
    exit /b 1
)

REM Create .env file if it doesn't exist
if not exist .env (
    echo Creating .env file from .env.example...
    copy .env.example .env
    echo Please edit .env and set a secure SECRET_KEY before deploying to production
    echo.
)

REM Start the application
echo Starting the application...
docker-compose up -d

REM Wait a moment for services to start
timeout /t 3 /nobreak >nul

REM Check if services are running
echo.
echo Checking service status...
docker-compose ps

echo.
echo ======================================
echo Application started successfully!
echo ======================================
echo.
echo Frontend: http://localhost
echo Backend API: http://localhost:5000
echo.
echo To view logs: docker-compose logs -f
echo To stop: docker-compose down
echo To stop and remove data: docker-compose down -v
echo.
pause
