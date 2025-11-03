#!/bin/bash

# S3 Upload Service Start Script

echo "Starting S3 Upload Service..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "Warning: .env file not found. Please create one based on .env.example"
    echo "Copying .env.example to .env..."
    cp .env.example .env
    echo "Please edit .env file with your AWS credentials before running again."
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install requirements
echo "Installing requirements..."
pip install -r requirements.txt

# Start the server
echo "Starting FastAPI server on http://localhost:8000"
uvicorn main:app --host 0.0.0.0 --port 8000 --reload