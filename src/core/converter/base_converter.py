"""
Classe de base pour les convertisseurs
"""

import os
import logging
from pathlib import Path
from typing import Dict, Optional


class BaseConverter:
    """Classe de base pour tous les convertisseurs"""
    
    def __init__(self, max_workers: int = 5, logger=None):
        self.max_workers = max_workers
        self.logger = logger or logging.getLogger('epub2pdf')
        
        # Créer le répertoire temporaire relatif à l'exécutable
        self.base_dir = Path(__file__).parent.parent.parent.parent
        self.temp_dir = self.base_dir / "temp"
        self.temp_dir.mkdir(exist_ok=True)
        
        # Vérifier les dépendances
        self._check_dependencies()
    
    def _check_dependencies(self):
        """Vérifie les dépendances disponibles"""
        # Pillow
        try:
            from PIL import Image
            self.pillow_available = True
            self.logger.debug("✅ Pillow disponible")
        except ImportError:
            self.pillow_available = False
            self.logger.warning("⚠️ Pillow non installé. Installation recommandée: pip install Pillow")
        
        # Wand
        try:
            from wand.image import Image as WandImage
            self.wand_available = True
            self.logger.debug("✅ Wand disponible")
        except ImportError as e:
            self.wand_available = False
            self.logger.warning(f"⚠️ Wand non installé ou erreur d'import: {e}")
            self.logger.warning("Installation recommandée: pip install Wand")
        except Exception as e:
            self.wand_available = False
            self.logger.warning(f"⚠️ Erreur lors de l'import de Wand: {e}")
        
        # PyPDF2
        try:
            from PyPDF2 import PdfWriter, PdfReader
            self.pypdf2_available = True
            self.logger.debug("✅ PyPDF2 disponible")
        except ImportError:
            self.pypdf2_available = False
            self.logger.warning("⚠️ PyPDF2 non installé. Installation recommandée: pip install PyPDF2")
        
        # Vérifier unrar
        try:
            import subprocess
            result = subprocess.run(['unar', '--version'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                self.logger.info("✅ unar disponible pour l'extraction")
            else:
                self.logger.warning("⚠️ unar non disponible - extraction limitée")
        except (FileNotFoundError, subprocess.TimeoutExpired):
            self.logger.warning("⚠️ unar non installé ou timeout - extraction limitée")
        
        # Configurer le multiprocessing pour éviter les problèmes
        import multiprocessing
        multiprocessing.set_start_method('spawn', force=True)
    
    def _natural_sort_key(self, path: str) -> list:
        """Clé de tri naturel pour les noms de fichiers"""
        import re
        return [int(text) if text.isdigit() else text.lower()
                for text in re.split('([0-9]+)', str(path))]
    
    def _is_image_file(self, filename: str) -> bool:
        """Vérifie si un fichier est une image"""
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
        return Path(filename).suffix.lower() in image_extensions
