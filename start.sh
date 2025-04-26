#!/bin/bash
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate reportgen

# Get the PORT from environment variable with a fallback to 8000
export PORT=${PORT:-8000}

# Log startup info for debugging
echo "Starting application on port $PORT"
echo "Python version: $(python --version)"
echo "Current directory: $(pwd)"
echo "Files in directory: $(ls -la)"

# Run gunicorn binding to the PORT provided by Azure or default to 8000
conda run -n reportgen gunicorn app:app --bind 0.0.0.0:$PORT --log-level debug