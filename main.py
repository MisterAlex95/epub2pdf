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
        from src.gui.modern_interface import ModernInterface
        
        # Créer l'application
        app = QApplication(sys.argv)
        app.setApplicationName("epub2pdf")
        app.setApplicationVersion("2.0.0")
        
        # Créer et afficher la fenêtre principale
        window = ModernInterface()
        window.show()
        
        # Démarrer l'application
        sys.exit(app.exec())
        
    except Exception as e:
        print(f"Erreur lors du démarrage de l'application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 