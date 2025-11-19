#!/bin/bash

echo "=========================================="
echo "Running PDF Validator Locally (No Docker)"
echo "=========================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python3 is not installed"
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "Error: npm is not installed"
    exit 1
fi

# Install backend dependencies
echo "Setting up backend..."
cd backend

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate

# Check for system dependencies
echo "Checking for libqpdf..."
if ! ldconfig -p | grep -q libqpdf; then
    echo ""
    echo "Warning: libqpdf-dev not found!"
    echo "Please install it first:"
    echo "  Ubuntu/Debian: sudo apt-get install libqpdf-dev"
    echo "  macOS: brew install qpdf"
    echo ""
    read -p "Press Enter if already installed, or Ctrl+C to exit and install..."
fi

echo "Installing Python packages..."
pip install -q -r requirements.txt

echo ""
echo "Starting backend on http://localhost:5000"
python app.py &
BACKEND_PID=$!

cd ..

# Install frontend dependencies
echo ""
echo "Setting up frontend..."
cd frontend

if [ ! -d "node_modules" ]; then
    echo "Installing npm packages..."
    npm install
fi

echo ""
echo "Starting frontend on http://localhost:3000"
npm run dev &
FRONTEND_PID=$!

cd ..

echo ""
echo "=========================================="
echo "Application Running!"
echo "=========================================="
echo "Frontend: http://localhost:3000"
echo "Backend:  http://localhost:5000"
echo ""
echo "Press Ctrl+C to stop both services"
echo ""

# Wait for Ctrl+C
trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait
