#!/usr/bin/env python3
"""
Point d'entrée principal de l'application de conversion EPUB/CBR/CBZ vers PDF
Version moderne avec PySide6
"""

import sys
import os
from pathlib import Path

# Ajouter le répertoire src au path pour les imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Vérifier PySide6 avant d'importer l'interface
try:
    from PySide6.QtWidgets import QApplication
except ImportError:
    print("Erreur d'import: No module named 'PySide6'")
    print("Veuillez installer PySide6: pip install PySide6")
    sys.exit(1)

def main():
    """Fonction principale de l'application"""
    try:
        # Importer et utiliser la nouvelle interface moderne
        from src.gui.modern_interface import main as modern_main
        
        # Lancer l'interface moderne
        modern_main()
        
    except Exception as e:
        print(f"Erreur lors du démarrage de l'application: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 