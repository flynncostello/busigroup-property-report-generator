#!/bin/bash
set -e

# Set PATH to include conda
export PATH="/opt/conda/bin:$PATH"

# Log beginning of startup
echo "START.SH: Starting container initialization $(date)"
echo "START.SH: Current directory: $(pwd)"
echo "START.SH: Files: $(ls -la)"

# Activate conda environment without using source
eval "$(/opt/conda/bin/conda shell.bash hook)"
echo "START.SH: Conda hook activated"

conda activate reportgen
echo "START.SH: Environment 'reportgen' activated"

# Get the PORT from environment variable with a fallback to 8000
export PORT=${PORT:-8000}
export KEEPALIVE_PORT=8001

# Log environment variables
echo "START.SH: PORT=$PORT, KEEPALIVE_PORT=$KEEPALIVE_PORT"
echo "START.SH: Environment variables:"
printenv | grep -E 'PORT|WEBSITE|DOCKER'

# Create a trap to ensure cleanup on exit
trap 'echo "START.SH: Shutting down all processes"; kill $(jobs -p) 2>/dev/null || true' EXIT

# Start keepalive server in background
echo "START.SH: Starting keepalive server..."
python keepalive.py &
KEEPALIVE_PID=$!
echo "START.SH: Keepalive server started (PID: $KEEPALIVE_PID)"

# Wait a moment for keepalive to initialize
sleep 2

# Start the main application with gunicorn
echo "START.SH: Starting main application server..."
exec gunicorn app:app \
  --bind 0.0.0.0:$PORT \
  --workers 1 \
  --timeout 120 \
  --access-logfile - \
  --log-level debug
