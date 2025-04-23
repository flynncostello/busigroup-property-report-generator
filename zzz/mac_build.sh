#!/usr/bin/env bash
# mac_build.sh - Setup environment for Property Report Generator on Mac M2

echo "=== Property Report Generator - Mac M2 Setup ==="
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

# Log functions
log_success() { print_color green "✓ $1"; }
log_error() { print_color red "✗ $1"; }
log_warning() { print_color yellow "! $1"; }
log_info() { echo "- $1"; }

# Print section header
print_section() {
    echo
    print_color blue "==== $1 ===="
    echo
}

print_section "System Check"

# Check if brew exists (for M2 Mac)
if ! command -v brew &> /dev/null; then
    log_warning "Homebrew not found. You may need it for WeasyPrint dependencies."
    log_info "You can install it with: /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
else
    log_success "Homebrew found"
    
    # Determine brew prefix
    BREW_PREFIX=$(brew --prefix)
    log_info "Brew prefix: $BREW_PREFIX"
fi

print_section "Creating Required Directories"

# Create necessary directories
mkdir -p uploads
mkdir -p output
mkdir -p logs
mkdir -p static/images
mkdir -p static/css
mkdir -p static/js

log_success "Required directories created"

print_section "Checking WeasyPrint"

# Check if WeasyPrint is installed
if python3 -c "import weasyprint" 2>/dev/null; then
    # WeasyPrint is installed, check version
    weasyprint_version=$(python3 -c "import weasyprint; print(weasyprint.__version__)")
    log_success "WeasyPrint is already installed (version: $weasyprint_version)"
    
    # Check if dependencies load correctly
    if python3 -c "import weasyprint; from weasyprint.text.ffi import ffi, pango, gobject" 2>/dev/null; then
        log_success "WeasyPrint dependencies verified successfully"
    else
        log_warning "WeasyPrint is installed but dependencies may be missing"
        
        if command -v brew &> /dev/null; then
            log_info "Installing required system libraries with Homebrew..."
            brew install pango cairo gdk-pixbuf libffi
            
            # Create critical symlinks if brew exists
            if [ -n "$BREW_PREFIX" ]; then
                log_info "You may need to create these symlinks (requires sudo):"
                echo "sudo ln -sf $BREW_PREFIX/opt/glib/lib/libgobject-2.0.0.dylib /usr/local/lib/gobject-2.0"
                echo "sudo ln -sf $BREW_PREFIX/opt/pango/lib/libpango-1.0.dylib /usr/local/lib/pango-1.0"
                echo "sudo ln -sf $BREW_PREFIX/opt/harfbuzz/lib/libharfbuzz.dylib /usr/local/lib/harfbuzz"
                echo "sudo ln -sf $BREW_PREFIX/opt/fontconfig/lib/libfontconfig.1.dylib /usr/local/lib/fontconfig-1"
                echo "sudo ln -sf $BREW_PREFIX/opt/pango/lib/libpangoft2-1.0.dylib /usr/local/lib/pangoft2-1.0"
                echo
                log_info "Would you like to run these commands now? (y/n)"
                read -r response
                if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
                    sudo ln -sf "$BREW_PREFIX/opt/glib/lib/libgobject-2.0.0.dylib" /usr/local/lib/gobject-2.0
                    sudo ln -sf "$BREW_PREFIX/opt/pango/lib/libpango-1.0.dylib" /usr/local/lib/pango-1.0
                    sudo ln -sf "$BREW_PREFIX/opt/harfbuzz/lib/libharfbuzz.dylib" /usr/local/lib/harfbuzz
                    sudo ln -sf "$BREW_PREFIX/opt/fontconfig/lib/libfontconfig.1.dylib" /usr/local/lib/fontconfig-1
                    sudo ln -sf "$BREW_PREFIX/opt/pango/lib/libpangoft2-1.0.dylib" /usr/local/lib/pangoft2-1.0
                    log_success "Symlinks created"
                else
                    log_warning "Skipping symlink creation. If PDF generation fails, you may need to create these manually."
                fi
            fi
        fi
    fi
else
    log_warning "WeasyPrint not found. Installing dependencies..."
    
    if command -v brew &> /dev/null; then
        log_info "Installing WeasyPrint with Homebrew..."
        brew install pango cairo gdk-pixbuf libffi weasyprint
        log_success "WeasyPrint dependencies installed with Homebrew"
    else
        log_warning "Homebrew not found. Please install it to manage WeasyPrint dependencies."
    fi
    
    log_info "Installing WeasyPrint with pip..."
    pip3 install weasyprint
fi

print_section "Installing Python Requirements"

# Install Python requirements
log_info "Installing Python requirements..."
python3 -m pip install -r requirements.txt
if [ $? -eq 0 ]; then
    log_success "Python requirements installed"
else
    log_warning "Some Python requirements could not be installed. Trying without cache..."
    python3 -m pip install --no-cache-dir -r requirements.txt
    if [ $? -eq 0 ]; then
        log_success "Python requirements installed (without cache)"
    else
        log_error "Failed to install Python requirements. You may need to install them manually."
    fi
fi

print_section "Setup Complete"

log_success "Property Report Generator setup complete"
log_info "To run the application, use: ./mac_run.sh"
echo