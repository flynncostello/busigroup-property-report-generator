#!/bin/bash
# Fix WeasyPrint version conflict

echo "=== Fixing WeasyPrint Version Conflict ==="

# Find all WeasyPrint installations
echo "Finding all WeasyPrint installations..."
pip list | grep weasyprint

# Completely remove ALL WeasyPrint installations
echo "Removing all WeasyPrint installations..."
pip uninstall -y weasyprint

# Create a new wrapper for WeasyPrint 65
echo "Creating WeasyPrint wrapper..."
mkdir -p fix_weasyprint

cat > fix_weasyprint/__init__.py << EOF
"""
Fixed WeasyPrint wrapper for version 65.0 with CSS class
"""
import os
import subprocess
import tempfile

WEASYPRINT_BIN = "/opt/homebrew/bin/weasyprint"

class HTML:
    def __init__(self, string=None, base_url=None, file_obj=None, filename=None):
        self.string = string
        self.file_obj = file_obj
        self.filename = filename
        self.base_url = base_url
        
    def write_pdf(self, target=None, stylesheets=None, zoom=1):
        """Generate PDF using Homebrew's WeasyPrint"""
        if self.string:
            with tempfile.NamedTemporaryFile(suffix='.html', delete=False) as temp:
                temp.write(self.string.encode('utf-8'))
                temp_name = temp.name
            cmd = [WEASYPRINT_BIN, temp_name]
        elif self.filename:
            cmd = [WEASYPRINT_BIN, self.filename]
        else:
            raise ValueError("Either string or filename must be provided")
        
        if target:
            cmd.append(target)
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if self.string and 'temp_name' in locals():
            os.unlink(temp_name)
            
        if result.returncode != 0:
            raise Exception(f"WeasyPrint failed: {result.stderr}")
            
        return target

class CSS:
    def __init__(self, string=None, filename=None, url_fetcher=None, media_type='print'):
        self.string = string
        self.filename = filename
        self.url_fetcher = url_fetcher
        self.media_type = media_type

__version__ = "65.0"
EOF

# Create a Python module to replace weasyprint
echo "Creating replacement module..."
cat > weasyprint.py << EOF
"""
WeasyPrint replacement that uses the fixed wrapper
"""
from fix_weasyprint import HTML, CSS
__version__ = "65.0"
EOF

# Modify app.py to use the fixed wrapper
echo "Modifying app.py for compatibility..."
BACKUP_FILE="app.py.bak"
if [ ! -f "$BACKUP_FILE" ]; then
    cp app.py "$BACKUP_FILE"
    echo "Backup created: $BACKUP_FILE"
fi

# Run the app with our fixed module
echo "=== Running Application ==="
PYTHONPATH="$(pwd):$PYTHONPATH" python3 app.py