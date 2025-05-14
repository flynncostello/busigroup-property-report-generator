import os
import logging
from weasyprint import HTML, CSS
from datetime import datetime
from .html_builder import HtmlBuilder

# Set up logger for this module
logger = logging.getLogger(__name__)

class PdfRenderer:
    """
    Class for rendering HTML as PDF.
    """
    
    def __init__(self, output_dir, static_dir):
        """
        Initialize PDF renderer with output directory path.
        
        Args:
            output_dir (str): Directory where PDFs will be saved
            static_dir (str): Directory containing static assets
        """
        self.output_dir = output_dir
        self.static_dir = static_dir
        self.html_builder = HtmlBuilder(static_dir)
        
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
    
    def render_pdf(self, data, business_type, first_line, second_line, third_line, report_date):
        """
        Render PDF from the processed data.
        
        Args:
            data (dict): Processed property data
            business_type (str): 'busivet' or 'busihealth'
            first_line (str): First line of title text
            second_line (str): Second line of title text
            third_line (str): Third line of title text (location)
            report_date (str): Report date string
            
        Returns:
            str: Path to the generated PDF file
        """
        logger.info(f"Generating PDF for {business_type} report")
        
        # Build HTML content
        html_content = self.html_builder.build_html(
            data, 
            business_type, 
            first_line,
            second_line, 
            third_line, 
            report_date
        )
        
        # Create output filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_filename = f"{business_type.lower()}_report_{timestamp}.pdf"
        output_path = os.path.join(self.output_dir, output_filename)
        
        # Get CSS path
        css_path = os.path.join(os.path.dirname(__file__), 'styles.css')
        
        try:
            # Generate PDF from HTML
            logger.info("Rendering HTML to PDF")
            
            # Create PDF using WeasyPrint with explicit margins set to 0
            base_url = self.static_dir  # Use static dir as base for relative paths
            
            # Generate the PDF
            HTML(string=html_content, base_url=base_url).write_pdf(
                output_path,
                stylesheets=[CSS(filename=css_path)]
            )
            
            logger.info(f"PDF saved to {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error rendering PDF: {str(e)}", exc_info=True)
            raise