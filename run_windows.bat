@echo off
setlocal enabledelayedexpansion

echo ===========================================
echo Property Report Generator for Windows
echo Version 1.0.0
echo ===========================================
echo.

REM Set colors for output
set "GREEN=[92m"
set "RED=[91m"
set "YELLOW=[93m"
set "BLUE=[94m"
set "RESET=[0m"

REM Check if running with admin privileges
net session >nul 2>&1
if %errorLevel% == 0 (
    echo %GREEN%✓ Running with administrator privileges%RESET%
) else (
    echo %YELLOW%! This script may require administrator privileges%RESET%
    echo   Some operations might fail without admin rights
    echo   Consider right-clicking the batch file and selecting "Run as administrator"
    echo.
    timeout /t 3 >nul
)

echo %BLUE%==== Checking Environment ====%RESET%
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorLevel% == 0 (
    for /f "tokens=2" %%V in ('python --version 2^>^&1') do set PYTHON_VERSION=%%V
    echo %GREEN%✓ Python !PYTHON_VERSION! is installed%RESET%
) else (
    echo %RED%✗ Python is not installed or not in PATH%RESET%
    echo   Please download and install Python from https://www.python.org/downloads/
    echo   Make sure to check "Add Python to PATH" during installation
    echo.
    echo %YELLOW%Press any key to exit...%RESET%
    pause >nul
    exit /b 1
)

REM Check if virtual environment exists
if exist venv\ (
    echo %GREEN%✓ Virtual environment exists%RESET%
    set VENV_CREATED=1
) else (
    echo %YELLOW%! Creating virtual environment...%RESET%
    python -m venv venv
    if !errorLevel! == 0 (
        echo %GREEN%✓ Virtual environment created%RESET%
        set VENV_CREATED=1
    ) else (
        echo %RED%✗ Failed to create virtual environment%RESET%
        echo   You might need to install the venv module: python -m pip install virtualenv
        echo.
        echo %YELLOW%Press any key to exit...%RESET%
        pause >nul
        exit /b 1
    )
)

REM Check if setup has been done before
if exist venv\.setup_complete (
    set SETUP_COMPLETE=1
    echo %GREEN%✓ Setup has been completed previously%RESET%
) else (
    set SETUP_COMPLETE=0
    echo %YELLOW%! First-time setup required%RESET%
)

REM Activate virtual environment
echo %YELLOW%! Activating virtual environment...%RESET%
call venv\Scripts\activate
if %errorLevel% neq 0 (
    echo %RED%✗ Failed to activate virtual environment%RESET%
    echo.
    echo %YELLOW%Press any key to exit...%RESET%
    pause >nul
    exit /b 1
)
echo %GREEN%✓ Virtual environment activated%RESET%

REM If first run, install dependencies
if %SETUP_COMPLETE% == 0 (
    echo.
    echo %BLUE%==== Installing Dependencies ====%RESET%
    echo.
    
    REM Upgrade pip
    echo %YELLOW%! Upgrading pip...%RESET%
    python -m pip install --upgrade pip
    if %errorLevel% neq 0 (
        echo %YELLOW%! Failed to upgrade pip, continuing anyway...%RESET%
    ) else (
        echo %GREEN%✓ Pip upgraded%RESET%
    )
    
    REM Install packages
    echo %YELLOW%! Installing required packages...%RESET%
    
    REM First install core dependencies
    pip install wheel setuptools
    
    REM Install WeasyPrint dependencies
    echo %YELLOW%! Installing WeasyPrint and dependencies...%RESET%
    pip install pydyf>=0.10.0 cffi>=0.6 tinyhtml5>=2.0.0b1 tinycss2>=1.3.0 cssselect2>=0.8.0 Pyphen>=0.9.1 Pillow>=9.1.0 fontTools>=4.0.0
    
    REM Install WeasyPrint
    pip install weasyprint>=54.0
    
    REM Install web framework and other dependencies
    pip install Flask>=2.0.0 Werkzeug>=2.0.0 jinja2>=3.0.0 pandas>=1.3.0 openpyxl>=3.0.0 numpy>=1.20.0 openpyxl-image-loader
    
    REM Verify WeasyPrint installation
    python -c "import weasyprint; print(f'WeasyPrint version: {weasyprint.__version__}')"
    if %errorLevel% neq 0 (
        echo %RED%✗ WeasyPrint installation verification failed%RESET%
        echo   This may affect PDF generation functionality
        echo   Please check GTK+ dependencies for Windows: https://doc.courtbouillon.org/weasyprint/stable/first_steps.html#windows
    ) else (
        echo %GREEN%✓ WeasyPrint installed successfully%RESET%
    )
    
    REM Create required directories
    echo %YELLOW%! Creating required directories...%RESET%
    if not exist output mkdir output
    if not exist logs mkdir logs
    if not exist downloads mkdir downloads
    if not exist merged_properties mkdir merged_properties
    
    REM Mark setup as complete
    echo 1 > venv\.setup_complete
    echo %GREEN%✓ Setup completed successfully%RESET%
)

echo.
echo %BLUE%==== Launching Application ====%RESET%
echo.
echo %YELLOW%! Starting the application...%RESET%
echo.
echo %GREEN%✓ Application starting at http://localhost:5000%RESET%
echo.
echo %YELLOW%! Press Ctrl+C to stop the application%RESET%
echo.

REM Run the application
python app.py

REM Deactivate virtual environment (will only run if the application exits normally)
call venv\Scripts\deactivate.bat

echo.
echo %BLUE%==== Application Stopped ====%RESET%
echo.
echo %YELLOW%Press any key to exit...%RESET%
pause >nul