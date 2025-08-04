#!/usr/bin/env python3
"""
Script de lancement rapide pour epub2pdf
"""

import subprocess
import sys
import os

def main():
    """Lance l'interface graphique"""
    try:
        # Vérifier que les scripts existent
        scripts_dir = "scripts"
        required_scripts = [
            os.path.join(scripts_dir, "epub2pdf.sh"),
            os.path.join(scripts_dir, "cbr2pdf.sh"),
            os.path.join(scripts_dir, "cbz2pdf.sh")
        ]
        
        for script in required_scripts:
            if not os.path.exists(script):
                print(f"❌ Script manquant: {script}")
                return 1
        
        # Lancer l'interface
        print("🚀 Lancement de l'interface epub2pdf...")
        subprocess.run([sys.executable, "main.py"])
        
    except Exception as e:
        print(f"❌ Erreur lors du lancement: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 