#!/bin/bash

# Set PATH to include conda
export PATH="/opt/conda/bin:$PATH"

# Log beginning of startup
echo "START.SH: Starting container initialization"

# Activate conda environment without using source
eval "$(/opt/conda/bin/conda shell.bash hook)"
echo "START.SH: Conda hook activated"

conda activate reportgen
echo "START.SH: Environment 'reportgen' activated"

# Get the PORT from environment variable with a fallback to 8000
export PORT=${PORT:-8000}

# Log startup info for debugging
echo "START.SH: Starting application on port $PORT"
echo "START.SH: Python version: $(python --version)"
echo "START.SH: Current directory: $(pwd)"
echo "START.SH: Files in directory: $(ls -la)"

# Print environment variables for debugging
echo "START.SH: Environment variables:"
printenv | grep -E 'PORT|WEBSITE|DOCKER'

# Run gunicorn with more detailed logging
echo "START.SH: Starting gunicorn server on 0.0.0.0:$PORT..."
exec gunicorn app:app --bind 0.0.0.0:$PORT --log-level debug --timeout 120 --access-logfile -