#!/usr/bin/env bash
# mac_run.sh - Run Property Report Generator on Mac M2

echo "=== Property Report Generator - Starting Application ==="
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
log_info() { echo "- $1"; }
log_success() { print_color green "✓ $1"; }
log_error() { print_color red "✗ $1"; }
log_warning() { print_color yellow "! $1"; }

# Check required directories exist
log_info "Checking required directories..."
mkdir -p uploads output logs static/images
log_success "Required directories verified"

# Check Python version
PYTHON_CMD="python3"  # Default Python command
python_version=$($PYTHON_CMD --version 2>&1)
log_info "Using $python_version"

# Check WeasyPrint - first try with the system Python
log_info "Verifying WeasyPrint installation..."
if $PYTHON_CMD -c "
try:
    import weasyprint
    print(f'WeasyPrint version: {weasyprint.__version__}')
    from weasyprint.text.ffi import ffi, pango, gobject
    print('WeasyPrint dependencies verified successfully')
    exit(0)
except ImportError as e:
    print(f'Import error: {e}')
    exit(1)
except Exception as e:
    print(f'Error: {e}')
    exit(2)
" 2>/dev/null; then
    log_success "WeasyPrint verified successfully"
else
    # Try with the Homebrew Python if system Python fails
    log_warning "WeasyPrint verification failed with system Python."
    
    # Try to find where WeasyPrint is installed
    if command -v brew &> /dev/null; then
        log_info "Checking Homebrew installation..."
        BREW_WEASYPRINT=$(brew --prefix weasyprint 2>/dev/null)
        
        if [ -n "$BREW_WEASYPRINT" ]; then
            log_info "Found Homebrew WeasyPrint at: $BREW_WEASYPRINT"
            # Set environment variables for Homebrew
            BREW_PREFIX=$(brew --prefix)
            export PYTHONPATH="$BREW_PREFIX/lib/python3.11/site-packages:$PYTHONPATH"
            export DYLD_LIBRARY_PATH="$BREW_PREFIX/lib:$DYLD_LIBRARY_PATH"
            export LD_LIBRARY_PATH="$BREW_PREFIX/lib:$LD_LIBRARY_PATH"
            export PATH="$BREW_PREFIX/bin:$PATH"
            
            log_info "Updated environment to use Homebrew Python paths"
        fi
    fi
    
    # Final check to see if we can now find WeasyPrint
    if $PYTHON_CMD -c "import weasyprint; print(f'WeasyPrint version: {weasyprint.__version__}')" 2>/dev/null; then
        log_success "WeasyPrint found after environment update"
    else
        log_warning "PDF generation might not work correctly due to WeasyPrint configuration issues"
        log_info "Continuing anyway..."
    fi
fi

# Set Flask environment variables
export FLASK_APP=app.py
export FLASK_DEBUG=True
export FLASK_RUN_PORT=5001

log_info "Starting Property Report Generator on port 5001..."
print_color blue "==== Application Starting ===="
echo
echo "Open your browser and navigate to: http://localhost:5001"
echo "Press Ctrl+C to stop the application"
echo

# Run the Flask application using the correct Python interpreter
$PYTHON_CMD app.py