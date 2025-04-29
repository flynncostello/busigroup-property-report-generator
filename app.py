#!/usr/bin/env python3
"""
Property Report Generator - Web Application

This is the Flask web application that provides a browser interface
for the Property Report Generator, optimized for deployment on Azure.
"""

import os
import sys
import logging
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, send_file, flash, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import pandas as pd
from utils.data_processor import process_excel_data
from utils.pdf_generator import generate_pdf

# Set up logging
os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f"logs/webapp_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
print("✅ Flask app loaded")
logger = logging.getLogger('webapp')

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


# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'property_report_generator_secret_key')

# Configure upload settings
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'xlsx', 'xls', 'csv'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Limit file size to 16MB

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
logger.info(f"Ensuring upload directory exists: {UPLOAD_FOLDER}")

# Ensure output directory exists (for PDFs)
os.makedirs('output', exist_ok=True)
logger.info("Ensuring output directory exists")

def allowed_file(filename):
    """Check if the uploaded file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def index():
    """Handle the main page and form submission."""
    if request.method == 'POST':
        logger.info("Received form submission")
        
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
                    mimetype='application/pdf'  # Add explicit mimetype
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
    return redirect(url_for('index'))

@app.route('/download-complete', methods=['GET'])
def download_complete():
    """Endpoint to signal that download is complete (called via AJAX)."""
    return jsonify({"status": "success", "message": "Download complete signal received"})


@app.route('/health')
def health_check():
    """Health check endpoint for Azure."""
    return "OK", 200


@app.route('/download-test')
def download_test():
    """Test endpoint for file downloads."""
    test_file = os.path.join('output', 'test.txt')
    
    # Create a simple test file
    with open(test_file, 'w') as f:
        f.write("This is a test file for download")
    
    return send_file(
        test_file,
        as_attachment=True,
        download_name="test.txt",
        mimetype='text/plain'
    )


@app.errorhandler(Exception)
def handle_exception(e):
    """Global exception handler to prevent app crashes."""
    logger.error(f"Unhandled exception: {str(e)}", exc_info=True)
    return "An unexpected error occurred. Please try again later.", 500


@app.route('/status', methods=['GET'])
def status():
    """Extended status endpoint for debugging."""
    import platform
    
    status_info = {
        'timestamp': datetime.now().isoformat(),
        'python_version': sys.version,
        'platform': platform.platform(),
        'directories': {
            'uploads': os.path.exists(UPLOAD_FOLDER) and os.access(UPLOAD_FOLDER, os.W_OK),
            'output': os.path.exists('output') and os.access('output', os.W_OK),
            'static': os.path.exists('static')
        }
    }
    
    # Check WeasyPrint
    try:
        import weasyprint
        status_info['weasyprint'] = {
            'version': weasyprint.__version__,
            'status': 'Working'
        }
    except Exception as e:
        status_info['weasyprint'] = {
            'status': 'Error',
            'message': str(e)
        }
    
    # Return detailed status
    return jsonify(status_info)

# Startup verification
logger.info("Verifying WeasyPrint installation...")
if not verify_weasyprint():
    logger.warning("WeasyPrint verification failed - PDF generation may not work correctly")
else:
    logger.info("WeasyPrint verification successful")


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(
        os.path.join(app.root_path, 'static'),
        'favicon.ico',
        mimetype='image/vnd.microsoft.icon'
    )



if __name__ == '__main__':
    # Use environment variable for port (Azure sets this)
    port = int(os.environ.get('PORT', 5001))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    # Log startup information
    logger.info(f"Starting Property Report Generator web application")
    logger.info(f"Running on port: {port}")
    logger.info(f"Debug mode: {debug}")
    
    # Start the application
    app.run(host='0.0.0.0', port=port, debug=debug)