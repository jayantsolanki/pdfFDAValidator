#!/bin/bash

# Startup script for PDF Validator Web App

echo "======================================"
echo "PDF Validator & Processor Web App"
echo "======================================"
echo ""

# Check if docker is installed
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed"
    echo "Please install Docker from https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if docker-compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "Error: docker-compose is not installed"
    echo "Please install docker-compose from https://docs.docker.com/compose/install/"
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file from .env.example..."
    cp .env.example .env
    echo "Please edit .env and set a secure SECRET_KEY before deploying to production"
    echo ""
fi

# Start the application
echo "Starting the application..."
docker-compose up -d

# Wait a moment for services to start
sleep 3

# Check if services are running
echo ""
echo "Checking service status..."
docker-compose ps

echo ""
echo "======================================"
echo "Application started successfully!"
echo "======================================"
echo ""
echo "Frontend: http://localhost"
echo "Backend API: http://localhost:5000"
echo ""
echo "To view logs: docker-compose logs -f"
echo "To stop: docker-compose down"
echo "To stop and remove data: docker-compose down -v"
echo ""
