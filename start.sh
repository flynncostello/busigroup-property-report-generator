#!/bin/bash

# Set PATH to include conda
export PATH="/opt/conda/bin:$PATH"

# Activate conda environment without using source
eval "$(/opt/conda/bin/conda shell.bash hook)"
conda activate reportgen

# Get the PORT from environment variable with a fallback to 8000
export PORT=${PORT:-8000}

# Log startup info for debugging
echo "Starting application on port $PORT"
echo "Python version: $(python --version)"
echo "Current directory: $(pwd)"

# Run gunicorn directly instead of using conda run
gunicorn app:app --bind 0.0.0.0:$PORT --log-level info