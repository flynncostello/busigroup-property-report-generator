#!/usr/bin/env bash
# build.sh - Prepare environment for WeasyPrint on Render

echo "=== Installing WeasyPrint dependencies ==="

# Update package lists
apt-get update -y

# Install system dependencies for WeasyPrint - with detailed package specification
apt-get install -y --no-install-recommends \
    build-essential \
    python3-dev \
    python3-setuptools \
    python3-wheel \
    python3-cffi \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    shared-mime-info \
    libxml2-dev \
    libxslt1-dev \
    libglib2.0-0 \
    libpangoft2-1.0-0 \
    libharfbuzz0b \
    libfontconfig1

echo "=== System dependencies installed ==="

# Verify critical libraries are available
echo "=== Verifying critical libraries ==="
ldconfig -p | grep -E 'libgobject|libpango|libharfbuzz|libfontconfig'

# Create required directories
mkdir -p output logs uploads static/images

# Create a simple test script to verify WeasyPrint works
cat > weasyprint_test.py << EOF
import sys
try:
    import weasyprint
    print(f"WeasyPrint version: {weasyprint.__version__}")
    
    # Test specifically for the libgobject-2.0-0 error
    from weasyprint.text.ffi import ffi, pango, gobject
    print("SUCCESS: All required libraries loaded successfully!")
except Exception as e:
    print(f"ERROR: {str(e)}")
    sys.exit(1)
EOF

# Run the test during build
echo "=== Testing WeasyPrint library imports ==="
python3 weasyprint_test.py

echo "=== Setup completed ==="