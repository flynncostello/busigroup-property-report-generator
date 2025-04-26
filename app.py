#!/usr/bin/env python3
import os
from flask import Flask

# Initialize Flask app
app = Flask(__name__)

# Configuration
PORT = int(os.environ.get('PORT', 8000))

@app.route('/')
def home():
    return "Property Report Generator is running!"

@app.route('/health')
def health():
    return "OK", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT)