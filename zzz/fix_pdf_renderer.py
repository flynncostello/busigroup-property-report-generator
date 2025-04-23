#!/usr/bin/env python3
"""
Helper script to patch PDF renderer to use our fixed WeasyPrint.
"""
import os
import sys
import re

def patch_renderer(file_path):
    """Patch the PDF renderer to use our fixed WeasyPrint."""
    if not os.path.exists(file_path):
        print(f"Error: {file_path} does not exist")
        return False
    
    # Create backup
    backup_path = f"{file_path}.bak"
    if not os.path.exists(backup_path):
        with open(file_path, 'r') as src, open(backup_path, 'w') as dst:
            dst.write(src.read())
        print(f"Created backup: {backup_path}")
    
    # Read the file
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Replace the import
    new_content = re.sub(
        r'from weasyprint import HTML, CSS',
        'from fixed_weasyprint import HTML, CSS',
        content
    )
    
    # Write the modified content
    with open(file_path, 'w') as f:
        f.write(new_content)
    
    print(f"Successfully patched {file_path}")
    return True

if __name__ == "__main__":
    renderer_path = "utils/pdf_components/pdf_renderer.py"
    patch_renderer(renderer_path)
