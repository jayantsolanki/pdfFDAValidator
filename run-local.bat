@echo off
echo ==========================================
echo Running PDF Validator Locally (No Docker)
echo ==========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed
    pause
    exit /b 1
)

REM Check if npm is installed
npm --version >nul 2>&1
if errorlevel 1 (
    echo Error: npm is not installed
    pause
    exit /b 1
)

echo Setting up backend...
cd backend

if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

call venv\Scripts\activate

echo Installing Python packages...
pip install -q -r requirements.txt

echo.
echo Starting backend on http://localhost:5000
start "Backend Server" cmd /k python app.py

cd ..

echo.
echo Setting up frontend...
cd frontend

if not exist node_modules (
    echo Installing npm packages...
    npm install
)

echo.
echo Starting frontend on http://localhost:3000
start "Frontend Server" cmd /k npm run dev

cd ..

echo.
echo ==========================================
echo Application Running!
echo ==========================================
echo Frontend: http://localhost:3000
echo Backend:  http://localhost:5000
echo.
echo Close the terminal windows to stop the services
echo.
pause
