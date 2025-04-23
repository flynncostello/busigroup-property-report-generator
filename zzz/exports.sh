#!/bin/bash
# Environment variables for WeasyPrint
export PYTHONPATH="/opt/homebrew/lib/python3.11/site-packages:$PYTHONPATH"
export DYLD_LIBRARY_PATH="/Users/flynncostello/.local/lib:/opt/homebrew/lib:$DYLD_LIBRARY_PATH"
export LD_LIBRARY_PATH="/Users/flynncostello/.local/lib:/opt/homebrew/lib:$LD_LIBRARY_PATH"
export PATH="/opt/homebrew/bin:$PATH"
export LDFLAGS="-L/opt/homebrew/lib"
export CPPFLAGS="-I/opt/homebrew/include" 
export PKG_CONFIG_PATH="/opt/homebrew/lib/pkgconfig:$PKG_CONFIG_PATH"
