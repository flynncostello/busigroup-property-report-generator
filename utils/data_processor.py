"""
Data processor module for extracting and analyzing property data from Excel/CSV files.

This module handles all data processing tasks required to generate the property report.
"""

import os
import logging
import pandas as pd
import numpy as np
import base64
import tempfile
import zipfile
import shutil

# Set up logger for this module
logger = logging.getLogger(__name__)

def validate_headers(file_path, sheet_name=None):
    """
    Validate that headers are in the correct columns as specified.
    
    Args:
        file_path (str): Path to the Excel/CSV file
        sheet_name (str, optional): Name of the sheet to validate (for Excel files)
        
    Returns:
        dict: {'valid': bool, 'error': str or None}
    """
    # Define expected headers with their column positions
    # Fixed column mapping based on user requirements
    expected_headers = {
        'A': 'Type',
        'B': 'Property Photo',
        'C': 'Street Address',
        'D': 'Suburb',
        'E': 'State',
        'F': 'Postcode',
        'G': 'Site Zoning',
        'H': 'Property Type',
        'K': 'Car',  # Fixed: Car is in column K, not I
        'N': 'Floor Size (m²)',
        'AL': 'Last Listed Price (Sold/For Sale)',
        'AT': 'Total Lease Price (Base + Outgoings)',
        'AZ': 'Allowable Use in Zone (T/F)',
        'BA': '$/m²',
        'BD': 'PUT IN REPORT (T/F)',
        'BF': "Busi's Comment"
    }
    
    try:
        # Read the file to get headers
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path, nrows=0)  # Read only headers
        else:
            df = pd.read_excel(file_path, sheet_name=sheet_name, nrows=0)  # Read only headers
        
        # Get column names and convert to list
        actual_columns = df.columns.tolist()
        
        # Convert column letters to indices
        def column_letter_to_index(col_letter):
            """Convert column letter(s) to 0-based index"""
            result = 0
            for char in col_letter:
                result = result * 26 + (ord(char.upper()) - ord('A')) + 1
            return result - 1
        
        # Check each expected header
        for col_letter, expected_header in expected_headers.items():
            if expected_header is None:
                continue  # Skip columns we don't care about
                
            col_index = column_letter_to_index(col_letter)
            
            # Check if the column index is within range
            if col_index >= len(actual_columns):
                return {
                    'valid': False,
                    'error': f"Column '{col_letter}' does not exist in the file. Expected '{expected_header}' at column {col_letter}."
                }
            
            # Get the actual header at this position
            actual_header = actual_columns[col_index]
            
            # Compare headers (case-sensitive)
            if actual_header != expected_header:
                return {
                    'valid': False,
                    'error': f"Column '{col_letter}' contains '{actual_header}' but should contain '{expected_header}'"
                }
        
        logger.info("Header validation passed successfully")
        return {'valid': True, 'error': None}
        
    except Exception as e:
        logger.error(f"Error validating headers: {str(e)}")
        return {'valid': False, 'error': f"Error reading file: {str(e)}"}

def extract_excel_images(excel_path):
    """
    Extract images from Excel by treating the file as a ZIP archive.
    
    Args:
        excel_path (str): Path to the Excel file
        
    Returns:
        dict: Dictionary of extracted images as base64 data URLs
    """
    if not os.path.exists(excel_path):
        logger.error(f"Excel file not found: {excel_path}")
        return {}
    
    image_dict = {}
    temp_dir = tempfile.mkdtemp()
    
    try:
        logger.info(f"Extracting Excel file as ZIP: {excel_path}")
        
        # Copy Excel file to temp folder and rename to zip
        temp_excel = os.path.join(temp_dir, "temp.xlsx")
        temp_zip = os.path.join(temp_dir, "temp.zip")
        shutil.copy2(excel_path, temp_excel)
        shutil.move(temp_excel, temp_zip)
        
        # Extract the ZIP contents
        extract_folder = os.path.join(temp_dir, "extracted")
        os.makedirs(extract_folder, exist_ok=True)
        
        with zipfile.ZipFile(temp_zip, 'r') as zip_ref:
            zip_ref.extractall(extract_folder)
            
        # Look for images in xl/media folder
        media_folder = os.path.join(extract_folder, "xl", "media")
        if os.path.exists(media_folder):
            image_files = [f for f in os.listdir(media_folder) 
                          if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]
            
            logger.info(f"Found {len(image_files)} images in Excel file")
            
            # Convert each image to a data URL
            for i, img_file in enumerate(image_files):
                img_path = os.path.join(media_folder, img_file)
                try:
                    with open(img_path, 'rb') as f:
                        img_data = f.read()
                        
                    img_format = img_file.split('.')[-1].lower()
                    if img_format == 'jpg':
                        img_format = 'jpeg'
                        
                    b64_data = base64.b64encode(img_data).decode('utf-8')
                    data_url = f"data:image/{img_format};base64,{b64_data}"
                    
                    # Store with index (will need to be mapped to the correct property later)
                    image_dict[i+1] = {
                        'data_url': data_url,
                        'filename': img_file
                    }
                    
                    logger.info(f"Processed image {i+1}: {img_file} ({len(img_data)} bytes)")
                except Exception as e:
                    logger.error(f"Error processing image {img_file}: {str(e)}")
        else:
            logger.warning("No media folder found in Excel file. No images to extract.")
    
    except Exception as e:
        logger.error(f"Error extracting images from Excel: {str(e)}")
    
    finally:
        # Clean up temp directory
        shutil.rmtree(temp_dir)
    
    return image_dict

def map_images_to_properties(df, images):
    """
    Map extracted images to properties.
    This is a simple approach that assumes images appear in the same order as properties.
    
    Args:
        df (pandas.DataFrame): The property DataFrame
        images (dict): Dictionary of extracted images
        
    Returns:
        dict: DataFrame index to image data URL mapping
    """
    if not images:
        return {}
    
    # Get properties that should be included in the report
    properties_for_report = df[df['PUT IN REPORT (T/F)'] == 'T'].copy()
    
    # Create mapping of DataFrame index to image data URL
    image_mapping = {}
    
    # Get properties by type for consistent ordering
    for_lease = properties_for_report[properties_for_report['Type'] == 'For Lease']
    for_sale = properties_for_report[properties_for_report['Type'] == 'For Sale']
    
    # Assign images in order, first to For Lease properties, then to For Sale
    image_counter = 1
    
    # Map images to For Lease properties
    for idx in for_lease.index:
        if image_counter <= len(images):
            image_mapping[idx] = images[image_counter]['data_url']
            logger.info(f"Mapped image {image_counter} to property at index {idx}")
            image_counter += 1
    
    # Map images to For Sale properties
    for idx in for_sale.index:
        if image_counter <= len(images):
            image_mapping[idx] = images[image_counter]['data_url']
            logger.info(f"Mapped image {image_counter} to property at index {idx}")
            image_counter += 1
    
    logger.info(f"Mapped {image_counter-1} images to properties")
    return image_mapping

def process_excel_data(df, excel_file_path=None):
    """
    Process the Excel/CSV data and extract relevant information for the report.
    
    Args:
        df (pandas.DataFrame): The dataframe containing property data
        excel_file_path (str, optional): Path to the original Excel file for direct image extraction
        
    Returns:
        dict: A dictionary containing all processed data needed for the report
    """
    logger.info("Starting data processing")
    logger.info(f"DataFrame shape: {df.shape}")
    logger.info(f"DataFrame columns: {list(df.columns)}")
    
    # Extract images using the ZIP method if Excel file path is provided
    image_dict = {}
    if excel_file_path and os.path.exists(excel_file_path):
        logger.info(f"Extracting images from Excel file: {excel_file_path}")
        extracted_images = extract_excel_images(excel_file_path)
        if extracted_images:
            # Map images to properties
            image_dict = map_images_to_properties(df, extracted_images)
            logger.info(f"Mapped {len(image_dict)} images to properties")
        else:
            logger.warning("No images were extracted from the Excel file")
    
    # Validate required columns
    required_columns = [
        'Type', 'Property Photo', 'Street Address', 'Suburb', 'State', 'Postcode',
        'Site Zoning', 'Property Type', 'Car', 'Floor Size (m²)', 'Sale Price',
        'Last Listed Price (Sold/For Sale)', 'Total Lease Price (Base + Outgoings)', 'PUT IN REPORT (T/F)', 'Busi\'s Comment', '$/m²'
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
        
        for idx, property_row in lease_properties.iterrows():
            # Get image data for this property if available
            image_data = image_dict.get(idx)
            property_data = extract_property_data(property_row, 'For Lease', image_data)
            result['for_lease_properties'].append(property_data)
            
        logger.info(f"Processed {len(result['for_lease_properties'])} 'For Lease' properties")
    except Exception as e:
        logger.error(f"Error processing 'For Lease' properties: {str(e)}", exc_info=True)
        raise
    
    # Extract 'For Sale' properties to include in the report
    try:
        logger.info("Processing 'For Sale' properties")
        sale_properties = df[(df['Type'] == 'For Sale') & (df['PUT IN REPORT (T/F)'] == 'T')]
        
        for idx, property_row in sale_properties.iterrows():
            # Get image data for this property if available
            image_data = image_dict.get(idx)
            property_data = extract_property_data(property_row, 'For Sale', image_data)
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
    # Create a proper copy to avoid SettingWithCopyWarning
    filtered_df = df[(df['Type'] == property_type) & (df['PUT IN REPORT (T/F)'] == put_in_report)].copy()
    
    logger.debug(f"Calculating average $/m² for {property_type} (PUT IN REPORT = {put_in_report})")
    logger.debug(f"Found {len(filtered_df)} matching properties")
    
    if filtered_df.empty:
        logger.debug(f"No properties found for {property_type} with PUT IN REPORT = {put_in_report}")
        return 0
    
    # Convert '$/m²' column to numeric, handling non-numeric values
    if '$/m²' in filtered_df.columns:
        # Create a temporary series from the column to avoid FutureWarning
        # and perform operations on it instead of directly on the DataFrame
        temp_series = pd.Series(filtered_df['$/m²']).astype(str)
        temp_series = temp_series.str.replace('$', '', regex=False)
        temp_series = temp_series.str.replace(',', '', regex=False)
        numeric_values = pd.to_numeric(temp_series, errors='coerce')
        
        # Assign back to DataFrame
        filtered_df.loc[:, '$/m²'] = numeric_values
        
        # Calculate average, ignoring NaN values
        avg_price = numeric_values.mean()
        return round(avg_price) if not np.isnan(avg_price) else 0
    else:
        logger.warning("$/m² column not found in filtered dataframe")
        return 0

def extract_property_data(row, property_type, image_data=None):
    """
    Extract and format property data from a row in the dataframe.
    
    Args:
        row (pandas.Series): A row from the properties dataframe
        property_type (str): The type of property ('For Lease' or 'For Sale')
        image_data (str, optional): Base64 image data if available
        
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
        if pd.notna(row['Total Lease Price (Base + Outgoings)']) and row['Total Lease Price (Base + Outgoings)'] != '':
            price = format_price_string(row['Total Lease Price (Base + Outgoings)'])
        else:
            price = "Not Disclosed"
    elif property_type == 'For Sale':
        if pd.notna(row['Last Listed Price (Sold/For Sale)']) and row['Last Listed Price (Sold/For Sale)'] != '':
            price = format_price_string(row['Last Listed Price (Sold/For Sale)'])
        else:
            price = "Not Disclosed"
    
    # Format floor area
    floor_area = str(row['Floor Size (m²)']) if pd.notna(row['Floor Size (m²)']) else "Not Disclosed"
    
    # Format car spaces
    car_spaces = str(row['Car']) if pd.notna(row['Car']) else "-"
    
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
        'image_data': image_data       # Base64 image data from Excel
    }
    
    # Log detailed information about extracted property
    logger.info(f"Extracted property data for {street_address}, {suburb}")
    logger.info(f"Property Type: {property_type}, Price: {price}, Floor Area: {floor_area}")
    logger.info(f"Image data present: {'Yes' if image_data else 'No'}")
    
    # Count of properties processed with images
    if image_data:
        logger.info(f"✅ Property {street_address} has image data")
        logger.info(f"Image data URL starts with: {image_data[:50]}") # Log first 50 chars for brevity
    else:
        logger.info(f"❌ Property {street_address} is missing image data")
    
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