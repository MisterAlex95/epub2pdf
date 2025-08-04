#!/usr/bin/env python3
"""
epub2pdf - Unified PDF Converter
Main entry point for the application
"""

import sys
import os
from pathlib import Path

# Ajouter le répertoire src au path Python
sys.path.insert(0, str(Path(__file__).parent / "src"))

from unified_gui import main

if __name__ == "__main__":
    main() 