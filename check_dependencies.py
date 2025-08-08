#!/usr/bin/env python3
"""
Script de vérification des dépendances pour EPUB2PDF
"""

import sys
import subprocess
import importlib
from pathlib import Path

def check_python_version():
    """Vérifie la version de Python"""
    print("🐍 Vérification de la version Python...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python {version.major}.{version.minor} détecté")
        print("   Python 3.8 ou supérieur est requis")
        return False
    else:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} détecté")
        return True

def check_required_packages():
    """Vérifie les paquets Python requis"""
    print("\n📦 Vérification des paquets Python requis...")
    
    required_packages = {
        'PySide6': 'Interface utilisateur moderne',
        'Pillow': 'Traitement d\'images',
        'PyPDF2': 'Manipulation PDF',
        'rarfile': 'Extraction d\'archives RAR',
        'requests': 'Requêtes HTTP pour métadonnées'
    }
    
    optional_packages = {
        'wand': 'Traitement d\'images avancé (optionnel)',
        'numba': 'Optimisation des performances (optionnel)',
        'psutil': 'Monitoring système (optionnel)'
    }
    
    all_good = True
    
    # Vérifier les paquets requis
    for package, description in required_packages.items():
        try:
            importlib.import_module(package.lower().replace('-', '_'))
            print(f"✅ {package} - {description}")
        except ImportError:
            print(f"❌ {package} - {description} (MANQUANT)")
            all_good = False
    
    # Vérifier les paquets optionnels
    print("\n🔧 Paquets optionnels :")
    for package, description in optional_packages.items():
        try:
            importlib.import_module(package.lower().replace('-', '_'))
            print(f"✅ {package} - {description}")
        except ImportError:
            print(f"⚠️  {package} - {description} (optionnel)")
    
    return all_good

def check_system_dependencies():
    """Vérifie les dépendances système"""
    print("\n🖥️  Vérification des dépendances système...")
    
    system_deps = {
        'unar': 'Extraction d\'archives',
        'convert': 'ImageMagick (traitement d\'images)'
    }
    
    all_good = True
    
    for dep, description in system_deps.items():
        try:
            result = subprocess.run([dep, '--version'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                print(f"✅ {dep} - {description}")
            else:
                print(f"❌ {dep} - {description} (NON FONCTIONNEL)")
                all_good = False
        except (FileNotFoundError, subprocess.TimeoutExpired):
            print(f"❌ {dep} - {description} (NON TROUVÉ)")
            all_good = False
    
    return all_good

def check_project_structure():
    """Vérifie la structure du projet"""
    print("\n📁 Vérification de la structure du projet...")
    
    required_dirs = [
        'src',
        'src/core',
        'src/gui',
        'src/utils',
        'tests',
        'temp',
        'logs'
    ]
    
    required_files = [
        'main.py',
        'requirements.txt',
        'src/core/file_manager.py',
        'src/gui/modern_interface.py'
    ]
    
    all_good = True
    
    # Vérifier les dossiers
    for dir_path in required_dirs:
        if Path(dir_path).exists():
            print(f"✅ Dossier {dir_path}/")
        else:
            print(f"❌ Dossier {dir_path}/ (MANQUANT)")
            all_good = False
    
    # Vérifier les fichiers
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✅ Fichier {file_path}")
        else:
            print(f"❌ Fichier {file_path} (MANQUANT)")
            all_good = False
    
    return all_good

def main():
    """Fonction principale"""
    print("=" * 60)
    print("🔍 VÉRIFICATION DES DÉPENDANCES EPUB2PDF")
    print("=" * 60)
    
    checks = [
        check_python_version(),
        check_required_packages(),
        check_system_dependencies(),
        check_project_structure()
    ]
    
    print("\n" + "=" * 60)
    if all(checks):
        print("🎉 TOUTES LES VÉRIFICATIONS SONT PASSÉES !")
        print("✅ L'application est prête à être utilisée.")
        return 0
    else:
        print("⚠️  CERTAINES VÉRIFICATIONS ONT ÉCHOUÉ")
        print("❌ Veuillez installer les dépendances manquantes.")
        print("\n💡 Conseils d'installation :")
        print("   pip install -r requirements.txt")
        print("   brew install unar imagemagick  # macOS")
        print("   sudo apt-get install unar imagemagick  # Ubuntu")
        return 1

if __name__ == "__main__":
    sys.exit(main())
