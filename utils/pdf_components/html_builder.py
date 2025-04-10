"""
HTML Builder module for creating HTML from templates and data.

This module uses Jinja2 to render templates with data and generate full HTML.
"""

import os
import jinja2
from . import templates

class HtmlBuilder:
    """
    Class for building HTML from templates and data using Jinja2.
    """
    
    def __init__(self, static_dir):
        """
        Initialize HTML builder with paths to assets.
        
        Args:
            static_dir (str): Path to static assets directory
        """
        self.static_dir = static_dir
        self.images_dir = os.path.join(static_dir, 'images')
        self.watermark_path = None  # Will be set during build_html
        
        # Setup Jinja2 environment
        template_loader = jinja2.FunctionLoader(self._get_template)
        self.env = jinja2.Environment(
            loader=template_loader,
            autoescape=jinja2.select_autoescape(['html', 'xml'])
        )
        
        # Add template for CSS
        css_path = os.path.join(os.path.dirname(__file__), 'styles.css')
        with open(css_path, 'r') as f:
            self.css_content = f.read()
        
        # Register CSS to include in templates
        self.env.globals['include'] = self._include_resource
        
    def _include_resource(self, template_name):
        """Include external resources like CSS in templates"""
        if template_name == 'styles.css':
            return self.css_content
        return ""
    
    def _get_template(self, name):
        """Get template content based on name."""
        templates_map = {
            'head': templates.get_html_head(),
            'footer': templates.get_html_footer(),
            'cover_page': templates.get_cover_page_template(),
            'map_page': templates.get_map_page_template(),
            'property_page_header': templates.get_property_page_header_template(),
            'property_item': templates.get_property_item_template(),
            'property_page_footer': templates.get_property_page_footer_template(),
            'next_steps': templates.get_next_steps_template()
        }
        
        if name in templates_map:
            return templates_map[name]
        return ""
    
    def build_html(self, data, business_type, second_line, third_line, report_date):
        """
        Build complete HTML for the report.
        
        Args:
            data (dict): Processed property data
            business_type (str): 'busivet' or 'busihealth'
            second_line (str): Second line of title text
            third_line (str): Third line of title text (location)
            report_date (str): Report date string
            
        Returns:
            str: Complete HTML for the report
        """
        html_parts = []
        
        # Add HTML head
        head_template = self.env.get_template('head')
        html_parts.append(head_template.render())
        
        # Define paths
        logo_path = os.path.join(self.images_dir, f'{business_type}_logo.png')
        self.watermark_path = os.path.join(self.images_dir, f'{business_type}_watermark.png')
        title_background_path = os.path.join(self.images_dir, 'title_page_background.png')
        map_path = os.path.join(self.images_dir, 'template_map.png')
        global_icon_path = os.path.join(self.images_dir, 'global_icon.png')
        
        # Icon paths
        icon_paths = {
            'address_icon_path': os.path.join(self.images_dir, 'address_icon.png'),
            'floor_area_icon_path': os.path.join(self.images_dir, 'floor_area_icon.png'),
            'price_icon_path': os.path.join(self.images_dir, 'price_icon.png'),
            'zoning_icon_path': os.path.join(self.images_dir, 'zoning_icon.png'),
            'type_icon_path': os.path.join(self.images_dir, 'type_icon.png'),
            'car_spaces_icon_path': os.path.join(self.images_dir, 'car_spaces_icon.png'),
            'comment_icon_path': os.path.join(self.images_dir, 'comment_icon.png')
        }
        
        # Set business info
        if business_type.lower() == 'busivet':
            website = 'BUSIVET.COM.AU'
            email = 'BEN@BUSIVET.COM.AU'
            first_line = 'Vet Partners'
        else:  # busihealth
            website = 'BUSIHEALTH.COM'
            email = 'BEN@BUSIHEALTH.COM'
            first_line = 'Health Partners'
        
        # Build cover page
        cover_template = self.env.get_template('cover_page')
        cover_html = cover_template.render(
            business_type=business_type,
            logo_path=logo_path,
            title_background_path=title_background_path,
            first_line=first_line,
            second_line=second_line,
            third_line=third_line,
            report_date=report_date,
            website=website,
            email=email,
            global_icon_path=global_icon_path
        )
        html_parts.append(cover_html)
        
        # Build map page
        map_template = self.env.get_template('map_page')
        map_html = map_template.render(
            business_type=business_type,
            logo_path=logo_path,
            map_path=map_path,
            location=third_line,
            report_date=report_date,
            statistics=data['statistics'],
            website=website,
            watermark_path=self.watermark_path
        )
        html_parts.append(map_html)
        
        # Build property pages - For Lease
        if data['for_lease_properties']:
            self._add_property_pages(
                html_parts, 
                'FOR LEASE', 
                data['for_lease_properties'], 
                business_type, 
                logo_path, 
                icon_paths, 
                report_date, 
                website
            )
        
        # Build property pages - For Sale
        if data['for_sale_properties']:
            self._add_property_pages(
                html_parts, 
                'FOR SALE', 
                data['for_sale_properties'], 
                business_type, 
                logo_path, 
                icon_paths, 
                report_date, 
                website
            )
        
        # Build next steps page
        next_steps_template = self.env.get_template('next_steps')
        next_steps_html = next_steps_template.render(
            business_type=business_type,
            logo_path=logo_path,
            report_date=report_date,
            website=website,
            watermark_path=self.watermark_path
        )
        html_parts.append(next_steps_html)
        
        # Add HTML footer
        footer_template = self.env.get_template('footer')
        html_parts.append(footer_template.render())
        
        return ''.join(html_parts)
    
    def _add_property_pages(self, html_parts, section_title, properties, business_type, logo_path, icon_paths, report_date, website):
        """Add property listing pages to the HTML parts list."""
        
        properties_per_page = 3  # Maximum properties per page
        property_chunks = [properties[i:i+properties_per_page] for i in range(0, len(properties), properties_per_page)]
        
        for chunk in property_chunks:
            # Add page header
            header_template = self.env.get_template('property_page_header')
            header_html = header_template.render(
                section_title=section_title,
                business_type=business_type,
                logo_path=logo_path,
                report_date=report_date,
                watermark_path=self.watermark_path
            )
            html_parts.append(header_html)
            
            # Add each property
            for i, property_data in enumerate(chunk):
                property_type = "LEASE" if section_title == "FOR LEASE" else "SALE"
                
                # Create normalized property object with correct field names
                property = {
                    'suburb': property_data['suburb'],
                    'suburb_formatted': property_data['suburb_formatted'],
                    'street_address': property_data['street address'],
                    'floor_area': property_data['floor area'],
                    'price': property_data['price'],
                    'zoning': property_data['zoning'],
                    'property_type': property_data['property type'],
                    'car_spaces': property_data['car spaces'],
                    'comments': property_data.get('comments', ''),
                    'image': property_data.get('image')
                }
                
                # Render property item template
                item_template = self.env.get_template('property_item')
                item_html = item_template.render(
                    property=property,
                    property_type=property_type,
                    **icon_paths,
                    loop={'index': i+1, 'last': i == len(chunk)-1},
                    properties_per_page=properties_per_page
                )
                html_parts.append(item_html)
            
            # Add page footer
            footer_template = self.env.get_template('property_page_footer')
            footer_html = footer_template.render(
                website=website
            )
            html_parts.append(footer_html)