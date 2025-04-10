#!/bin/bash

# Property Report Generator startup script for Mac/Unix systems

echo "=== Property Report Generator ==="
echo

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed or not in your PATH."
    echo "Please install Python 3 from https://www.python.org/downloads/"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to create virtual environment."
        exit 1
    fi
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to activate virtual environment."
    exit 1
fi

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies."
    exit 1
fi

# Create necessary directories if they don't exist
mkdir -p output logs static/images uploads

# Check if command line argument is provided
if [ "$1" == "local" ]; then
    echo "Running in local script mode..."
    python3 generate_report.py
else
    echo "Starting web application..."
    echo "Please open your browser and go to http://127.0.0.1:5000"
    python3 app.py
fi