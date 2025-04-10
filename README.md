# Property Report Generator

A comprehensive application that generates professional property reports from Excel/CSV data, supporting both direct script execution and a web interface.

## Project Overview

This application processes property data and creates formatted PDF reports with these sections:

- Cover page with business branding and background image
- Map page with statistics table
- Property listing pages (For Lease properties)
- Property listing pages (For Sale properties)
- Next steps page

The application supports both BusiVet and BusiHealth branding.

## Project Structure

```
property_report_generator/
│
├── generate_report.py         # Script for direct local execution
├── app.py                     # Flask web application
├── static/                    # Static assets for web app
│   ├── css/
│   │   └── styles.css         # CSS for the web interface
│   ├── js/
│   │   └── script.js          # JavaScript for the UI
│   └── images/                # Image assets
│       ├── busivet_logo.png
│       ├── busihealth_logo.png
│       ├── busivet_watermark.png
│       ├── busihealth_watermark.png
│       ├── title_page_background.png    # Title page main image
│       ├── template_map.png
│       ├── address_icon.png
│       ├── floor_area_icon.png
│       ├── price_icon.png
│       ├── zoning_icon.png
│       ├── type_icon.png
│       ├── car_spaces_icon.png
│       ├── comment_icon.png
│       └── global_icon.png
│
├── templates/                 # HTML templates for web app
│   └── index.html             # Main interface
│
├── utils/                     # Shared utility modules
│   ├── __init__.py
│   ├── data_processor.py      # Process Excel/CSV data
│   └── pdf_generator.py       # Generate PDF reports
│
├── output/                    # Generated PDF reports directory
├── logs/                      # Log files directory
├── requirements.txt           # Dependencies
├── run.sh                     # Unix run script (for Mac)
└── README.md                  # Documentation & setup guide
```

## Setup & Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Initial Setup

1. **Clone or download** this repository to your computer

2. **Make the run script executable**:

   ```bash
   chmod +x run.sh
   ```

3. **Run the setup script** (will create a virtual environment and install dependencies):

   ```bash
   ./run.sh
   ```

### Required Image Assets

The following images need to be placed in the `static/images/` directory:

1. **Logo & Watermark Images**
   - `busivet_logo.png` - BusiVet logo
   - `busihealth_logo.png` - BusiHealth logo
   - `busivet_watermark.png` - BusiVet watermark for page backgrounds
   - `busihealth_watermark.png` - BusiHealth watermark for page backgrounds
   - `title_page_background.png` - Background image for cover page (top 3/5)

2. **Map Image**
   - `template_map.png` - Map image showing property locations

3. **Icons**
   - `address_icon.png` - Icon for property address
   - `floor_area_icon.png` - Icon for floor area
   - `price_icon.png` - Icon for price information
   - `zoning_icon.png` - Icon for zoning information
   - `type_icon.png` - Icon for property type
   - `car_spaces_icon.png` - Icon for car spaces
   - `comment_icon.png` - Icon for comments
   - `global_icon.png` - Icon for website URL

## Usage Instructions

### Option 1: Running as a Local Script

Run the generator script directly from the command line:

```bash
# Interactive mode (with prompts)
./run.sh local

# OR run the Python script directly with arguments
python generate_report.py --file data.xlsx --business busivet --title "Landscape Report" --location "Sydney Area" --date "10 April 2025"
```

### Option 2: Running as a Web Application

Start the web application:

```bash
./run.sh
```

Then open your browser and go to: `http://127.0.0.1:5000`

Fill in the form:
- Select business type (BusiVet or BusiHealth)
- Enter report title line
- Enter location line
- Enter report date
- Upload Excel/CSV file with property data
- Click "Generate Report" to create and download the PDF

## Excel/CSV Format Requirements

The uploaded file must include these key columns:

- `Type` - Property type ('For Sale', 'For Lease', 'Sold', 'Already Leased')
- `Property Photo` - Path to property image
- `Street Address` - Property street address
- `Suburb` - Suburb name (in all caps)
- `State` - State abbreviation
- `Postcode` - Postal code
- `Site Zoning` - Zoning information
- `Property Type` - Type of property (e.g., 'Commercial')
- `Car` - Number of car spaces
- `Floor Size (m²)` - Floor size in square meters
- `Sale Price` - For 'Sold' properties
- `Last Listed Price` - For 'For Sale' properties
- `Last Rental Price` - For 'For Lease' or 'Already Leased' properties
- `PUT IN REPORT (T/F)` - Whether to include in report ('T' or 'F')
- `Busi's Comment` - Comments to include in report
- `$/m²` - Price per square meter

## Troubleshooting

The application logs detailed information to the `logs` directory:

- `property_report_*.log` - Logs from local script execution
- `webapp_*.log` - Logs from web application execution

Common issues:
- Missing image assets will be logged as warnings
- Invalid file formats will be rejected
- Missing required columns in the Excel/CSV will cause errors