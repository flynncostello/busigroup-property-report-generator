#!/bin/bash

# Log everything for debugging
echo "=== CONTAINER START $(date) ==="
echo "Current directory: $(pwd)"
echo "Files: $(ls -la)"

# Set path to include conda
export PATH="/opt/conda/bin:$PATH"

# Activate conda environment without using source
eval "$(/opt/conda/bin/conda shell.bash hook)"
conda activate reportgen

# Get the PORT from environment variable with a fallback to 8000
export PORT=${PORT:-8000}
echo "Starting Azure diagnostic app on port $PORT"

# Start health check process
echo "Starting health check process"
python app.py &
FLASK_PID=$!

# Log health check PID
echo "Flask running with PID: $FLASK_PID"

# To prevent container from terminating, wait forever
echo "Container will stay running to allow debugging"
tail -f /dev/null