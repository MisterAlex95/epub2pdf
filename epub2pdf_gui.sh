#!/bin/bash

# epub2pdf GUI Launcher
# Launches the graphical user interface for epub2pdf

set -euo pipefail

# Check if Python is available
if ! command -v python3 &>/dev/null; then
    echo "❌ Python 3 is required but not installed"
    echo "💡 Install Python 3 with: brew install python3"
    exit 1
fi

# Check if tkinter is available
if ! python3 -c "import tkinter" 2>/dev/null; then
    echo "❌ tkinter is required but not available"
    echo "💡 Install tkinter with your Python installation"
    exit 1
fi

# Check if epub2pdf.sh exists
if [ ! -f "epub2pdf.sh" ]; then
    echo "❌ epub2pdf.sh not found in current directory"
    echo "💡 Make sure you're in the epub2pdf directory"
    exit 1
fi

# Make GUI script executable
chmod +x epub2pdf_gui.py

# Launch the GUI
echo "🚀 Launching epub2pdf GUI..."
python3 epub2pdf_gui.py 