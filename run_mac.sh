#!/bin/bash

# Property Report Generator for macOS
# This script handles all dependencies and runs the report generator
# Optimized specifically for macOS with proper WeasyPrint configuration

echo "=== Property Report Generator for macOS ==="
echo "Version: 1.0.0"
echo

# Function to echo text in color
print_color() {
    local color=$1
    local text=$2
    
    case $color in
        "green") echo -e "\033[0;32m$text\033[0m" ;;
        "red") echo -e "\033[0;31m$text\033[0m" ;;
        "yellow") echo -e "\033[0;33m$text\033[0m" ;;
        "blue") echo -e "\033[0;34m$text\033[0m" ;;
        *) echo "$text" ;;
    esac
}

# Print section header
print_section() {
    echo
    print_color blue "==== $1 ===="
    echo
}

# Log success message
log_success() {
    print_color green "✓ $1"
}

# Log error message
log_error() {
    print_color red "✗ $1"
}

# Log warning message
log_warning() {
    print_color yellow "! $1"
}

# Log info message
log_info() {
    echo "- $1"
}

print_section "System Check"

# Determine macOS version
macos_version=$(sw_vers -productVersion)
log_info "macOS Version: $macos_version"

# Determine Mac architecture
arch=$(uname -m)
if [[ "$arch" == "arm64" ]]; then
    log_info "Architecture: Apple Silicon (M1/M2)"
    BREW_PREFIX="/opt/homebrew"
else
    log_info "Architecture: Intel"
    BREW_PREFIX="/usr/local"
fi

# Check if Xcode Command Line Tools are installed
if ! command -v xcode-select &> /dev/null; then
    log_warning "Xcode Command Line Tools may not be installed."
    echo "  If you encounter build errors, install them with:"
    echo "  xcode-select --install"
else
    log_success "Xcode Command Line Tools detected"
fi

print_section "Homebrew Setup"

# Check if Homebrew is installed
if ! command -v brew &> /dev/null; then
    log_warning "Homebrew is not installed. It's required for WeasyPrint dependencies."
    echo "Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    
    # Add Homebrew to PATH if it's not already there
    if ! command -v brew &> /dev/null; then
        if [[ -f "$BREW_PREFIX/bin/brew" ]]; then
            eval "$($BREW_PREFIX/bin/brew shellenv)"
        else
            log_error "Homebrew installation appears to have failed or is not in PATH."
            echo "Please install Homebrew manually and try again:"
            echo "/bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
            exit 1
        fi
    fi
    log_success "Homebrew installed successfully"
else
    log_success "Homebrew already installed"
fi

log_info "Brew prefix: $BREW_PREFIX"

print_section "WeasyPrint Dependencies"

# Recommended approach: Use Homebrew's weasyprint package directly
log_info "Checking if WeasyPrint is installed via Homebrew..."
if ! brew list --formula | grep -q weasyprint; then
    log_info "Installing WeasyPrint via Homebrew (recommended approach)..."
    brew install weasyprint
    if [ $? -eq 0 ]; then
        log_success "WeasyPrint installed successfully via Homebrew"
        # Create symlink to use Homebrew's weasyprint executable
        ln -sf "$BREW_PREFIX/bin/weasyprint" "$BREW_PREFIX/bin/weasyprint-system"
    else
        log_warning "Could not install WeasyPrint via Homebrew"
        log_info "Falling back to installing dependencies manually..."
    fi
else
    log_success "WeasyPrint already installed via Homebrew"
    # Create symlink to use Homebrew's weasyprint executable
    ln -sf "$BREW_PREFIX/bin/weasyprint" "$BREW_PREFIX/bin/weasyprint-system"
fi

# Install other dependencies needed for WeasyPrint in Python
log_info "Installing required system libraries..."
packages=("pango" "cairo" "gdk-pixbuf" "gobject-introspection" "libffi" "harfbuzz" "freetype" "fontconfig")
missing_packages=()

for pkg in "${packages[@]}"; do
    if ! brew list --formula | grep -q $pkg; then
        missing_packages+=($pkg)
    fi
done

if [ ${#missing_packages[@]} -gt 0 ]; then
    log_info "Installing missing packages: ${missing_packages[*]}"
    brew install ${missing_packages[@]}
    if [ $? -ne 0 ]; then
        log_error "Failed to install required packages."
        echo "Please install them manually with: brew install ${missing_packages[*]}"
        exit 1
    fi
    log_success "All required packages installed"
else
    log_success "All required packages already installed"
fi

# Create necessary symlinks for library compatibility
log_info "Creating critical symbolic links for WeasyPrint..."

# CRITICAL FIX: Create specific symlinks that are known to fix the libgobject-2.0-0 error
# These symlinks need to be created with sudo, so we'll check if they exist and prompt if needed
required_symlinks=(
    "/usr/local/lib/gobject-2.0:$BREW_PREFIX/opt/glib/lib/libgobject-2.0.0.dylib"
    "/usr/local/lib/pango-1.0:$BREW_PREFIX/opt/pango/lib/libpango-1.0.dylib"
    "/usr/local/lib/harfbuzz:$BREW_PREFIX/opt/harfbuzz/lib/libharfbuzz.dylib"
    "/usr/local/lib/fontconfig-1:$BREW_PREFIX/opt/fontconfig/lib/libfontconfig.1.dylib"
    "/usr/local/lib/pangoft2-1.0:$BREW_PREFIX/opt/pango/lib/libpangoft2-1.0.dylib"
)

missing_links=()
for link_pair in "${required_symlinks[@]}"; do
    link_dest="${link_pair%%:*}"
    link_source="${link_pair#*:}"
    
    # Check if the source exists
    if [[ ! -f "$link_source" ]]; then
        log_warning "Source file doesn't exist: $link_source"
        continue
    fi
    
    # Check if the symlink exists and points to the correct location
    if [[ -L "$link_dest" ]]; then
        current_target=$(readlink "$link_dest")
        if [[ "$current_target" == "$link_source" ]]; then
            log_success "Symlink already exists: $link_dest -> $link_source"
        else
            log_warning "Symlink exists but points to different target: $link_dest -> $current_target"
            missing_links+=("$link_pair")
        fi
    else
        missing_links+=("$link_pair")
    fi
done

if [ ${#missing_links[@]} -gt 0 ]; then
    log_warning "Missing critical symlinks that require sudo privileges"
    echo "Please run the following commands in a terminal with sudo:"
    echo
    for link_pair in "${missing_links[@]}"; do
        link_dest="${link_pair%%:*}"
        link_source="${link_pair#*:}"
        echo "sudo ln -sf $link_source $link_dest"
    done
    echo
    
    # Offer to run the commands with sudo
    read -p "Would you like the script to try running these commands with sudo? (y/n) " run_sudo
    if [[ "$run_sudo" == "y" || "$run_sudo" == "Y" ]]; then
        for link_pair in "${missing_links[@]}"; do
            link_dest="${link_pair%%:*}"
            link_source="${link_pair#*:}"
            log_info "Running: sudo ln -sf $link_source $link_dest"
            sudo ln -sf "$link_source" "$link_dest"
            if [ $? -eq 0 ]; then
                log_success "Created symlink: $link_dest -> $link_source"
            else
                log_error "Failed to create symlink. Please run the command manually."
            fi
        done
    fi
fi

# Create additional local symlinks that don't require sudo
log_info "Creating additional library symlinks..."
for lib in gobject-2.0 gio-2.0 glib-2.0 cairo pango-1.0 pangocairo-1.0 harfbuzz fontconfig; do
    if [[ -f "$BREW_PREFIX/lib/lib$lib.dylib" ]] && [[ ! -f "$BREW_PREFIX/lib/lib$lib-0.dylib" ]]; then
        ln -sf "$BREW_PREFIX/lib/lib$lib.dylib" "$BREW_PREFIX/lib/lib$lib-0.dylib"
        log_info "Created symlink for lib$lib-0.dylib"
    fi
done

print_section "Python Environment"

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    log_error "Python 3 is not installed or not in your PATH."
    echo "Please install Python 3 from https://www.python.org/downloads/"
    exit 1
fi

# Check Python version (3.9+ required for latest WeasyPrint)
python_version=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
python_major=$(echo $python_version | cut -d. -f1)
python_minor=$(echo $python_version | cut -d. -f2)

if [[ $python_major -lt 3 || ($python_major -eq 3 && $python_minor -lt 9) ]]; then
    log_warning "Python $python_version detected, but Python 3.9 or higher is recommended for the latest WeasyPrint."
    log_info "Continuing with Python $python_version, but you may want to upgrade."
else
    log_success "Using Python $python_version"
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    log_info "Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        log_error "Failed to create virtual environment."
        echo "You might need to install the venv module: python3 -m pip install virtualenv"
        exit 1
    fi
    log_success "Virtual environment created"
else
    log_success "Using existing virtual environment"
fi

# Activate virtual environment
log_info "Activating virtual environment..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    log_error "Failed to activate virtual environment."
    exit 1
fi
log_success "Virtual environment activated"

# Set environment variables for proper library linking
log_info "Setting up environment variables for WeasyPrint..."
export LDFLAGS="-L$BREW_PREFIX/lib"
export CPPFLAGS="-I$BREW_PREFIX/include"
export DYLD_LIBRARY_PATH="$BREW_PREFIX/lib:$DYLD_LIBRARY_PATH"
export PKG_CONFIG_PATH="$BREW_PREFIX/lib/pkgconfig:$PKG_CONFIG_PATH"

# Update pip to latest version
log_info "Updating pip to latest version..."
python -m pip install --upgrade pip
log_success "Pip updated"

print_section "Installing Project Dependencies"

# Install/update dependencies
log_info "Installing project dependencies..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    log_error "Failed to install dependencies."
    echo "Check requirements.txt or try running: pip install --no-cache-dir -r requirements.txt"
    exit 1
fi
log_success "Project dependencies installed"

# Mark dependencies as installed
touch venv/.dependencies_installed

# Ensure WeasyPrint is working in our virtual environment
print_section "WeasyPrint Verification"

# First, try to use Homebrew's WeasyPrint
log_info "Testing system-wide WeasyPrint (from Homebrew)..."
if command -v weasyprint-system &> /dev/null; then
    weasyprint_system_version=$(weasyprint-system --version 2>&1)
    log_success "System WeasyPrint version: $weasyprint_system_version"
else
    log_warning "System-wide WeasyPrint not found"
fi

# Reinstall WeasyPrint and all its dependencies in our virtual environment
log_info "Installing WeasyPrint and all its dependencies..."
pip uninstall -y weasyprint cffi pydyf tinycss2 cssselect2 pyphen fonttools tinyhtml5
pip install --no-cache-dir cffi>=0.6 pydyf>=0.10.0 tinycss2>=1.3.0 cssselect2>=0.8.0 Pyphen>=0.9.1 fontTools>=4.0.0 tinyhtml5>=2.0.0b1
pip install --no-cache-dir weasyprint>=54.0

# Verify all WeasyPrint dependencies
log_info "Verifying all WeasyPrint dependencies..."
python3 -c "
import sys
missing = []

# Define required packages and their minimum versions
requirements = {
    'pydyf': '0.10.0',
    'cffi': '0.6',
    'tinycss2': '1.3.0',
    'cssselect2': '0.8.0',
    'pyphen': '0.9.1',
    'PIL': '9.1.0',  # Pillow
    'fontTools': '4.0.0',
    'tinyhtml5': '2.0.0'  # Note: beta version, checking only major and minor
}

# Check each package
for package, min_version in requirements.items():
    try:
        if package == 'PIL':
            import PIL
            imported = PIL
        else:
            imported = __import__(package.lower())
        
        # Get version
        if package == 'PIL':
            version = imported.__version__
            package = 'Pillow'  # For display
        else:
            version = imported.__version__
        
        # Simple version comparison (not handling complex versioning)
        current = [int(x) for x in version.split('.')]
        required = [int(x) for x in min_version.split('.')]
        
        if current >= required:
            print(f'✓ {package}: {version} (>= {min_version})')
        else:
            print(f'✗ {package}: {version} (< {min_version})')
            missing.append(package)
    except ImportError:
        print(f'✗ {package}: Not installed')
        missing.append(package)
    except Exception as e:
        print(f'? {package}: Error checking version: {e}')

if missing:
    print(f'\\nMissing or outdated dependencies: {\", \".join(missing)}')
    sys.exit(1)
else:
    print('\\nAll WeasyPrint dependencies verified!')
"

if [ $? -ne 0 ]; then
    log_error "Some WeasyPrint dependencies are missing or outdated"
    log_info "Installing missing dependencies..."
    pip install --no-cache-dir -r requirements.txt
else
    log_success "All WeasyPrint dependencies verified"
fi

# Verify WeasyPrint installation in virtual environment
log_info "Verifying WeasyPrint installation in virtual environment..."
python_weasyprint_test=$(python3 -c "
try:
    import weasyprint
    print(f'WeasyPrint version: {weasyprint.__version__}')
    
    # Test specifically for the libgobject-2.0-0 error by importing the specific module
    from weasyprint.text.ffi import ffi, pango, gobject
    print('All required libraries loaded successfully!')
    print('SUCCESS')
except Exception as e:
    print(f'ERROR: {str(e)}')
    
    # Check if it's the specific libgobject error
    error_str = str(e)
    if 'libgobject-2.0-0' in error_str:
        print('\\nThis is the libgobject-2.0-0 error. Please check that you created the symlinks with sudo.')
")

if [[ $python_weasyprint_test == *"SUCCESS"* ]]; then
    log_success "WeasyPrint is properly installed in the virtual environment"
else
    log_warning "WeasyPrint verification in virtual environment failed"
    echo "$python_weasyprint_test"
    
    # Create a simple test to check if Homebrew's WeasyPrint works
    log_info "Creating test HTML to check system WeasyPrint..."
    cat > test.html << EOF
<!DOCTYPE html>
<html>
<head>
    <title>WeasyPrint Test</title>
    <style>
        body { font-family: sans-serif; color: #333; }
        h1 { color: #0066cc; }
    </style>
</head>
<body>
    <h1>WeasyPrint Test</h1>
    <p>If you can see this PDF, WeasyPrint is working correctly!</p>
</body>
</html>
EOF

    # If system WeasyPrint works, create a wrapper script to use it
    if command -v weasyprint-system &> /dev/null; then
        log_info "Testing PDF generation with system WeasyPrint..."
        if weasyprint-system test.html test.pdf 2>/dev/null; then
            log_success "System WeasyPrint works! Creating a wrapper to use it."
            # Create a wrapper module to use the system WeasyPrint
            mkdir -p venv/lib/python*/site-packages/weasyprint_wrapper
            cat > venv/lib/python*/site-packages/weasyprint_wrapper/__init__.py << EOF
"""
WeasyPrint wrapper module that uses the system-installed WeasyPrint binary.
"""
import os
import subprocess
import tempfile

class HTML:
    def __init__(self, string=None, base_url=None, file_obj=None, filename=None):
        self.string = string
        self.file_obj = file_obj
        self.filename = filename
        self.base_url = base_url
        
    def write_pdf(self, target=None, stylesheets=None, zoom=1):
        """Generate a PDF using system-installed WeasyPrint."""
        if self.string:
            # If HTML is provided as a string, write it to a temporary file
            with tempfile.NamedTemporaryFile(suffix='.html', delete=False) as temp:
                temp.write(self.string.encode('utf-8'))
                temp_name = temp.name
            
            # Use the temporary file as input
            cmd = ['$BREW_PREFIX/bin/weasyprint', temp_name]
        elif self.filename:
            # If HTML is provided as a filename
            cmd = ['$BREW_PREFIX/bin/weasyprint', self.filename]
        else:
            raise ValueError("Either string or filename must be provided")
        
        # Add output file
        if target:
            cmd.append(target)
        
        # Run the command
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # Clean up temp file if created
        if self.string:
            os.unlink(temp_name)
            
        if result.returncode != 0:
            raise Exception(f"WeasyPrint failed: {result.stderr}")
        
        return target
EOF
            # Create a file to override weasyprint imports
            cat > venv/lib/python*/site-packages/weasyprint.py << EOF
"""
WeasyPrint stub that redirects to system WeasyPrint.
"""
from weasyprint_wrapper import HTML

__version__ = "$(weasyprint-system --version 2>&1)"
EOF
            log_success "Created wrapper to use system WeasyPrint"
        else
            log_error "System WeasyPrint also failed to generate a PDF."
        fi
    fi
    
    if ! [[ $python_weasyprint_test == *"SUCCESS"* ]] && ! command -v weasyprint-system &> /dev/null; then
        log_error "WeasyPrint installation failed. Please try the following:"
        echo
        echo "1. Install WeasyPrint directly with Homebrew:"
        echo "   brew install weasyprint"
        echo
        echo "2. If that doesn't work, try:"
        echo "   brew uninstall pango cairo gdk-pixbuf"
        echo "   brew install pango cairo gdk-pixbuf"
        echo "   pip install --no-cache-dir weasyprint"
        echo
        echo "3. Check the WeasyPrint troubleshooting guide:"
        echo "   https://doc.courtbouillon.org/weasyprint/stable/first_steps.html"
        echo
        exit 1
    fi
fi

print_section "Preparing Application"

# Create necessary directories
log_info "Creating required directories..."
mkdir -p output logs static/images uploads utils/pdf_components
log_success "Directories created"

# Check for data file
default_data_file="Properties_Hunters_Hill_NSW_2110_Crows_Nest_NSW_2065_04_04_2025_18_03.xlsx"
if [ ! -f "$default_data_file" ]; then
    log_warning "Default data file '$default_data_file' not found."
    echo "The script will use a hardcoded path. Check generate_report.py if it fails."
else
    log_success "Found default data file: $default_data_file"
fi

# Final summary
print_section "Summary"
echo "Working Directory: $(pwd)"
echo "Output Directory: $(pwd)/output"
echo "Log Directory: $(pwd)/logs"
echo

print_section "Launching Report Generator"

# Run the report generator in local mode
python3 generate_report.py

# Check if report generation was successful
if [ $? -eq 0 ]; then
    print_section "Success"
    log_success "Report generation complete!"
    echo "Check the output directory for your PDF."
    echo "You can view logs in the logs directory for more details."
    
    # Save the commands for future reference
    log_info "Creating a reference file for the critical symlinks..."
    cat > weasyprint_symlinks.sh << EOF
#!/bin/bash
# Critical symlinks for WeasyPrint on macOS
# These commands fixed the libgobject-2.0-0 error

sudo ln -sf $BREW_PREFIX/opt/glib/lib/libgobject-2.0.0.dylib /usr/local/lib/gobject-2.0
sudo ln -sf $BREW_PREFIX/opt/pango/lib/libpango-1.0.dylib /usr/local/lib/pango-1.0
sudo ln -sf $BREW_PREFIX/opt/harfbuzz/lib/libharfbuzz.dylib /usr/local/lib/harfbuzz
sudo ln -sf $BREW_PREFIX/opt/fontconfig/lib/libfontconfig.1.dylib /usr/local/lib/fontconfig-1
sudo ln -sf $BREW_PREFIX/opt/pango/lib/libpangoft2-1.0.dylib /usr/local/lib/pangoft2-1.0
EOF
    chmod +x weasyprint_symlinks.sh
    log_success "Created weasyprint_symlinks.sh for future reference"
else
    print_section "Error"
    log_error "Report generation failed."
    echo "Check the logs for details."
    
    # If WeasyPrint was the problem, make a direct suggestion
    if grep -q "libgobject-2.0-0" "logs/property_report_$(date +%Y%m%d)_*.log" 2>/dev/null; then
        print_section "WeasyPrint Fix"
        log_warning "Found the libgobject-2.0-0 error in logs"
        echo "Please run the following commands to fix WeasyPrint:"
        echo "sudo ln -sf $BREW_PREFIX/opt/glib/lib/libgobject-2.0.0.dylib /usr/local/lib/gobject-2.0"
        echo "sudo ln -sf $BREW_PREFIX/opt/pango/lib/libpango-1.0.dylib /usr/local/lib/pango-1.0"
        echo "sudo ln -sf $BREW_PREFIX/opt/harfbuzz/lib/libharfbuzz.dylib /usr/local/lib/harfbuzz"
        echo "sudo ln -sf $BREW_PREFIX/opt/fontconfig/lib/libfontconfig.1.dylib /usr/local/lib/fontconfig-1"
        echo "sudo ln -sf $BREW_PREFIX/opt/pango/lib/libpangoft2-1.0.dylib /usr/local/lib/pangoft2-1.0"
        echo ""
        echo "After creating these symlinks, run this script again."
    fi
    
    exit 1
fi