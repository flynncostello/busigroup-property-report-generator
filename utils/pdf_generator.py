"""
PDF Generator module for creating property report PDFs.

This module handles the creation of formatted PDF reports with property data.
"""

import os
import sys
import logging
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, Table, 
    TableStyle, PageBreak, Frame, PageTemplate, BaseDocTemplate,
    NextPageTemplate
)
from reportlab.pdfgen import canvas
from io import BytesIO

# Set up logger for this module
logger = logging.getLogger(__name__)

# Define constants
ORANGE_COLOR = colors.Color(235/255, 150/255, 91/255)  # RGB: (235, 150, 91)
BLUE_COLOR = colors.Color(62/255, 91/255, 162/255)     # RGB: (62, 91, 162)
LIGHT_GREY_COLOR = colors.Color(0.95, 0.95, 0.95)

# Custom function to convert ReportLab color to hex
def color_to_hex(color):
    """Convert a reportlab color to a hex string."""
    r = int(color.red * 255)
    g = int(color.green * 255)
    b = int(color.blue * 255)
    return f'#{r:02x}{g:02x}{b:02x}'

# Ensure paths to static assets
STATIC_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static')
IMAGES_DIR = os.path.join(STATIC_DIR, 'images')
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'output')

# Ensure the output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)
logger.info(f"Static directory path: {STATIC_DIR}")
logger.info(f"Images directory path: {IMAGES_DIR}")
logger.info(f"Output directory path: {OUTPUT_DIR}")

def generate_pdf(data, business_type, second_line, third_line, report_date):
    """
    Generate a complete property report PDF.
    
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
    
    # Define paths to assets based on business type
    if business_type.lower() == 'busivet':
        logo_path = os.path.join(IMAGES_DIR, 'busivet_logo.png')
        watermark_path = os.path.join(IMAGES_DIR, 'busivet_watermark.png')
        website = 'BUSIVET.COM.AU'
        email = 'BEN@BUSIVET.COM.AU'
        first_line = 'Vet Partners'
        logger.info(f"Using BusiVet branding - Logo: {logo_path}")
    else:  # busihealth
        logo_path = os.path.join(IMAGES_DIR, 'busihealth_logo.png')
        watermark_path = os.path.join(IMAGES_DIR, 'busihealth_watermark.png')
        website = 'BUSIHEALTH.COM'
        email = 'BEN@BUSIHEALTH.COM'
        first_line = 'Health Partners'
        logger.info(f"Using BusiHealth branding - Logo: {logo_path}")
    
    # Define path to title page background image
    title_background_path = os.path.join(IMAGES_DIR, 'title_page_background.png')
    logger.info(f"Title page background image: {title_background_path}")
    
    # Define path to map image
    map_path = os.path.join(IMAGES_DIR, 'template_map.png')
    logger.info(f"Map image path: {map_path}")
    
    # Define paths to icons
    address_icon_path = os.path.join(IMAGES_DIR, 'address_icon.png')
    floor_area_icon_path = os.path.join(IMAGES_DIR, 'floor_area_icon.png')
    price_icon_path = os.path.join(IMAGES_DIR, 'price_icon.png')
    zoning_icon_path = os.path.join(IMAGES_DIR, 'zoning_icon.png')
    type_icon_path = os.path.join(IMAGES_DIR, 'type_icon.png')
    car_spaces_icon_path = os.path.join(IMAGES_DIR, 'car_spaces_icon.png')
    comment_icon_path = os.path.join(IMAGES_DIR, 'comment_icon.png')
    global_icon_path = os.path.join(IMAGES_DIR, 'global_icon.png')
    
    logger.info("Icon paths defined")
    
    # Create the output PDF filepath
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_filename = f"{business_type.lower()}_report_{timestamp}.pdf"
    output_path = os.path.join(OUTPUT_DIR, output_filename)
    logger.info(f"Output PDF will be saved to: {output_path}")
    
    # Create a PDF document
    doc = CustomDocTemplate(
        output_path,
        pagesize=A4,
        topMargin=0.5*inch,
        leftMargin=0.5*inch,
        rightMargin=0.5*inch,
        bottomMargin=0.5*inch,
        business_type=business_type,
        logo_path=logo_path,
        watermark_path=watermark_path,
        website=website
    )
    
    # Create a story (content) for the document
    story = []
    
    logger.info("Creating cover page")
    # Add cover page
    story.extend(
        create_cover_page(
            logo_path, 
            title_background_path,
            first_line, 
            second_line, 
            third_line, 
            report_date, 
            website, 
            email,
            global_icon_path
        )
    )
    
    logger.info("Creating map page with statistics")
    # Add map page with statistics
    story.extend(
        create_map_page(
            logo_path,
            map_path,
            third_line,
            report_date,
            data['statistics'],
            website
        )
    )
    
    logger.info(f"Creating property pages for {len(data['for_lease_properties'])} 'For Lease' properties")
    # Add For Lease properties pages
    if data['for_lease_properties']:
        story.extend(
            create_property_pages(
                logo_path,
                'FOR LEASE',
                report_date,
                data['for_lease_properties'],
                website,
                address_icon_path,
                floor_area_icon_path,
                price_icon_path,
                zoning_icon_path,
                type_icon_path,
                car_spaces_icon_path,
                comment_icon_path
            )
        )
    
    logger.info(f"Creating property pages for {len(data['for_sale_properties'])} 'For Sale' properties")
    # Add For Sale properties pages
    if data['for_sale_properties']:
        story.extend(
            create_property_pages(
                logo_path,
                'FOR SALE',
                report_date,
                data['for_sale_properties'],
                website,
                address_icon_path,
                floor_area_icon_path,
                price_icon_path,
                zoning_icon_path,
                type_icon_path,
                car_spaces_icon_path,
                comment_icon_path
            )
        )
    
    logger.info("Creating Next Steps page")
    # Add Next Steps page
    story.extend(
        create_next_steps_page(
            logo_path,
            report_date,
            website,
            business_type
        )
    )
    
    # Build the document
    logger.info("Building PDF document")
    doc.build(story)
    
    logger.info(f"PDF generated at {output_path}")
    return output_path

class CustomDocTemplate(BaseDocTemplate):
    """
    Custom document template for the property report with specific headers and footers.
    """
    def __init__(self, filename, pagesize=A4, **kwargs):
        self.business_type = kwargs.pop('business_type', 'busivet')
        self.logo_path = kwargs.pop('logo_path', None)
        self.watermark_path = kwargs.pop('watermark_path', None)
        self.website = kwargs.pop('website', 'BUSIVET.COM.AU')
        
        super().__init__(filename, pagesize=pagesize, **kwargs)
        
        # Create page templates
        self.addPageTemplates(
            [
                # Cover page (no header/footer)
                PageTemplate(
                    id='cover',
                    frames=[
                        Frame(
                            self.leftMargin,
                            self.bottomMargin,
                            self.width,
                            self.height,
                            id='cover_frame'
                        )
                    ]
                ),
                # Content pages with watermark
                PageTemplate(
                    id='content',
                    frames=[
                        Frame(
                            self.leftMargin,
                            self.bottomMargin + 40,  # Adjust for footer space
                            self.width,
                            self.height - 40,  # Reserve space for footer
                            id='content_frame'
                        )
                    ],
                    onPage=self.add_page_decorations
                )
            ]
        )
    
    def add_page_decorations(self, canvas, doc):
        """Add watermark to the page background and footer."""
        # Draw the watermark at 10% opacity as background
        if self.watermark_path and os.path.exists(self.watermark_path):
            canvas.saveState()
            canvas.setFillColorRGB(1, 1, 1, 0.95)  # RGBA (95% opacity)
            canvas.drawImage(
                self.watermark_path,
                0,
                0,
                width=doc.pagesize[0],
                height=doc.pagesize[1],
                mask='auto'
            )
            canvas.restoreState()
            
        # Draw the footer with website URL
        canvas.saveState()
        
        # Draw blue footer background
        canvas.setFillColor(BLUE_COLOR)
        canvas.rect(0, 0, doc.pagesize[0], 40, fill=1, stroke=0)
        
        # Draw website text
        canvas.setFillColor(colors.white)
        canvas.setFont("Helvetica", 10)
        text_width = canvas.stringWidth(self.website, "Helvetica", 10)
        canvas.drawString((doc.pagesize[0] - text_width) / 2, 15, self.website)
        
        canvas.restoreState()

def create_cover_page(logo_path, title_background_path, first_line, second_line, third_line, report_date, website, email, global_icon_path):
    """
    Create the cover page for the property report.
    
    Args:
        logo_path (str): Path to the logo image
        title_background_path (str): Path to the title page background image
        first_line (str): First line of big text (e.g., 'Vet Partners')
        second_line (str): Second line of big text (e.g., 'Landscape Report & Site Search')
        third_line (str): Third line of big text (e.g., 'Oran Park & Mickleham')
        report_date (str): Date for the report (e.g., '26 March 2025')
        website (str): Website URL (e.g., 'BUSIVET.COM.AU')
        email (str): Email address (e.g., 'BEN@BUSIVET.COM.AU')
        global_icon_path (str): Path to the global icon image
        
    Returns:
        list: List of flowables for the cover page
    """
    logger.info("Creating cover page content")
    
    # Create styles
    styles = getSampleStyleSheet()
    
    # Create custom styles for cover page
    title_style = ParagraphStyle(
        'CoverTitle',
        parent=styles['Title'],
        fontName='Helvetica-Bold',
        fontSize=36,
        alignment=TA_CENTER,
        textColor=colors.white,
        spaceAfter=5
    )
    
    subtitle_style = ParagraphStyle(
        'CoverSubtitle',
        parent=styles['Title'],
        fontName='Helvetica',
        fontSize=28,
        alignment=TA_CENTER,
        textColor=colors.white,
        spaceAfter=5
    )
    
    date_style = ParagraphStyle(
        'CoverDate',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=14,
        alignment=TA_CENTER,
        textColor=colors.white
    )
    
    website_style = ParagraphStyle(
        'WebsiteStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        alignment=TA_CENTER,
        textColor=colors.white
    )
    
    email_style = ParagraphStyle(
        'EmailStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        alignment=TA_CENTER,
        textColor=colors.white
    )
    
    # Create content
    elements = []
    
    # Logo with white background at top center
    elements.append(Spacer(1, 0.5*inch))  # 0.5 inch top margin
    
    # Create a table with a white background for the logo
    if os.path.exists(logo_path):
        img = Image(logo_path)
        img_width = 2*inch
        img_height = 1.2*inch
        img.drawWidth = img_width
        img.drawHeight = img_height
        
        logo_table = Table(
            [[img]],
            colWidths=[img_width],
            rowHeights=[img_height]
        )
        
        logo_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BACKGROUND', (0, 0), (-1, -1), colors.white),
            ('BOX', (0, 0), (-1, -1), 1, colors.white),
        ]))
        
        logo_table.hAlign = 'CENTER'
        elements.append(logo_table)
    else:
        logger.warning(f"Logo image not found at: {logo_path}")
    
    elements.append(Spacer(1, 0.1*inch))  # Space after logo
    
    # Add title page background image (proportionally sized)
    if os.path.exists(title_background_path):
        bg_img = Image(title_background_path)
        # Set to appropriate dimensions (top 2/3 of the page)
        bg_img.drawWidth = 7.5*inch
        bg_img.drawHeight = 4*inch
        bg_img.hAlign = 'CENTER'
        elements.append(bg_img)
    else:
        logger.warning(f"Title background image not found at: {title_background_path}")
        # Spacer as fallback
        elements.append(Spacer(1, 4*inch))
    
    # Add orange divider line (10px height, full width)
    elements.append(
        Paragraph(
            f'<hr width="100%" height="10" color="{color_to_hex(ORANGE_COLOR)}"/>',
            styles['Normal']
        )
    )
    
    # Create blue background div for text sections
    blue_background = Table(
        [[Paragraph(f'<font color="white">{first_line}</font>', title_style)],
         [Paragraph(f'<font color="white">{second_line}</font>', subtitle_style)],
         [Paragraph(f'<font color="white">{third_line}</font>', subtitle_style)],
         [Spacer(1, 20)],  # Space before date
         [Paragraph(
             f'''<table width="40%" align="center" bgcolor="{color_to_hex(ORANGE_COLOR)}" style="border-radius: 5px; padding: 10px;">
                 <tr><td align="center">{report_date}</td></tr>
                </table>''',
             date_style
         )],
         [Spacer(1, 40)]  # Space before footer
        ],
        colWidths=[7*inch],
        style=TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), BLUE_COLOR),
            ('ALIGN', (0, 0), (0, -1), 'CENTER'),
            ('VALIGN', (0, 0), (0, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (0, -2), 15),
        ])
    )
    elements.append(blue_background)
    
    # Add website and email in a footer section
    footer_table = Table(
        [[
            Spacer(1, 0),
            Image(global_icon_path, width=0.3*inch, height=0.3*inch) if os.path.exists(global_icon_path) else Spacer(1, 0.3*inch),
            Paragraph(website, website_style),
            Spacer(1, 0)
        ],
        [
            Spacer(1, 0),
            Spacer(1, 0.3*inch),
            Paragraph(email, email_style),
            Spacer(1, 0)
        ]],
        colWidths=[1*inch, 0.3*inch, 4.4*inch, 1*inch],
        style=TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), BLUE_COLOR),
            ('ALIGN', (2, 0), (2, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('SPAN', (1, 0), (1, 0)),  # Just for the icon
            ('SPAN', (1, 1), (1, 1)),  # Empty cell
        ])
    )
    elements.append(footer_table)
    
    # Add page break and switch to content template for next pages
    elements.append(PageBreak())
    elements.append(NextPageTemplate('content'))
    
    return elements

def create_map_page(logo_path, map_path, location, report_date, statistics, website):
    """
    Create the map page with statistics table.
    
    Args:
        logo_path (str): Path to the logo image
        map_path (str): Path to the map image
        location (str): Location text (e.g., 'Oran Park & Mickleham')
        report_date (str): Date for the report (e.g., '26 March 2025')
        statistics (dict): Statistics data for the table
        website (str): Website URL (e.g., 'BUSIVET.COM.AU')
        
    Returns:
        list: List of flowables for the map page
    """
    logger.info("Creating map page content")
    
    # Create styles
    styles = getSampleStyleSheet()
    
    # Create custom styles
    header_style = ParagraphStyle(
        'MapHeader',
        parent=styles['Title'],
        fontName='Helvetica',
        fontSize=16,
        alignment=TA_LEFT,
        textColor=BLUE_COLOR,
        spaceAfter=10
    )
    
    normal_style = ParagraphStyle(
        'MapNormal',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        alignment=TA_CENTER,
        spaceAfter=5
    )
    
    footnote_style = ParagraphStyle(
        'MapFootnote',
        parent=styles['Italic'],
        fontName='Helvetica',
        fontSize=8,
        alignment=TA_CENTER,
        textColor=colors.gray
    )
    
    # Create content
    elements = []
    
    # Add title and logo in a table
    title_text = f"{location.upper()} & SURROUNDS ({report_date.upper()})"
    
    header_table_data = [
        [
            Paragraph(title_text, header_style),
            Image(logo_path, width=1*inch, height=0.6*inch) if os.path.exists(logo_path) else Paragraph("", normal_style)
        ]
    ]
    
    header_table = Table(
        header_table_data,
        colWidths=[6*inch, 1*inch]
    )
    
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (0, 0), 'LEFT'),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
    ]))
    
    elements.append(header_table)
    
    # Add orange divider (10px height, 95% width)
    elements.append(
        Paragraph(
            f'<hr width="95%" height="10" color="{color_to_hex(ORANGE_COLOR)}" align="center"/>',
            styles['Normal']
        )
    )
    
    # Add map image with preserved aspect ratio
    if os.path.exists(map_path):
        map_img = Image(map_path)
        map_img.drawWidth = 6.5*inch
        # Calculate height based on original aspect ratio
        map_img.drawHeight = 3.5*inch  # Maintain proportion
        map_img.hAlign = 'CENTER'  # Center the map
        elements.append(map_img)
    else:
        logger.warning(f"Map image not found at: {map_path}")
        elements.append(Spacer(1, 3.5*inch))  # Spacer as fallback
    
    elements.append(Spacer(1, 0.2*inch))  # Space before table
    
    # Create statistics table with proper styling
    table_data = [
        # Header row
        [
            Paragraph(f"<b>{location}</b>", normal_style),
            Paragraph(f"<b>For Lease/Sale<br/>Last 12 months to<br/>{report_date}</b>", normal_style),
            Paragraph("<b>Meet Criteria &<br/>Available</b>", normal_style),
            Paragraph("<b>$/m2<br/>(average)</b>", normal_style)
        ],
        # Sites Available For Lease row
        [
            Paragraph("<b>Sites Available<br/>For Lease</b>", normal_style),
            Paragraph(f"{statistics['for_lease']['total']}", normal_style),
            Paragraph(f"{statistics['for_lease']['criteria']}", normal_style),
            Paragraph(f"${statistics['for_lease']['avg_price']}", normal_style)
        ],
        # Leased row
        [
            Paragraph("Leased<br/>(last 12 mths)", normal_style),
            Paragraph(f"{statistics['already_leased']['total']}", normal_style),
            Paragraph(f"{statistics['already_leased']['criteria']}", normal_style),
            Paragraph(f"${statistics['already_leased']['avg_price']}", normal_style)
        ],
        # Sites Available For Sale row
        [
            Paragraph("<b>Sites Available<br/>For Sale</b>", normal_style),
            Paragraph(f"{statistics['for_sale']['total']}", normal_style),
            Paragraph(f"{statistics['for_sale']['criteria']}", normal_style),
            Paragraph(f"${statistics['for_sale']['avg_price']}", normal_style)
        ],
        # Sold row
        [
            Paragraph("Sold<br/>(last 12 mths)", normal_style),
            Paragraph(f"{statistics['sold']['total']}", normal_style),
            Paragraph(f"{statistics['sold']['criteria']}", normal_style),
            Paragraph(f"${statistics['sold']['avg_price']}", normal_style)
        ]
    ]
    
    # Define table style - no borders between cells, proper coloring
    table_style = TableStyle([
        # Header row - orange background with white text
        ('BACKGROUND', (0, 0), (-1, 0), ORANGE_COLOR),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        
        # Left column headers - light grey background with blue text
        ('BACKGROUND', (0, 1), (0, -1), LIGHT_GREY_COLOR),
        ('TEXTCOLOR', (0, 1), (0, -1), BLUE_COLOR),
        
        # Center alignment for all cells
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        
        # Blue text for data cells
        ('TEXTCOLOR', (1, 1), (-1, -1), BLUE_COLOR),
        
        # Orange borders for highlighted cells
        ('BOX', (2, 1), (2, 1), 1, ORANGE_COLOR),  # For Lease - Meet Criteria
        ('BOX', (2, 3), (2, 3), 1, ORANGE_COLOR),  # For Sale - Meet Criteria
        
        # Cell borders for all cells
        ('GRID', (0, 0), (-1, -1), 0.5, colors.white),
        
        # Row padding
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ])
    
    # Create table with style
    statistics_table = Table(
        table_data,
        colWidths=[2*inch, 1.5*inch, 1.5*inch, 1.5*inch],
        style=table_style
    )
    
    elements.append(statistics_table)
    
    # Add footnote
    elements.append(Spacer(1, 15))
    elements.append(
        Paragraph(
            "*Rate reflects type of comparable properties",
            footnote_style
        )
    )
    
    elements.append(PageBreak())
    
    return elements

def create_property_pages(logo_path, section_title, report_date, properties, website,
                          address_icon_path, floor_area_icon_path, price_icon_path, 
                          zoning_icon_path, type_icon_path, car_spaces_icon_path, 
                          comment_icon_path):
    """
    Create pages for property listings, with 3 properties per page.
    
    Args:
        logo_path (str): Path to the logo image
        section_title (str): Section title ('FOR LEASE' or 'FOR SALE')
        report_date (str): Date for the report
        properties (list): List of property data dictionaries
        website (str): Website URL
        address_icon_path (str): Path to the address icon
        floor_area_icon_path (str): Path to the floor area icon
        price_icon_path (str): Path to the price icon
        zoning_icon_path (str): Path to the zoning icon
        type_icon_path (str): Path to the property type icon
        car_spaces_icon_path (str): Path to the car spaces icon
        comment_icon_path (str): Path to the comment icon
        
    Returns:
        list: List of flowables for the property pages
    """
    logger.info(f"Creating {section_title} property pages")
    
    # Create styles
    styles = getSampleStyleSheet()
    
    # Create custom styles
    title_style = ParagraphStyle(
        'PropertyTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=16,
        alignment=TA_LEFT,
        textColor=BLUE_COLOR,
        spaceAfter=5
    )
    
    section_title_style = ParagraphStyle(
        'SectionTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=16,
        alignment=TA_LEFT,
        textColor=BLUE_COLOR,
        opacity=0.8,
        spaceBefore=5,
        spaceAfter=5,
        leading=20
    )
    
    date_style = ParagraphStyle(
        'PropertyDate',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=16,
        alignment=TA_CENTER,
        textColor=BLUE_COLOR
    )
    
    subtitle_style = ParagraphStyle(
        'PropertySubtitle',
        parent=styles['Heading2'],
        fontName='Helvetica',
        fontSize=14,
        alignment=TA_LEFT,
        textColor=BLUE_COLOR,
        spaceAfter=5
    )
    
    normal_style = ParagraphStyle(
        'PropertyNormal',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        textColor=BLUE_COLOR,
        spaceAfter=5
    )
    
    orange_text_style = ParagraphStyle(
        'OrangeText',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        textColor=ORANGE_COLOR
    )
    
    blue_text_style = ParagraphStyle(
        'BlueText',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        textColor=BLUE_COLOR
    )
    
    # Create content
    elements = []
    
    # Divide properties into chunks of 3 per page
    property_chunks = [properties[i:i+3] for i in range(0, len(properties), 3)]
    
    for page_index, chunk in enumerate(property_chunks):
        # Add header with section title, date, and logo
        header_table_data = [
            [
                Paragraph(f"{section_title}", section_title_style),
                Paragraph(f"{report_date}", date_style),
                Image(logo_path, width=1*inch, height=0.6*inch) if os.path.exists(logo_path) else Paragraph("", normal_style)
            ]
        ]
        
        header_table = Table(
            header_table_data,
            colWidths=[2.5*inch, 2.5*inch, 2*inch]
        )
        
        header_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'CENTER'),
            ('ALIGN', (2, 0), (2, 0), 'RIGHT'),
        ]))
        
        elements.append(header_table)
        
        # Add orange divider (10px height, 95% width)
        elements.append(
            Paragraph(
                f'<hr width="95%" height="10" color="{color_to_hex(ORANGE_COLOR)}" align="center"/>',
                styles['Normal']
            )
        )
        
        # Add each property in the chunk
        for i, property_data in enumerate(chunk):
            # Create property entry
            # Property header with suburb
            elements.append(
                Paragraph(
                    f"{property_data['suburb']}",
                    title_style
                )
            )
            
            # Property subheader (LEASE or SALE)
            property_type = "LEASE" if section_title == "FOR LEASE" else "SALE"
            elements.append(
                Paragraph(
                    f"{property_type}",
                    subtitle_style
                )
            )
            
            # Create property details and image table
            # Property details (left) and image (right)
            property_image = None
            if 'image' in property_data and property_data['image'] and property_data['image'] != 'nan':
                try:
                    # Try to load image if path is provided
                    logger.debug(f"Loading property image: {property_data['image']}")
                    property_image = Image(property_data['image'], width=2*inch, height=1.5*inch)
                except Exception as e:
                    logger.warning(f"Could not load property image: {str(e)}")
            
            # If no image available, use a placeholder
            if not property_image:
                logger.debug("Using placeholder for property image")
                property_image = Paragraph("No Image Available", normal_style)
            
            # Create property details content
            details_content = []
            
            # Address with icon
            address_content = []
            if os.path.exists(address_icon_path):
                address_icon = Image(address_icon_path, width=0.2*inch, height=0.2*inch)
                address_content.append(address_icon)
            else:
                address_content.append(Paragraph("", normal_style))
            
            address_content.append(
                Paragraph(
                    f"Address: <font color='{color_to_hex(ORANGE_COLOR)}'><b>{property_data['street address']}</b></font>, <font color='{color_to_hex(BLUE_COLOR)}'><b>{property_data['suburb_formatted']}</b></font>",
                    normal_style
                )
            )
            details_content.append(address_content)
            
            # Floor Area with icon
            floor_area_content = []
            if os.path.exists(floor_area_icon_path):
                floor_area_icon = Image(floor_area_icon_path, width=0.2*inch, height=0.2*inch)
                floor_area_content.append(floor_area_icon)
            else:
                floor_area_content.append(Paragraph("", normal_style))
            
            floor_area_content.append(
                Paragraph(
                    f"Floor Area: {property_data['floor area']}m²",
                    normal_style
                )
            )
            details_content.append(floor_area_content)
            
            # Price with icon
            price_content = []
            if os.path.exists(price_icon_path):
                price_icon = Image(price_icon_path, width=0.2*inch, height=0.2*inch)
                price_content.append(price_icon)
            elif os.path.exists(floor_area_icon_path):  # Fallback
                price_icon = Image(floor_area_icon_path, width=0.2*inch, height=0.2*inch)
                price_content.append(price_icon)
            else:
                price_content.append(Paragraph("", normal_style))
            
            price_content.append(
                Paragraph(
                    f"Price: {property_data['price']}",
                    normal_style
                )
            )
            details_content.append(price_content)
            
            # Zoning with icon
            zoning_content = []
            if os.path.exists(zoning_icon_path):
                zoning_icon = Image(zoning_icon_path, width=0.2*inch, height=0.2*inch)
                zoning_content.append(zoning_icon)
            else:
                zoning_content.append(Paragraph("", normal_style))
            
            zoning_content.append(
                Paragraph(
                    f"Zoning: {property_data['zoning']}",
                    normal_style
                )
            )
            details_content.append(zoning_content)
            
            # Property Type with icon
            property_type_content = []
            if os.path.exists(type_icon_path):
                type_icon = Image(type_icon_path, width=0.2*inch, height=0.2*inch)
                property_type_content.append(type_icon)
            else:
                property_type_content.append(Paragraph("", normal_style))
            
            property_type_content.append(
                Paragraph(
                    f"Type: {property_data['property type']}",
                    normal_style
                )
            )
            details_content.append(property_type_content)
            
            # Car Spaces with icon
            car_spaces_content = []
            if os.path.exists(car_spaces_icon_path):
                car_spaces_icon = Image(car_spaces_icon_path, width=0.2*inch, height=0.2*inch)
                car_spaces_content.append(car_spaces_icon)
            else:
                car_spaces_content.append(Paragraph("", normal_style))
            
            car_spaces_content.append(
                Paragraph(
                    f"Car Spaces: {property_data['car spaces']}",
                    normal_style
                )
            )
            details_content.append(car_spaces_content)
            
            # Comments with icon
            if property_data['comments'] and str(property_data['comments']).lower() != 'nan':
                comments_content = []
                if os.path.exists(comment_icon_path):
                    comment_icon = Image(comment_icon_path, width=0.2*inch, height=0.2*inch)
                    comments_content.append(comment_icon)
                else:
                    comments_content.append(Paragraph("", normal_style))
                
                comments_content.append(
                    Paragraph(
                        f"Comments: {property_data['comments']}",
                        normal_style
                    )
                )
                details_content.append(comments_content)
            
            # Create table for details content (icons + text)
            details_tables = []
            for detail_row in details_content:
                if len(detail_row) > 1:  # Only if we have both icon and text
                    detail_table = Table(
                        [detail_row],
                        colWidths=[0.3*inch, 4.5*inch]
                    )
                    detail_table.setStyle(TableStyle([
                        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                        ('ALIGN', (0, 0), (0, 0), 'CENTER'),
                        ('ALIGN', (1, 0), (1, 0), 'LEFT'),
                    ]))
                    details_tables.append(detail_table)
            
            # Create the main property table (details on left, image on right)
            property_table_data = [
                [details_tables, property_image]
            ]
            
            property_table = Table(
                property_table_data,
                colWidths=[5*inch, 2*inch]
            )
            
            property_table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('ALIGN', (0, 0), (0, 0), 'LEFT'),
                ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
            ]))
            
            elements.append(property_table)
            
            # Add a spacer and divider between properties (except for the last one on the page or the last property)
            if i < len(chunk) - 1:
                elements.append(Spacer(1, 20))  # 20px space
                
                # Get the current divider color based on property count (alternating)
                divider_color = BLUE_COLOR if i % 2 == 0 else ORANGE_COLOR
                
                # Add a divider with 90% width
                elements.append(
                    Paragraph(
                        f'<hr width="90%" height="10" color="{color_to_hex(divider_color)}" align="center"/>',
                        styles['Normal']
                    )
                )
                
                elements.append(Spacer(1, 20))  # 20px space after divider
        
        # Add a page break at the end of each chunk (page) except for the last one
        if page_index < len(property_chunks) - 1:
            elements.append(PageBreak())
    
    elements.append(PageBreak())
    
    return elements

def create_next_steps_page(logo_path, report_date, website, business_type):
    """
    Create the Next Steps page.
    
    Args:
        logo_path (str): Path to the logo image
        report_date (str): Date for the report
        website (str): Website URL
        business_type (str): 'busivet' or 'busihealth'
        
    Returns:
        list: List of flowables for the Next Steps page
    """
    logger.info("Creating Next Steps page")
    
    # Create styles
    styles = getSampleStyleSheet()
    
    # Create custom styles
    title_style = ParagraphStyle(
        'NextStepsTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=24,
        alignment=TA_CENTER,
        textColor=BLUE_COLOR,
        spaceAfter=20
    )
    
    date_style = ParagraphStyle(
        'NextStepsDate',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=16,
        alignment=TA_CENTER,
        textColor=BLUE_COLOR
    )
    
    normal_style = ParagraphStyle(
        'NextStepsNormal',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        alignment=TA_CENTER,
        spaceAfter=10,
        textColor=BLUE_COLOR
    )
    
    # Create content
    elements = []
    
    # Add date and logo header
    header_table_data = [
        [
            Paragraph("", normal_style),
            Paragraph(f"{report_date}", date_style),
            Image(logo_path, width=1*inch, height=0.6*inch) if os.path.exists(logo_path) else Paragraph("", normal_style)
        ]
    ]
    
    header_table = Table(
        header_table_data,
        colWidths=[2.5*inch, 2.5*inch, 2*inch]
    )
    
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (0, 0), 'LEFT'),
        ('ALIGN', (1, 0), (1, 0), 'CENTER'),
        ('ALIGN', (2, 0), (2, 0), 'RIGHT'),
    ]))
    
    elements.append(header_table)
    
    # Add orange divider (10px height)
    elements.append(
        Paragraph(
            f'<hr width="95%" height="10" color="{color_to_hex(ORANGE_COLOR)}" align="center"/>',
            styles['Normal']
        )
    )
    
    # Add title
    elements.append(Spacer(1, 40))
    elements.append(
        Paragraph(
            'NEXT STEPS:',
            title_style
        )
    )
    elements.append(Spacer(1, 40))
    
    # Add next steps content - centered
    elements.append(
        Paragraph(
            '• Please advise your review of the preferred sites (via markup) noting the pros and cons to assist in evaluation of these for further exploration.',
            normal_style
        )
    )
    
    elements.append(Spacer(1, 20))
    
    elements.append(
        Paragraph(
            f'• Busi{business_type.capitalize()[4:]} will then review this evaluation in collaboration with you to determine which sites are to be explored in depth.',
            normal_style
        )
    )
    
    return elements