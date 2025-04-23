#!/bin/bash
# Run script with proper environment

# Add our directory to PYTHONPATH
export PYTHONPATH="/Users/flynncostello/Desktop/busihealth-site-search-report-generator:$PYTHONPATH"

# Set Flask variables
export FLASK_APP=app.py
export FLASK_DEBUG=True

# Run the app
python app.py
