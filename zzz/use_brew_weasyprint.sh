#!/bin/bash
# Switch to using Homebrew's WeasyPrint

# Get Homebrew prefix
BREW_PREFIX=$(brew --prefix)

# Create wrapper directory
mkdir -p homebrew_weasyprint

# Create a Python module that uses Homebrew's WeasyPrint
cat > homebrew_weasyprint/__init__.py << EOF
"""
Wrapper for Homebrew's WeasyPrint (v65.1)
"""
import os
import subprocess
import tempfile

# Path to Homebrew's WeasyPrint executable
WEASYPRINT_BIN = "$BREW_PREFIX/bin/weasyprint"

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

# For API compatibility with WeasyPrint
__version__ = "65.1"  # This is the Homebrew version
EOF

# Create a symlink in your Python's site-packages
SITE_PACKAGES_DIR=$(python3 -c "import site; print(site.getsitepackages()[0])")
echo "Creating symlink in: $SITE_PACKAGES_DIR"

# Ensure we have permission to write there
if [ -w "$SITE_PACKAGES_DIR" ]; then
    ln -sf "$(pwd)/homebrew_weasyprint/__init__.py" "$SITE_PACKAGES_DIR/weasyprint.py"
    echo "Symlink created successfully"
else
    echo "Cannot write to site-packages. Adding to PYTHONPATH instead."
    echo "export PYTHONPATH=\"$(pwd):$PYTHONPATH\""
    export PYTHONPATH="$(pwd):$PYTHONPATH"
fi

echo "Now using Homebrew's WeasyPrint (v65.1)"