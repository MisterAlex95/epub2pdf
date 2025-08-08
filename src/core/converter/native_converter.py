"""
Convertisseur natif principal pour EPUB/CBR/CBZ vers PDF
"""

import os
import shutil
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from .base_converter import BaseConverter
from .extractor import Extractor
from .image_processor import ImageProcessor
from .pdf_merger import PDFMerger


class NativeConverter(BaseConverter):
    """Convertisseur natif principal pour EPUB/CBR/CBZ vers PDF"""
    
    def __init__(self, max_workers: int = 5, logger=None):
        super().__init__(max_workers, logger)
        
        # Initialiser les composants
        self.extractor = Extractor(max_workers, logger)
        self.image_processor = ImageProcessor(max_workers, logger)
        self.pdf_merger = PDFMerger(max_workers, logger)
    
    def convert_cbr_to_pdf(self, cbr_path: str, output_path: str, 
                          options: Dict = None) -> Tuple[bool, str]:
        """Convertit un fichier CBR en PDF"""
        try:
            self.logger.info(f"🚀 Début conversion CBR: {Path(cbr_path).name}")
            
            # Options par défaut
            options = options or {}
            
            # Déterminer le chemin de sortie
            if not output_path:
                output_path = self._get_default_output_path(cbr_path, "pdf")
            
            # Extraire les images du CBR
            image_paths = self.extractor.extract_cbr(cbr_path)
            if not image_paths:
                return False, "Aucune image extraite du CBR"
            
            # Convertir les images en PDF
            success = self.image_processor.convert_images_to_pdf(image_paths, output_path, options)
            
            if success:
                # Nettoyer les fichiers temporaires
                self._cleanup_temp_files(image_paths)
                return True, f"Conversion réussie: {len(image_paths)} images"
            else:
                return False, "Échec de la conversion des images en PDF"
                
        except Exception as e:
            self.logger.error(f"❌ Erreur conversion CBR: {e}")
            return False, f"Erreur: {str(e)}"
    
    def convert_cbz_to_pdf(self, cbz_path: str, output_path: str,
                          options: Dict = None) -> Tuple[bool, str]:
        """Convertit un fichier CBZ en PDF"""
        try:
            self.logger.info(f"🚀 Début conversion CBZ: {Path(cbz_path).name}")
            
            # Options par défaut
            options = options or {}
            
            # Déterminer le chemin de sortie
            if not output_path:
                output_path = self._get_default_output_path(cbz_path, "pdf")
            
            # Extraire les images du CBZ
            image_paths = self.extractor.extract_cbz(cbz_path)
            if not image_paths:
                return False, "Aucune image extraite du CBZ"
            
            # Convertir les images en PDF
            success = self.image_processor.convert_images_to_pdf(image_paths, output_path, options)
            
            if success:
                # Vérifier que le fichier a été créé
                if os.path.exists(output_path):
                    file_size = os.path.getsize(output_path)
                    self.logger.info(f"✅ Fichier PDF créé: {output_path} ({file_size / (1024*1024):.1f} MB)")
                else:
                    self.logger.error(f"❌ Fichier PDF non créé: {output_path}")
                    return False, "Fichier PDF non créé"
                
                # Nettoyer les fichiers temporaires
                self._cleanup_temp_files(image_paths)
                return True, f"Conversion réussie: {len(image_paths)} images"
            else:
                return False, "Échec de la conversion des images en PDF"
                
        except Exception as e:
            self.logger.error(f"❌ Erreur conversion CBZ: {e}")
            return False, f"Erreur: {str(e)}"
    
    def convert_epub_to_pdf(self, epub_path: str, output_path: str,
                           options: Dict = None) -> Tuple[bool, str]:
        """Convertit un fichier EPUB en PDF (placeholder pour l'instant)"""
        try:
            self.logger.info(f"🚀 Début conversion EPUB: {Path(epub_path).name}")
            
            # Pour l'instant, retourner une erreur car EPUB n'est pas implémenté
            return False, "Conversion EPUB non implémentée (utilisez CBZ/CBR)"
            
        except Exception as e:
            self.logger.error(f"❌ Erreur conversion EPUB: {e}")
            return False, f"Erreur: {str(e)}"
    
    def _get_default_output_path(self, input_path: str, extension: str) -> str:
        """Génère le chemin de sortie par défaut"""
        try:
            input_file = Path(input_path)
            output_dir = input_file.parent
            
            # Chercher un répertoire de sortie approprié
            if "mangas" in str(output_dir).lower():
                # Si c'est dans un dossier mangas, garder la structure
                pass
            else:
                # Sinon, essayer de trouver un dossier Documents/Livres/mangas
                docs_dir = Path.home() / "Documents" / "Livres" / "mangas"
                if docs_dir.exists():
                    output_dir = docs_dir
            
            # S'assurer que le répertoire de sortie existe
            output_dir.mkdir(parents=True, exist_ok=True)
            self.logger.debug(f"📁 Répertoire de sortie: {output_dir}")
            
            # Créer le nom de fichier de sortie
            output_name = input_file.stem + f".{extension}"
            output_path = output_dir / output_name
            
            self.logger.debug(f"Chemin de sortie par défaut: {output_path}")
            return str(output_path)
            
        except Exception as e:
            self.logger.warning(f"⚠️ Erreur génération chemin sortie: {e}")
            # Fallback: même répertoire que l'entrée
            input_file = Path(input_path)
            return str(input_file.with_suffix(f".{extension}"))
    
    def _cleanup_temp_files(self, image_paths: List[str]):
        """Nettoie les fichiers temporaires"""
        try:
            # Supprimer les images temporaires
            for img_path in image_paths:
                try:
                    if os.path.exists(img_path):
                        os.remove(img_path)
                except Exception as e:
                    self.logger.debug(f"⚠️ Erreur suppression {img_path}: {e}")
            
            # Supprimer les répertoires temporaires vides
            temp_dirs = set()
            for img_path in image_paths:
                temp_dir = Path(img_path).parent
                if "cbr2pdf_" in temp_dir.name or "cbz2pdf_" in temp_dir.name:
                    temp_dirs.add(temp_dir)
            
            for temp_dir in temp_dirs:
                try:
                    if temp_dir.exists() and not any(temp_dir.iterdir()):
                        temp_dir.rmdir()
                except Exception as e:
                    self.logger.debug(f"⚠️ Erreur suppression répertoire {temp_dir}: {e}")
                    
        except Exception as e:
            self.logger.warning(f"⚠️ Erreur nettoyage fichiers temporaires: {e}")
