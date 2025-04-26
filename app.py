#!/usr/bin/env python3
import os
import time
import threading
import logging
from flask import Flask, jsonify

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Global flag for whether app is healthy
HEALTHY = True

@app.route('/')
def home():
    logger.info("Root endpoint accessed")
    return "Property Report Generator Diagnostics Page - App is running!"

@app.route('/health')
def health():
    logger.info(f"Health endpoint accessed. Current status: {'HEALTHY' if HEALTHY else 'UNHEALTHY'}")
    if HEALTHY:
        return "OK", 200
    else:
        return "Unhealthy", 500

@app.route('/keepalive')
def keepalive():
    """Force container to stay alive even if main app has issues"""
    return "Keepalive active", 200

def log_health_status():
    """Background thread that logs health status every 5 seconds"""
    count = 0
    while True:
        count += 1
        logger.info(f"[HEARTBEAT #{count}] App is running. Health status: {'HEALTHY' if HEALTHY else 'UNHEALTHY'}")
        time.sleep(5)

if __name__ == '__main__':
    # Start background logging thread
    health_thread = threading.Thread(target=log_health_status, daemon=True)
    health_thread.start()
    
    # Start Flask app
    port = int(os.environ.get('PORT', 8000))
    logger.info(f"Starting app on port {port}")
    app.run(host='0.0.0.0', port=port, threaded=True)