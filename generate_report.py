#!/usr/bin/env python3
"""
Property Report Generator - Local Script Version

This script allows direct generation of property reports from Excel/CSV files
without using the web interface.

Usage:
    python generate_report.py [options]

Example:
    python generate_report.py --file data.xlsx --business busivet --title "Landscape Report" --location "Sydney & Melbourne" --date "10 April 2025"
"""

import os
import sys
import argparse
import logging
import pandas as pd
from datetime import datetime
from utils.data_processor import process_excel_data
from utils.pdf_generator import generate_pdf

# Set up logging
os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f"logs/property_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('generate_report')


def generate_report(file_path, business_type, title_line, location_line, report_date):
    """Generate a property report from the given Excel/CSV file."""
    logger.info(f"Starting report generation with {file_path}")
    logger.info(f"Parameters: Business={business_type}, Title={title_line}, Location={location_line}, Date={report_date}")
    
    try:
        # Check if file exists
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return None
        
        # Determine file type and read accordingly
        logger.info(f"Reading data from {file_path}")
        if file_path.lower().endswith('.csv'):
            df = pd.read_csv(file_path)
            logger.info("CSV file detected and loaded")
        elif file_path.lower().endswith(('.xlsx', '.xls')):
            df = pd.read_excel(file_path)
            logger.info("Excel file detected and loaded")
        else:
            logger.error(f"Unsupported file format: {file_path}")
            return None
        
        # Check if dataframe is empty
        if df.empty:
            logger.error("No data found in the file")
            return None
            
        logger.info(f"Data loaded successfully - {len(df)} rows")
        
        # Process Excel data
        logger.info("Processing property data...")
        processed_data = process_excel_data(df, file_path)
        
        # Generate PDF report
        logger.info("Generating PDF report...")
        output_path = generate_pdf(
            processed_data,
            business_type=business_type,
            second_line=title_line,
            third_line=location_line,
            report_date=report_date
        )
        
        logger.info(f"Report generated successfully: {output_path}")
        return output_path
        
    except Exception as e:
        logger.error(f"Error generating report: {str(e)}", exc_info=True)
        return None


if __name__ == "__main__":
    output_path = generate_report(
        '/Users/flynncostello/Library/CloudStorage/OneDrive-Personal/Work/BusiHealth & BusiVet/Site Report Automator/pdf_report_generator/Properties_Hunters_Hill_NSW_2110_Crows_Nest_NSW_2065_04_04_2025_18_03.xlsx', 
        'busivet', 
        'Landscape Report & Site Search', 
        'Oran Park & Mickleham', 
        '10 April 2025'
    )
    
    if output_path:
        print(f"\nSuccess! Report generated at: {output_path}")
    else:
        print("\nFailed to generate report. Please check the logs for details.")