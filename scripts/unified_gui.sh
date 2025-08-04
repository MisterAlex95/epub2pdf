#!/bin/bash

# Unified GUI Launcher
# Launches the unified graphical user interface for epub2pdf & cbr2pdf

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
    echo "💡 Install tkinter with: brew install python-tk"
    exit 1
fi

# Check if scripts exist
if [ ! -f "scripts/epub2pdf.sh" ]; then
    echo "❌ epub2pdf.sh not found in scripts directory"
    echo "💡 Make sure you're in the project directory"
    exit 1
fi

if [ ! -f "scripts/cbr2pdf.sh" ]; then
    echo "❌ cbr2pdf.sh not found in scripts directory"
    echo "💡 Make sure you're in the project directory"
    exit 1
fi

if [ ! -f "scripts/cbz2pdf.sh" ]; then
    echo "❌ cbz2pdf.sh not found in scripts directory"
    echo "💡 Make sure you're in the project directory"
    exit 1
fi

# Launch the GUI
echo "🚀 Launching unified GUI..."
python3 main.py 