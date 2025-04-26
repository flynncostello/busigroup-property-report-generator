#!/bin/bash

# Set PATH to include conda
export PATH="/opt/conda/bin:$PATH"

# Log everything for debugging
echo "=== CONTAINER START $(date) ==="
echo "Current directory: $(pwd)"
echo "Files: $(ls -la)"
echo "PORT: ${PORT:-8000}"

# Simple Flask app instead of your complex app
# Use Python directly from conda without activating environment
python3 -m flask --app app run --host=0.0.0.0 --port=${PORT:-8000}

# Keep container running even if Flask fails
echo "Flask exited, keeping container alive for debugging"
tail -f /dev/null