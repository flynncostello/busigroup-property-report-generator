#!/usr/bin/env bash
# start.sh - One file to fully setup and run the Property Report Generator

set -e  # Exit immediately on error

ENV_NAME="reportgen"
PYTHON_VERSION="3.12"
APP_PORT=8000  # Standard port for Docker/Azure

echo "=== Property Report Generator - Full Setup and Launch ==="

# 1. Conda Environment Setup
echo
echo ">>> Checking or Creating Conda Environment: $ENV_NAME"

if conda info --envs | grep -q "$ENV_NAME"; then
    echo "✅ Environment '$ENV_NAME' already exists."
else
    echo "🔧 Creating environment '$ENV_NAME' with Python $PYTHON_VERSION..."
    conda create -n "$ENV_NAME" python="$PYTHON_VERSION" -y
    echo "✅ Environment created."
fi

# 2. Activate Environment
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate "$ENV_NAME"

# 3. Install Homebrew system libraries (Mac only)
echo
echo ">>> Installing system libraries (if on MacOS)"
if [[ "$OSTYPE" == "darwin"* ]]; then
    brew install cairo pango gdk-pixbuf libffi || true
fi

# 4. Install Python Packages
echo
echo ">>> Installing Python packages"

python -m pip install --upgrade pip
pip install flask werkzeug jinja2 gunicorn pandas openpyxl numpy openpyxl-image-loader beautifulsoup4 weasyprint

# 5. Create Necessary Directories
echo
echo ">>> Creating required directories"

mkdir -p uploads output logs static/images static/css static/js templates

# 6. Set WeasyPrint Environment Variables (Only Mac needs these)
echo
echo ">>> Setting WeasyPrint environment variables"

export PKG_CONFIG_PATH="/opt/homebrew/lib/pkgconfig:/opt/homebrew/opt/libffi/lib/pkgconfig:/opt/homebrew/opt/cairo/lib/pkgconfig:$PKG_CONFIG_PATH"
export DYLD_LIBRARY_PATH="/opt/homebrew/lib:$DYLD_LIBRARY_PATH"
export LDFLAGS="-L/opt/homebrew/lib"
export CPPFLAGS="-I/opt/homebrew/include"

# 7. Set Flask Environment Variables
export FLASK_APP=app.py
export FLASK_DEBUG=False
export PYTHONPATH="$(pwd):$PYTHONPATH"

# 8. Launch App
echo
echo ">>> Starting the web application"

if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "🧪 Detected macOS, launching Flask dev server..."
    python app.py
else
    echo "🚀 Launching production server with Gunicorn..."
    gunicorn app:app --bind 0.0.0.0:$APP_PORT
    wait $!
fi
