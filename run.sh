#!/bin/bash
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate reportgen

# WeasyPrint environment variables
export PKG_CONFIG_PATH="/opt/homebrew/lib/pkgconfig:/opt/homebrew/opt/libffi/lib/pkgconfig:/opt/homebrew/opt/cairo/lib/pkgconfig:$PKG_CONFIG_PATH"
export DYLD_LIBRARY_PATH="/opt/homebrew/lib:$DYLD_LIBRARY_PATH"
export LDFLAGS="-L/opt/homebrew/lib"
export CPPFLAGS="-I/opt/homebrew/include"

export FLASK_APP=app.py
export FLASK_DEBUG=True
export PYTHONPATH="$(pwd):$PYTHONPATH"

python app.py