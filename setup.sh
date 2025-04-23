#!/usr/bin/env bash
# setup.sh - Full setup for the Property Report Generator (WeasyPrint only)

set -e  # Exit on error

ENV_NAME="reportgen"
PYTHON_VERSION="3.12"
APP_PORT=5001

echo "=== Property Report Generator - Full Setup ==="

### 1. Conda Environment Setup ###
echo
echo ">>> Checking or Creating Conda Environment: $ENV_NAME"

if conda info --envs | grep -q "$ENV_NAME"; then
    echo "✅ Environment '$ENV_NAME' already exists."
else
    echo "🔧 Creating environment '$ENV_NAME' with Python $PYTHON_VERSION..."
    conda create -n "$ENV_NAME" python="$PYTHON_VERSION" -y
    echo "✅ Environment created."
fi

# Activate it
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate "$ENV_NAME"

### 2. Install Homebrew system libraries ###
echo
echo ">>> Installing required native libraries via Homebrew..."

# Only try brew if we're on macOS (not in Docker)
if [[ "$OSTYPE" == "darwin"* ]]; then
    brew install cairo pango gdk-pixbuf libffi || true
fi

### 3. Export environment variables for WeasyPrint ###
echo
echo ">>> Configuring environment for WeasyPrint + Cairo"
export PKG_CONFIG_PATH="/opt/homebrew/lib/pkgconfig:/opt/homebrew/opt/libffi/lib/pkgconfig:/opt/homebrew/opt/cairo/lib/pkgconfig:$PKG_CONFIG_PATH"
export DYLD_LIBRARY_PATH="/opt/homebrew/lib:$DYLD_LIBRARY_PATH"
export LDFLAGS="-L/opt/homebrew/lib"
export CPPFLAGS="-I/opt/homebrew/include"

### 4. Install Python dependencies ###
echo
echo ">>> Installing Python packages..."

python -m pip install --upgrade pip
python -m pip install flask werkzeug jinja2 gunicorn
python -m pip install pandas openpyxl numpy openpyxl-image-loader
python -m pip install beautifulsoup4 weasyprint


echo "✅ All packages installed"

### 5. Create required folders ###
echo
echo ">>> Creating app directories..."

mkdir -p uploads output logs static/images static/css static/js templates

echo "✅ Directories created."

### 6. Create run.sh ###
echo
echo ">>> Creating launcher script (run.sh)..."

cat > run.sh << EOF
#!/bin/bash
source "\$(conda info --base)/etc/profile.d/conda.sh"
conda activate $ENV_NAME

# WeasyPrint environment variables
export PKG_CONFIG_PATH="/opt/homebrew/lib/pkgconfig:/opt/homebrew/opt/libffi/lib/pkgconfig:/opt/homebrew/opt/cairo/lib/pkgconfig:\$PKG_CONFIG_PATH"
export DYLD_LIBRARY_PATH="/opt/homebrew/lib:\$DYLD_LIBRARY_PATH"
export LDFLAGS="-L/opt/homebrew/lib"
export CPPFLAGS="-I/opt/homebrew/include"

export FLASK_APP=app.py
export FLASK_DEBUG=True
export PYTHONPATH="\$(pwd):\$PYTHONPATH"

python app.py
EOF

chmod +x run.sh
echo "✅ run.sh created"