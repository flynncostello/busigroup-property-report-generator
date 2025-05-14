"""
PDF Generator module for creating property report PDFs.

This module handles the generation of PDF reports based on HTML templates.
"""

import os
import logging
from utils.pdf_components.pdf_renderer import PdfRenderer

# Set up logger for this module
logger = logging.getLogger(__name__)

# Ensure paths to static assets and output directory
STATIC_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static')
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'output')

# Ensure the output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)
logger.info(f"Static directory path: {STATIC_DIR}")
logger.info(f"Output directory path: {OUTPUT_DIR}")

def generate_pdf(data, business_type, first_line, second_line, third_line, report_date):
    """
    Generate a complete property report PDF using HTML templates.
    
    Args:
        data (dict): Processed property data
        business_type (str): 'busivet' or 'busihealth'
        second_line (str): Second line of big text for cover page
        third_line (str): Third line of big text for cover page (location)
        report_date (str): Date for the report (e.g., '26 March 2025')
        
    Returns:
        str: Path to the generated PDF file
    """
    logger.info(f"Generating PDF for {business_type} report")
    
    # Initialize PDF renderer with output directory
    pdf_renderer = PdfRenderer(OUTPUT_DIR, STATIC_DIR)
    
    # Generate PDF from data
    output_path = pdf_renderer.render_pdf(
        data,
        business_type,
        first_line,
        second_line,
        third_line, 
        report_date
    )
    
    logger.info(f"PDF generated at {output_path}")
    return output_path