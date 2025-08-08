"""
Utilitaires de nettoyage des fichiers temporaires
"""

import shutil
from pathlib import Path
import logging


def cleanup_temp_files():
    """Nettoie les fichiers temporaires"""
    try:
        # Chemin vers le dossier temp relatif à l'exécutable
        base_dir = Path(__file__).parent.parent.parent
        temp_dir = base_dir / "temp"
        
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
            temp_dir.mkdir(exist_ok=True)
            logging.info(f"✅ Dossier temporaire nettoyé: {temp_dir}")
        else:
            logging.info("✅ Aucun dossier temporaire à nettoyer")
            
    except Exception as e:
        logging.error(f"❌ Erreur lors du nettoyage: {e}")


def get_temp_dir():
    """Retourne le chemin du dossier temporaire"""
    base_dir = Path(__file__).parent.parent.parent
    temp_dir = base_dir / "temp"
    temp_dir.mkdir(exist_ok=True)
    return temp_dir
