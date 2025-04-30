"""
HTML templates for PDF generation.

This module contains the HTML templates for each section of the property report.
"""

def get_html_head():
    """
    Returns the HTML head section with CSS links
    """
    return """<!DOCTYPE html>
<html lang="en" style="margin: 0; padding: 0;">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Property Report</title>
    <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;700&display=swap" rel="stylesheet">
    <style>
        /* Override default margins and padding */
        @page { margin: 0; padding: 0; size: A4; }
        html, body { margin: 0 !important; padding: 0 !important; }
        
        /* Include CSS inline for PDF generation */
        {% include 'styles.css' %}
    </style>
</head>
<body style="margin: 0; padding: 0;">
"""

def get_html_footer():
    """
    Returns the HTML closing tags
    """
    return """
</body>
</html>
"""


def get_cover_page_template():
    """
    Returns the template for the cover page with improved image handling and proper sizing
    """
    return """
    <div class="page cover-page" style="height: 842pt">
        <!-- Cover page background image -->
        <img src="{{ title_background_path }}" alt="Cover background" class="cover-bg-image">
        
        <!-- Logo overlaid on top -->
        <div class="cover-logo-container">
            <div class="logo">
                <img src="{{ logo_path }}" alt="{{ business_type }} Logo" class="logo-image">
            </div>
        </div>
        
        <!-- Orange divider -->
        <div class="orange_divider_cover_page"></div>
        
        <!-- Blue content area -->
        <div class="cover-content">
            <h1 class="cover-title">{{ first_line }}</h1>
            <h2 class="cover-subtitle">{{ second_line }}</h2>
            <h2 class="cover-subtitle">{{ third_line }}</h2>
            
            <div class="date-box">{{ report_date }}</div>
        </div>
        
        <!-- Footer -->
        <div class="footer">
            <div style="display: flex; align-items: center; justify-content: center;">
                <img src="{{ global_icon_path }}" alt="Globe" class="globe-icon">
                <span>{{ website }}</span>
                <div class="footer-separator">|</div>
                <div>{{ email }}</div>
            </div>
        </div>
    </div>
    """



def get_map_page_template():
    """
    Returns the template for the map page
    """
    return """
<div class="page">
    <!-- Watermark -->
    <img src="{{ watermark_path }}" class="page-watermark" alt="Watermark">
    
    <div class="map-header">
        <div class="map-title">{{ location | upper }} ({{ report_date | upper }})</div>
        <img src="{{ logo_path }}" alt="{{ business_type }} Logo" style="height: 60px;">
    </div>
    
    <div class="orange-divider" style="width: 95%; margin-top: 15px;"></div>
    
    <img src="{{ map_path }}" alt="Area Map" class="map-image">
    
    <table class="stats-table">
        <thead>
            <tr>
                <th>{{ location | upper }}</th>
                <th>For Lease/Sale<br>Last 12 months to<br>{{ report_date }}</th>
                <th>Meet Criteria &<br>Available</th>
                <th>$/m2<br>(average)</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td class="left-header">Sites Available<br>For Lease</td>
                <td><strong>{{ statistics.for_lease.total }}</strong></td>
                <td {% if statistics.for_lease.criteria > 0 %}class="highlighted-cell"{% endif %}><strong>{{ statistics.for_lease.criteria }}</strong></td>
                <td><strong>${{ statistics.for_lease.avg_price }}</strong></td>
            </tr>
            <tr>
                <td class="left-header regular-row">Leased<br>(last 12 mths)</td>
                <td>{{ statistics.already_leased.total }}</td>
                <td>{{ statistics.already_leased.criteria }}</td>
                <td>${{ statistics.already_leased.avg_price }}</td>
            </tr>
            <tr>
                <td class="left-header">Sites Available<br>For Sale</td>
                <td><strong>{{ statistics.for_sale.total }}</strong></td>
                <td {% if statistics.for_sale.criteria > 0 %}class="highlighted-cell"{% endif %}><strong>{{ statistics.for_sale.criteria }}</strong></td>
                <td><strong>${{ statistics.for_sale.avg_price }}</strong></td>
            </tr>
            <tr>
                <td class="left-header regular-row">Sold<br>(last 12 mths)</td>
                <td>{{ statistics.sold.total }}</td>
                <td>{{ statistics.sold.criteria }}</td>
                <td>${{ statistics.sold.avg_price }}</td>
            </tr>
        </tbody>
    </table>
    
    <div class="footnote">*Rate reflects type of comparable properties</div>
    
    <div style="position: absolute; bottom: 0; left: 0; width: 100%; margin: 0; padding: 0;" class="blue-bg">
        <div style="text-align: center; padding: 15px; font-size: 12px">{{ website }}</div>
    </div>
</div>
"""

def get_property_page_header_template():
    """
    Returns the template for the property page header
    """
    return """
<div class="page">
    <!-- Watermark -->
    <img src="{{ watermark_path }}" class="page-watermark" alt="Watermark">
    
    <div class="property-header">
        <div class="property-title">{{ section_title }}</div>
        <div style="text-align: center; font-size: 25px; color: rgb(62, 91, 162); font-weight: 500; text-transform: uppercase;">{{ report_date }}</div>
        <img src="{{ logo_path }}" alt="{{ business_type }} Logo" style="height: 60px;">
    </div>
    
    <div class="orange-divider" style="margin-bottom=30px"></div>
"""


def get_property_item_template():
    """
    Returns the template for a property item
    """
    return """
    <div class="property-item">
        <div class="property-section-title">{{ property.suburb }}</div>
        <div class="property-subtitle">{{ property_type }}</div>
        
        <div class="property-details">
            <div class="details-column">
                <div class="detail-row">
                    <img src="{{ address_icon_path }}" alt="Address" class="icon">
                    <div>
                        <span class="detail-label">Address:</span>
                        <span class="detail-value detail-street">{{ property.street_address }}</span>,
                        <span class="detail-value detail-suburb">{{ property.suburb_formatted }}</span>
                    </div>
                </div>
                
                <div class="detail-row">
                    <img src="{{ floor_area_icon_path }}" alt="Floor Area" class="icon">
                    <div>
                        <span class="detail-label">Floor Area:</span>
                        <span class="detail-value normal">{{ property.floor_area }} m²</span>
                    </div>
                </div>
                
                <div class="detail-row">
                    <img src="{{ price_icon_path }}" alt="Price" class="icon">
                    <div>
                        <span class="detail-label">Price:</span>
                        <span class="detail-value normal">{{ property.price }}</span>
                    </div>
                </div>
                
                <div class="detail-row">
                    <img src="{{ zoning_icon_path }}" alt="Zoning" class="icon">
                    <div>
                        <span class="detail-label">Zoning:</span>
                        <span class="detail-value normal">{{ property.zoning }}</span>
                    </div>
                </div>
                
                <div class="detail-row">
                    <img src="{{ type_icon_path }}" alt="Type" class="icon">
                    <div>
                        <span class="detail-label">Type:</span>
                        <span class="detail-value normal">{{ property.property_type }}</span>
                    </div>
                </div>
                
                <div class="detail-row">
                    <img src="{{ car_spaces_icon_path }}" alt="Car Spaces" class="icon">
                    <div>
                        <span class="detail-label">Car Spaces:</span>
                        <span class="detail-value normal">{{ property.car_spaces }}</span>
                    </div>
                </div>
                
                {% if property.comments %}
                <div class="detail-row">
                    <img src="{{ comment_icon_path }}" alt="Comments" class="icon">
                    <div>
                        <span class="detail-label">Comments:</span>
                        <span class="detail-value normal">{{ property.comments }}</span>
                    </div>
                </div>
                {% endif %}
            </div>
            
            <div class="image-column">
                {% if property.image %}
                <img src="{{ property.image }}" alt="Property Image" class="property-image">
                {% else %}
                <div style="text-align: center; padding: 30px; border: 1px dashed #ccc;">No Image Available</div>
                {% endif %}
            </div>
        </div>
    </div>

    
    {% if not loop.last and loop.index != properties_per_page and loop.index != properties_per_page * 2 %}
    {% set divider_color = loop.index % 2 == 0 and "orange-divider" or "blue-divider" %}
    <div class="{{ divider_color }}"></div>
    {% endif %}
        
    {% if loop.index == properties_per_page or loop.index == properties_per_page * 2 or loop.last %}
    {# Close the if statement - fixes the template syntax error #}
    {% endif %}
    <div style="height: 0.5em;"></div>
"""

def get_property_page_footer_template():
    """
    Returns the template for the property page footer
    """
    return """
    <div style="position: absolute; bottom: 0; left: 0; width: 100%; margin: 0; padding: 0;" class="blue-bg">
        <div style="text-align: center; padding: 15px; font-size: 12px">{{ website }}</div>
    </div>
</div>
"""

def get_next_steps_template():
    """
    Returns the template for the next steps page
    """
    return """
<div class="page">
    <!-- Watermark -->
    <img src="{{ watermark_path }}" class="page-watermark" alt="Watermark">
    
    <div class="property-header">
        <div style="text-align: center; font-size: 25px; color: rgb(62, 91, 162); font-weight: 500; text-transform: uppercase;">{{ report_date }}</div>
        <img src="{{ logo_path }}" alt="{{ business_type }} Logo" style="height: 60px;">
    </div>
    
    <div class="orange-divider"></div>
    
    <div class="next-steps-container" style="padding: 3% 8% 0 5%;">
        <h2 class="next-steps-title" style="margin-left: 20px">NEXT STEPS:</h2>
        
        <div class="next-steps-content">
            <div class="next-step">
                Please advise your review of the preferred sites (via markup) noting the pros and cons to assist in evaluation of these for further exploration.
            </div>
            
            <div class="next-step">
                Busi{{ business_type[4:]|capitalize }} will then review this evaluation in collaboration with you to determine which sites are to be explored in depth.
            </div>
        </div>
    </div>
    
    <div style="position: absolute; bottom: 0; left: 0; width: 100%; margin: 0; padding: 0;" class="blue-bg">
        <div style="text-align: center; padding: 15px; font-size: 12px">{{ website }}</div>
    </div>
</div>
"""