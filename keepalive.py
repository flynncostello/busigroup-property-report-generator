#!/usr/bin/env python3
"""
Keepalive server to ensure the container stays running even if the main app fails.
This handles health checks and basic routing.
"""

import os
import threading
import time
from flask import Flask, redirect

app = Flask(__name__)

@app.route('/')
def root():
    """Root route redirects to index page of main app."""
    return "Property Report Generator is running. Please wait while the application loads...", 200

@app.route('/health')
def health():
    """Health check endpoint."""
    return "OK", 200

@app.route('/keepalive')
def keepalive():
    """Keepalive endpoint."""
    return "Container keepalive active", 200

def log_heartbeat():
    """Background thread that logs health status every 10 seconds."""
    count = 0
    while True:
        count += 1
        print(f"[KEEPALIVE #{count}] Container is alive - {time.strftime('%Y-%m-%d %H:%M:%S')}")
        time.sleep(10)

if __name__ == '__main__':
    # Start background logging thread
    health_thread = threading.Thread(target=log_heartbeat, daemon=True)
    health_thread.start()
    
    # Get port from environment with fallback
    port = int(os.environ.get('KEEPALIVE_PORT', 8001))
    print(f"Starting keepalive server on port {port}")
    
    # Run the Flask app
    app.run(host='0.0.0.0', port=port, threaded=True)