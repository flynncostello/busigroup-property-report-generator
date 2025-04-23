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
