#!/usr/bin/env python3
"""
Property Report Generator - Web Application

This is the Flask web application that provides a browser interface
for the Property Report Generator, optimized for deployment on Azure.
"""

import os
import sys
import threading
import logging
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, send_file, flash, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import pandas as pd

# Initialize Flask app early for faster startup
app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = os.environ.get('SECRET_KEY', 'property_report_generator_secret_key')

# Global initialization flag
initialization_complete = False

# Set up logging - simpler setup during initial startup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('webapp')
logger.info("✅ Flask app loaded")

# Configure upload settings
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'xlsx', 'xls', 'csv'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Limit file size to 16MB

# Create a fast health check endpoint for Azure
@app.route('/health')
def health_check():
    """Reliable health check endpoint for Azure that never fails."""
    try:
        # Always return OK, even if app isn't fully initialized
        return "OK", 200
    except:
        # Never fail the health check
        return "OK", 200

# Faster status endpoint with minimal checks
@app.route('/status', methods=['GET'])
def status():
    """Extended status endpoint for debugging."""
    import platform
    
    # Return minimal status info immediately
    status_info = {
        'status': 'running',
        'timestamp': datetime.now().isoformat(),
        'python_version': sys.version,
        'platform': platform.platform(),
        'initialization_complete': initialization_complete
    }
    
    return jsonify(status_info)

def verify_weasyprint():
    """Verify WeasyPrint installation by checking version and HTML rendering."""
    try:
        import weasyprint
        logger.info(f"WeasyPrint version: {weasyprint.__version__}")
        
        # Try a very simple PDF generation in memory
        weasyprint.HTML(string="<h1>Test</h1>").write_pdf()
        
        logger.info("WeasyPrint basic rendering test passed")
        return True
    except Exception as e:
        logger.error(f"WeasyPrint verification failed: {str(e)}")
        return False

def initialize_app_background():
    """Perform initialization tasks in background after app has started."""
    global initialization_complete
    
    try:
        logger.info("Starting background initialization...")
        
        # Set up file logging now that we're in the background
        try:
            os.makedirs('logs', exist_ok=True)
            file_handler = logging.FileHandler(f"logs/webapp_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
            file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
            logger.addHandler(file_handler)
            logger.info("File logging initialized")
        except Exception as e:
            logger.error(f"Failed to set up file logging: {str(e)}")
        
        # Create directories
        for directory in ['uploads', 'output', 'static/images', 'static/css', 'static/js', 'templates']:
            os.makedirs(directory, exist_ok=True)
            logger.info(f"Ensured directory exists: {directory}")
        
        # Verify WeasyPrint
        weasyprint_status = verify_weasyprint()
        logger.info(f"WeasyPrint verification: {'Successful' if weasyprint_status else 'Failed but continuing'}")
        
        # Import modules only after initialization
        try:
            from utils.data_processor import process_excel_data
            from utils.pdf_generator import generate_pdf
            logger.info("Successfully imported utility modules")
        except Exception as e:
            logger.error(f"Error importing utility modules: {str(e)}")
        
        # Mark initialization as complete
        initialization_complete = True
        logger.info("Background initialization completed successfully")
        
    except Exception as e:
        logger.error(f"Background initialization failed: {str(e)}", exc_info=True)
        # Even if initialization fails, we'll set it to True so the app can attempt to function
        initialization_complete = True

# Start the background initialization thread
background_init_thread = threading.Thread(target=initialize_app_background)
background_init_thread.daemon = True
background_init_thread.start()

# Middleware to check initialization status
@app.before_request
def check_initialization():
    """Check if app is initialized before processing complex requests."""
    # Skip middleware for health/status endpoints and favicon
    if request.path in ['/health', '/status', '/favicon.ico']:
        return None
        
    # For all other requests, return a friendly message if not initialized
    if not initialization_complete:
        if request.path == '/':
            flash('Application is initializing. Please wait a moment and refresh the page.', 'info')
            return render_template('index.html')
        return "Application is initializing, please try again shortly", 503

def allowed_file(filename):
    """Check if the uploaded file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def index():
    """Handle the main page and form submission."""
    if request.method == 'POST':
        logger.info("Received form submission")
        
        # Import modules lazily to ensure they're imported after initialization
        from utils.data_processor import process_excel_data
        from utils.pdf_generator import generate_pdf
        
        # Check if business type was selected
        business_type = request.form.get('business_type')
        if not business_type:
            logger.warning("No business type selected")
            flash('Please select a business type (BusiVet or BusiHealth)', 'error')
            return redirect(request.url)
        
        # Check if the second line was provided
        second_line = request.form.get('second_line')
        if not second_line:
            logger.warning("No second line text provided")
            flash('Please provide the second line text (e.g., Landscape Report & Site Search)', 'error')
            return redirect(request.url)
        
        # Check if the third line was provided
        third_line = request.form.get('third_line')
        if not third_line:
            logger.warning("No third line text provided")
            flash('Please provide the third line text (e.g., Oran Park & Mickleham)', 'error')
            return redirect(request.url)
        
        # Check if date was provided
        report_date = request.form.get('report_date')
        if not report_date:
            logger.warning("No report date provided")
            flash('Please provide a date for the report', 'error')
            return redirect(request.url)

        # Check if file was submitted
        if 'file' not in request.files:
            logger.warning("No file part in request")
            flash('No file part', 'error')
            return redirect(request.url)
        
        file = request.files['file']
        
        # Check if file was selected
        if file.filename == '':
            logger.warning("No file selected")
            flash('No selected file', 'error')
            return redirect(request.url)
        
        # Process valid file
        if file and allowed_file(file.filename):
            try:
                logger.info(f"Processing file: {file.filename}")
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                logger.info(f"File saved at {filepath}")
                
                # Process the file data
                logger.info("Reading Excel/CSV data...")
                df = None
                
                # Determine file type and read accordingly
                if filename.endswith('.csv'):
                    logger.info("Reading CSV file")
                    df = pd.read_csv(filepath)
                else:  # Excel file
                    logger.info("Reading Excel file")
                    df = pd.read_excel(filepath)
                
                if df is None or df.empty:
                    logger.error("Empty dataframe after reading file")
                    flash('Unable to read data from the uploaded file', 'error')
                    return redirect(request.url)
                
                # Process data
                logger.info("Processing property data...")
                processed_data = process_excel_data(df, filepath)  # Pass the filepath for image extraction
                
                # Generate PDF report
                logger.info("Generating PDF report...")
                pdf_path = generate_pdf(
                    processed_data,
                    business_type=business_type,
                    second_line=second_line,
                    third_line=third_line,
                    report_date=report_date
                )
                
                # Serve the PDF for download
                logger.info(f"Sending file {pdf_path} for download")
                return send_file(
                    pdf_path,
                    as_attachment=True,
                    download_name=f"Property_Report_{third_line.replace(' ', '_')}_{report_date.replace(' ', '_')}.pdf",
                    mimetype='application/pdf'
                )
                
            except Exception as e:
                logger.error(f"Error processing file: {str(e)}", exc_info=True)
                flash(f'Error processing file: {str(e)}', 'error')
                return redirect(request.url)
        else:
            logger.warning(f"Invalid file type: {file.filename}")
            flash('File type not allowed. Please upload an Excel (.xlsx, .xls) or CSV file.', 'error')
            return redirect(request.url)
    
    # GET request: render the form
    logger.info("Rendering index page")
    return render_template('index.html')

@app.route('/reset', methods=['POST'])
def reset():
    """Reset the form and return to the index page."""
    logger.info("Form reset requested")
    # Instead of redirecting, return a success response to be handled by JavaScript
    return jsonify({"status": "success", "message": "Form reset successful"})

@app.route('/favicon.ico')
def favicon():
    try:
        return send_from_directory(
            os.path.join(app.root_path, 'static'),
            'favicon.ico',
            mimetype='image/vnd.microsoft.icon'
        )
    except:
        return "", 204  # Return empty response if favicon not found

if __name__ == '__main__':
    # Use environment variable for port (Azure sets this)
    port = int(os.environ.get('PORT', 8000))  # Changed default to 8000 to match Dockerfile
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    # Log startup information
    logger.info(f"Starting Property Report Generator web application")
    logger.info(f"Running on port: {port}")
    logger.info(f"Debug mode: {debug}")
    
    # Start the application
    app.run(host='0.0.0.0', port=port, debug=debug)