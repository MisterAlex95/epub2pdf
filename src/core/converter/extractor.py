"""
Module d'extraction pour les fichiers CBR/CBZ
"""

import os
import zipfile
import rarfile
import tempfile
import shutil
import subprocess
from pathlib import Path
from typing import List, Optional
from .base_converter import BaseConverter


class Extractor(BaseConverter):
    """Extracteur pour les fichiers CBR/CBZ"""
    
    def extract_cbr(self, cbr_path: str) -> List[str]:
        """Extrait un fichier CBR et retourne la liste des images"""
        try:
            self.logger.info(f"📦 Extraction du fichier CBR...")
            
            # Créer un répertoire temporaire unique
            import uuid
            extract_dir = self.temp_dir / f"cbr2pdf_{uuid.uuid4().hex[:8]}"
            extract_dir.mkdir(exist_ok=True)
            self.logger.debug(f"📁 Répertoire temporaire: {extract_dir}")
            
            # Essayer d'abord avec unrar (plus rapide)
            if self._extract_with_unrar(cbr_path, str(extract_dir)):
                return self._get_image_files(extract_dir)
            
            # Fallback avec rarfile
            return self._extract_cbr_with_dir(cbr_path, str(extract_dir))
            
        except Exception as e:
            self.logger.error(f"❌ Erreur extraction CBR: {e}")
            return []
    
    def extract_cbz(self, cbz_path: str) -> List[str]:
        """Extrait un fichier CBZ et retourne la liste des images"""
        try:
            self.logger.info(f"📦 Extraction du fichier CBZ...")
            
            # Créer un répertoire temporaire unique
            import uuid
            extract_dir = self.temp_dir / f"cbz2pdf_{uuid.uuid4().hex[:8]}"
            extract_dir.mkdir(exist_ok=True)
            self.logger.debug(f"📁 Répertoire temporaire: {extract_dir}")
            
            # Vérifier que le fichier existe
            if not os.path.exists(cbz_path):
                self.logger.error(f"❌ Fichier CBZ inexistant: {cbz_path}")
                return []
            
            file_size = os.path.getsize(cbz_path)
            self.logger.debug(f"📏 Taille du fichier CBZ: {file_size / (1024*1024):.1f} MB")
            
            # Extraction ZIP
            with zipfile.ZipFile(cbz_path, 'r') as zip_ref:
                # Lister tous les fichiers
                all_files = zip_ref.namelist()
                self.logger.debug(f"📋 {len(all_files)} fichiers dans le ZIP")
                
                # Filtrer les images
                image_files = [f for f in all_files if self._is_image_file(f)]
                self.logger.info(f"📄 {len(image_files)} images trouvées dans le ZIP")
                
                # Extraire les images
                extracted_count = 0
                for img_file in image_files:
                    try:
                        zip_ref.extract(img_file, extract_dir)
                        self.logger.debug(f"✅ Extrait: {img_file}")
                        extracted_count += 1
                    except Exception as e:
                        self.logger.warning(f"⚠️ Erreur extraction {img_file}: {e}")
                
                self.logger.debug(f"📊 {extracted_count}/{len(image_files)} images extraites avec succès")
                
                # Obtenir les chemins complets des images extraites
                image_paths = []
                for img_file in image_files:
                    full_path = extract_dir / img_file
                    if full_path.exists():
                        image_paths.append(str(full_path))
                        self.logger.debug(f"✅ Image disponible: {full_path.name} ({full_path.stat().st_size} bytes)")
                    else:
                        self.logger.warning(f"⚠️ Image manquante après extraction: {img_file}")
                
                # Dédupliquer et trier
                unique_paths = list(set(image_paths))
                if len(unique_paths) != len(image_paths):
                    self.logger.warning(f"⚠️ {len(image_paths) - len(unique_paths)} images dupliquées supprimées")
                
                self.logger.info(f"📦 Extraction ZIP terminée: {len(unique_paths)} images uniques")
                return unique_paths
                
        except Exception as e:
            self.logger.error(f"❌ Erreur extraction CBZ: {e}")
            return []
    
    def _extract_with_unrar(self, cbr_path: str, extract_dir: str) -> bool:
        """Extrait avec unrar (plus rapide)"""
        try:
            result = subprocess.run(
                ['unar', '-o', extract_dir, cbr_path],
                capture_output=True,
                text=True,
                timeout=60  # Augmenter le timeout
            )
            if result.returncode == 0:
                # Vérifier que des fichiers ont été extraits
                extracted_files = list(Path(extract_dir).rglob('*'))
                if len(extracted_files) > 0:
                    return True
                else:
                    self.logger.warning("⚠️ unrar a réussi mais aucun fichier extrait")
                    return False
            else:
                self.logger.debug(f"⚠️ unrar échoué (code {result.returncode}): {result.stderr}")
                return False
        except subprocess.TimeoutExpired:
            self.logger.warning("⚠️ unrar timeout - essai avec rarfile")
            return False
        except Exception as e:
            self.logger.debug(f"⚠️ unrar échoué: {e}")
            return False
    
    def _extract_cbr_with_dir(self, cbr_path: str, extract_dir: str) -> List[str]:
        """Extrait avec rarfile (fallback)"""
        try:
            with rarfile.RarFile(cbr_path, 'r') as rar_ref:
                # Lister tous les fichiers
                all_files = rar_ref.namelist()
                self.logger.debug(f"📋 {len(all_files)} fichiers dans le RAR")
                
                # Filtrer les images
                image_files = [f for f in all_files if self._is_image_file(f)]
                self.logger.info(f"📄 {len(image_files)} images trouvées dans le RAR")
                
                # Extraire les images
                for img_file in image_files:
                    try:
                        rar_ref.extract(img_file, extract_dir)
                        self.logger.debug(f"✅ Extrait: {img_file}")
                    except Exception as e:
                        self.logger.warning(f"⚠️ Erreur extraction {img_file}: {e}")
                
                # Obtenir les chemins complets des images extraites
                image_paths = []
                for img_file in image_files:
                    full_path = Path(extract_dir) / img_file
                    if full_path.exists():
                        image_paths.append(str(full_path))
                
                # Dédupliquer et trier
                unique_paths = list(set(image_paths))
                if len(unique_paths) != len(image_paths):
                    self.logger.warning(f"⚠️ {len(image_paths) - len(unique_paths)} images dupliquées supprimées")
                
                self.logger.info(f"📦 Extraction RAR terminée: {len(unique_paths)} images uniques")
                return unique_paths
                
        except Exception as e:
            self.logger.error(f"❌ Erreur extraction RAR: {e}")
            return []
    
    def _get_image_files(self, extract_dir: Path) -> List[str]:
        """Récupère la liste des images dans un répertoire"""
        try:
            image_files = []
            for file_path in extract_dir.rglob('*'):
                if file_path.is_file() and self._is_image_file(file_path.name):
                    image_files.append(str(file_path))
            
            # Dédupliquer et trier
            unique_paths = list(set(image_files))
            if len(unique_paths) != len(image_files):
                self.logger.warning(f"⚠️ {len(image_files) - len(unique_paths)} images dupliquées supprimées")
            
            self.logger.info(f"✅ {len(unique_paths)} images extraites")
            return unique_paths
            
        except Exception as e:
            self.logger.error(f"❌ Erreur récupération images: {e}")
            return []
