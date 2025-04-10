"""
Data processor module for extracting and analyzing property data from Excel/CSV files.

This module handles all data processing tasks required to generate the property report.
"""

import os
import logging
import pandas as pd
import numpy as np
import sys

# Set up logger for this module
logger = logging.getLogger(__name__)

def process_excel_data(df):
    """
    Process the Excel/CSV data and extract relevant information for the report.
    
    Args:
        df (pandas.DataFrame): The dataframe containing property data
        
    Returns:
        dict: A dictionary containing all processed data needed for the report
    """
    logger.info("Starting data processing")
    logger.info(f"DataFrame shape: {df.shape}")
    logger.info(f"DataFrame columns: {list(df.columns)}")
    
    # Validate required columns
    required_columns = [
        'Type', 'Property Photo', 'Street Address', 'Suburb', 'State', 'Postcode',
        'Site Zoning', 'Property Type', 'Car', 'Floor Size (m²)', 'Sale Price',
        'Last Listed Price', 'Last Rental Price', 'PUT IN REPORT (T/F)', 'Busi\'s Comment', '$/m²'
    ]
    
    # Check for missing columns
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        logger.error(f"Missing required columns: {missing_columns}")
        raise ValueError(f"Missing required columns: {missing_columns}")
    
    # Initialize the result dictionary
    result = {
        'for_lease_properties': [],
        'for_sale_properties': [],
        'statistics': {},
    }
    
    # Process statistics for the map page
    try:
        logger.info("Processing statistics for the map page")
        
        # Count properties by type
        for_lease_count = len(df[df['Type'] == 'For Lease'])
        already_leased_count = len(df[df['Type'] == 'Already Leased'])
        for_sale_count = len(df[df['Type'] == 'For Sale'])
        sold_count = len(df[df['Type'] == 'Sold'])
        
        logger.info(f"Property counts - For Lease: {for_lease_count}, Already Leased: {already_leased_count}, "
                   f"For Sale: {for_sale_count}, Sold: {sold_count}")
        
        # Count properties that meet criteria (PUT IN REPORT = T) by type
        for_lease_criteria = len(df[(df['Type'] == 'For Lease') & (df['PUT IN REPORT (T/F)'] == 'T')])
        already_leased_criteria = len(df[(df['Type'] == 'Already Leased') & (df['PUT IN REPORT (T/F)'] == 'T')])
        for_sale_criteria = len(df[(df['Type'] == 'For Sale') & (df['PUT IN REPORT (T/F)'] == 'T')])
        sold_criteria = len(df[(df['Type'] == 'Sold') & (df['PUT IN REPORT (T/F)'] == 'T')])
        
        logger.info(f"Properties meeting criteria - For Lease: {for_lease_criteria}, Already Leased: {already_leased_criteria}, "
                   f"For Sale: {for_sale_criteria}, Sold: {sold_criteria}")
        
        # Calculate average $/m² for each type that meets criteria
        for_lease_avg_price = calculate_average_price_per_sqm(df, 'For Lease', 'T')
        already_leased_avg_price = calculate_average_price_per_sqm(df, 'Already Leased', 'T')
        for_sale_avg_price = calculate_average_price_per_sqm(df, 'For Sale', 'T')
        sold_avg_price = calculate_average_price_per_sqm(df, 'Sold', 'T')
        
        logger.info(f"Average prices $/m² - For Lease: ${for_lease_avg_price}, Already Leased: ${already_leased_avg_price}, "
                   f"For Sale: ${for_sale_avg_price}, Sold: ${sold_avg_price}")
        
        # Store statistics in the result
        result['statistics'] = {
            'for_lease': {
                'total': for_lease_count,
                'criteria': for_lease_criteria,
                'avg_price': for_lease_avg_price
            },
            'already_leased': {
                'total': already_leased_count,
                'criteria': already_leased_criteria,
                'avg_price': already_leased_avg_price
            },
            'for_sale': {
                'total': for_sale_count,
                'criteria': for_sale_criteria,
                'avg_price': for_sale_avg_price
            },
            'sold': {
                'total': sold_count,
                'criteria': sold_criteria,
                'avg_price': sold_avg_price
            }
        }
        
        logger.info("Statistics processed successfully")
    except Exception as e:
        logger.error(f"Error processing statistics: {str(e)}", exc_info=True)
        raise
    
    # Extract 'For Lease' properties to include in the report
    try:
        logger.info("Processing 'For Lease' properties")
        lease_properties = df[(df['Type'] == 'For Lease') & (df['PUT IN REPORT (T/F)'] == 'T')]
        
        for _, property_row in lease_properties.iterrows():
            property_data = extract_property_data(property_row, 'For Lease')
            result['for_lease_properties'].append(property_data)
            
        logger.info(f"Processed {len(result['for_lease_properties'])} 'For Lease' properties")
    except Exception as e:
        logger.error(f"Error processing 'For Lease' properties: {str(e)}", exc_info=True)
        raise
    
    # Extract 'For Sale' properties to include in the report
    try:
        logger.info("Processing 'For Sale' properties")
        sale_properties = df[(df['Type'] == 'For Sale') & (df['PUT IN REPORT (T/F)'] == 'T')]
        
        for _, property_row in sale_properties.iterrows():
            property_data = extract_property_data(property_row, 'For Sale')
            result['for_sale_properties'].append(property_data)
            
        logger.info(f"Processed {len(result['for_sale_properties'])} 'For Sale' properties")
    except Exception as e:
        logger.error(f"Error processing 'For Sale' properties: {str(e)}", exc_info=True)
        raise
    
    return result

def calculate_average_price_per_sqm(df, property_type, put_in_report):
    """
    Calculate the average price per square meter for properties of a given type.
    
    Args:
        df (pandas.DataFrame): The dataframe containing property data
        property_type (str): The type of property ('For Lease', 'Already Leased', 'For Sale', 'Sold')
        put_in_report (str): Filter for 'PUT IN REPORT (T/F)' column ('T' or 'F')
        
    Returns:
        int: The average price per square meter as an integer (rounded)
    """
    filtered_df = df[(df['Type'] == property_type) & (df['PUT IN REPORT (T/F)'] == put_in_report)]
    
    logger.debug(f"Calculating average $/m² for {property_type} (PUT IN REPORT = {put_in_report})")
    logger.debug(f"Found {len(filtered_df)} matching properties")
    
    if filtered_df.empty:
        logger.debug(f"No properties found for {property_type} with PUT IN REPORT = {put_in_report}")
        return 0
    
    # Convert '$/m²' column to numeric, handling non-numeric values
    if '$/m²' in filtered_df.columns:
        # Convert column to string first to handle any non-string values
        filtered_df['$/m²'] = filtered_df['$/m²'].astype(str)
        
        # Remove $ and commas, then convert to float
        filtered_df['$/m²'] = filtered_df['$/m²'].str.replace('$', '', regex=False)
        filtered_df['$/m²'] = filtered_df['$/m²'].str.replace(',', '', regex=False)
        filtered_df['$/m²'] = pd.to_numeric(filtered_df['$/m²'], errors='coerce')
        
        # Calculate average, ignoring NaN values
        avg_price = filtered_df['$/m²'].mean()
        return round(avg_price) if not np.isnan(avg_price) else 0
    else:
        logger.warning("$/m² column not found in filtered dataframe")
        return 0

def extract_property_data(row, property_type):
    """
    Extract and format property data from a row in the dataframe.
    
    Args:
        row (pandas.Series): A row from the properties dataframe
        property_type (str): The type of property ('For Lease' or 'For Sale')
        
    Returns:
        dict: A dictionary with the formatted property data
    """
    logger.debug(f"Extracting property data for {property_type} - Suburb: {row['Suburb']}")
    
    # Format street address (capitalize first letter of each word)
    street_address = " ".join([word.capitalize() for word in str(row['Street Address']).lower().split()])
    logger.debug(f"Formatted street address: {street_address}")
    
    # Format suburb (capitalize first letter of each word)
    suburb = " ".join([word.capitalize() for word in str(row['Suburb']).lower().split()])
    logger.debug(f"Formatted suburb: {suburb}")
    
    # Determine price based on property type
    price = ""
    if property_type == 'For Lease':
        if pd.notna(row['Last Rental Price']) and row['Last Rental Price'] != '':
            price = format_price_string(row['Last Rental Price'])
        else:
            price = "Not Disclosed"
    elif property_type == 'For Sale':
        if pd.notna(row['Last Listed Price']) and row['Last Listed Price'] != '':
            price = format_price_string(row['Last Listed Price'])
        else:
            price = "Not Disclosed"
    
    # Format floor area
    floor_area = str(row['Floor Size (m²)']) if pd.notna(row['Floor Size (m²)']) else "Not Disclosed"
    
    # Format car spaces
    car_spaces = str(row['Car']) if pd.notna(row['Car']) else "-"
    
    # Process image path - check if it's a valid path and exists
    image_path = row['Property Photo'] if pd.notna(row['Property Photo']) else None
    if image_path and isinstance(image_path, str):
        if not os.path.exists(image_path):
            logger.warning(f"Property photo not found at path: {image_path}")
            image_path = None
    
    # Extract property data with key names matching pdf_generator expectations
    property_data = {
        'suburb': str(row['Suburb']),  # Keep original for header
        'suburb_formatted': suburb,    # Formatted for display
        'street address': street_address,  # Note the space in the key name to match pdf_generator
        'floor area': floor_area,      # Space in key name
        'price': price,
        'zoning': str(row['Site Zoning']) if pd.notna(row['Site Zoning']) else "Not Specified",
        'property type': str(row['Property Type']) if pd.notna(row['Property Type']) else "Commercial",
        'car spaces': car_spaces,      # Space in key name
        'comments': str(row["Busi's Comment"]) if pd.notna(row["Busi's Comment"]) else "",
        'image': image_path
    }
    
    logger.debug(f"Extracted property data: {street_address}, {suburb}, {price}")
    return property_data

def format_price_string(price_value):
    """
    Format price values consistently for the report.
    
    Args:
        price_value: The price value to format
        
    Returns:
        str: Formatted price string
    """
    # If price is numeric, format with commas for thousands
    if isinstance(price_value, (int, float)) or (isinstance(price_value, str) and price_value.replace(',', '').replace('.', '').isdigit()):
        # Convert to float first
        if isinstance(price_value, str):
            # Remove currency symbols, commas, etc.
            clean_price = price_value.replace('$', '').replace(',', '')
            try:
                price_num = float(clean_price)
                
                # Format based on value
                if price_num % 1 == 0:  # It's a whole number
                    return f"${int(price_num):,}"
                else:
                    return f"${price_num:,.2f}"
            except ValueError:
                return str(price_value)  # Return as is if conversion fails
        else:
            # It's already a number
            if price_value % 1 == 0:  # It's a whole number
                return f"${int(price_value):,}"
            else:
                return f"${price_value:,.2f}"
    else:
        # If it's already a string like "Offers above $X" or "Not Disclosed"
        return str(price_value)