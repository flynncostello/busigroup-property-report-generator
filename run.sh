#!/bin/bash

# Property Report Generator startup script for Mac/Unix systems

echo "=== Property Report Generator ==="
echo

# Check operating system
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS specific checks
    # Check if Homebrew is installed
    if ! command -v brew &> /dev/null; then
        echo "Homebrew is not installed. It's recommended for installing dependencies."
        echo "Would you like to install Homebrew? (y/n)"
        read -r install_brew
        if [[ "$install_brew" == "y" ]]; then
            echo "Installing Homebrew..."
            /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        else
            echo "Skipping Homebrew installation. Some dependencies may need to be installed manually."
        fi
    fi
    
    # Check if WeasyPrint dependencies are installed
    if command -v brew &> /dev/null; then
        # Check if cairo, pango, and gdk-pixbuf are installed
        if ! brew list --formula | grep -q cairo || ! brew list --formula | grep -q pango || ! brew list --formula | grep -q gdk-pixbuf; then
            echo "Installing WeasyPrint dependencies with Homebrew..."
            brew install cairo pango gdk-pixbuf
        else
            echo "WeasyPrint dependencies already installed."
        fi
    fi
fi

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed or not in your PATH."
    echo "Please install Python 3 from https://www.python.org/downloads/"
    exit 1
fi

# Check Python version (3.8+ required)
python_version=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
if [[ $(echo "$python_version >= 3.8" | bc) -ne 1 ]]; then
    echo "ERROR: Python $python_version detected, but Python 3.8 or higher is required."
    echo "Please upgrade Python from https://www.python.org/downloads/"
    exit 1
fi

echo "Using Python $python_version"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to create virtual environment."
        exit 1
    fi
else
    echo "Using existing virtual environment."
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to activate virtual environment."
    exit 1
fi

# Check if dependencies need to be installed/updated
if [ ! -f "venv/.dependencies_installed" ] || [ "requirements.txt" -nt "venv/.dependencies_installed" ]; then
    echo "Installing/updating dependencies..."
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to install dependencies."
        exit 1
    fi
    # Mark dependencies as installed by touching a file with the current timestamp
    touch venv/.dependencies_installed
else
    echo "Dependencies are up to date."
fi

# Create necessary directories if they don't exist
mkdir -p output logs static/images uploads utils/pdf_components

# Check if command line argument is provided
if [ "$1" == "local" ]; then
    echo "Running in local script mode..."
    python3 generate_report.py
else
    echo "Starting web application..."
    echo "Please open your browser and go to http://127.0.0.1:5000"
    python3 app.py
fi