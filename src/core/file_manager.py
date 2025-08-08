"""
Gestionnaire de fichiers optimisé avec traitement parallèle et logs
"""

import os
import logging
import threading
import subprocess
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple

# Import du nouveau convertisseur Python natif
from .converter import NativeConverter


class FileManager:
    """Gestionnaire de fichiers optimisé avec conversion Python natif"""
    
    def __init__(self, scripts_dir=None):
        """Initialise le gestionnaire de fichiers optimisé"""
        self.files = []
        self.is_converting = False
        self.max_workers = 5
        self.mal_client_id = None
        self.interface = None
        
        # Options de fusion
        self.merge_mode = False
        self.merge_filename = None
        self.merge_pdfs = []
        
        # Optimisations de performance
        self._file_cache = {}  # Cache pour les informations de fichiers
        self._max_cache_size = 100  # Taille maximale du cache
        self._scan_cache = {}  # Cache pour les scans de répertoires
        self._conversion_stats = {
            'total_files': 0,
            'converted_files': 0,
            'failed_files': 0,
            'start_time': None,
            'end_time': None
        }
        
        # Configurer le logging en premier
        self._setup_logging()
        
        # Initialiser le convertisseur natif après le logger
        self.native_converter = NativeConverter(max_workers=self.max_workers, logger=self.logger)
        
        self._check_scripts()
    
    def _check_scripts(self):
        """Vérifie la présence des scripts shell (fallback) - DÉPRÉCIÉ"""
        # Les scripts shell ont été remplacés par le convertisseur Python natif
        self.logger.info("✅ Convertisseur Python natif disponible")
    
    def _setup_logging(self):
        """Configure le système de logging optimisé"""
        try:
            # Créer le dossier de logs
            logs_dir = Path(__file__).parent.parent / "logs"
            logs_dir.mkdir(exist_ok=True)
            
            # Configuration du logger principal
            self.logger = logging.getLogger('epub2pdf')
            self.logger.setLevel(logging.DEBUG)
            
            # Éviter les handlers dupliqués
            if not self.logger.handlers:
                # Handler pour fichier avec rotation
                log_file = logs_dir / f"conversion_{datetime.now().strftime('%Y%m%d')}_{datetime.now().strftime('%H%M%S')}.log"
                file_handler = logging.FileHandler(log_file, encoding='utf-8')
                file_handler.setLevel(logging.DEBUG)
                
                # Handler pour console
                console_handler = logging.StreamHandler()
                console_handler.setLevel(logging.INFO)
                
                # Format optimisé
                formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
                file_handler.setFormatter(formatter)
                console_handler.setFormatter(formatter)
                
                # Ajouter les handlers
                self.logger.addHandler(file_handler)
                self.logger.addHandler(console_handler)
            
            self.logger.info(f"Dossier de logs: {logs_dir}")
            
        except Exception as e:
            self.logger.error(f"Erreur configuration logging: {e}")
    
    def set_mal_client_id(self, client_id: str):
        """Configure l'ID client MyAnimeList"""
        try:
            if hasattr(self, 'metadata_manager'):
                self.metadata_manager.set_mal_client_id(client_id)
        except Exception as e:
            self.logger.error(f"Erreur configuration MAL: {e}")
    
    def set_max_workers(self, workers):
        """Configure le nombre maximum de workers avec optimisations"""
        try:
            self.max_workers = workers
            self.native_converter.max_workers = workers
            self.logger.info(f"Nombre de workers configuré: {workers}")
            
            # Ajuster la taille du cache selon le nombre de workers
            self._max_cache_size = max(50, workers * 10)
            
        except Exception as e:
            self.logger.error(f"Erreur configuration workers: {e}")
    
    def scan_directory(self, directory_path, recursive=False):
        """Scanne un répertoire avec optimisations de performance"""
        try:
            start_time = time.time()
            
            # Vérifier le cache de scan
            cache_key = f"{directory_path}_{recursive}"
            if cache_key in self._scan_cache:
                self.logger.info("📁 Utilisation du cache de scan")
                self.files = self._scan_cache[cache_key]
                return self.files
            
            self.logger.info(f"🔍 Scan du répertoire: {directory_path} (récursif: {recursive})")
            
            if not os.path.exists(directory_path):
                self.logger.error(f"❌ Répertoire inexistant: {directory_path}")
                return []
            
            # Scan optimisé avec ThreadPoolExecutor pour les gros répertoires
            if recursive:
                files = self._scan_recursive_optimized(directory_path)
            else:
                files = self._scan_simple_optimized(directory_path)
            
            # Traitement parallèle des informations de fichiers
            file_infos = self._process_files_parallel(files)
            
            self.files = file_infos
            
            # Mettre en cache
            self._scan_cache[cache_key] = file_infos
            
            elapsed_time = time.time() - start_time
            self.logger.info(f"✅ Scan terminé: {len(file_infos)} fichiers en {elapsed_time:.2f}s")
            
            return file_infos
            
        except Exception as e:
            self.logger.error(f"❌ Erreur scan répertoire: {e}")
            return []
    
    def _scan_recursive_optimized(self, directory_path: str) -> List[str]:
        """Scan récursif optimisé avec parallélisme"""
        files = []
        
        try:
            # Utiliser ThreadPoolExecutor pour scanner les sous-répertoires
            with ThreadPoolExecutor(max_workers=min(4, self.max_workers)) as executor:
                futures = []
                
                for root, dirs, filenames in os.walk(directory_path):
                    # Filtrer les fichiers supportés directement
                    supported_files = [
                        os.path.join(root, filename) 
                        for filename in filenames 
                        if self._is_supported_file(filename)
                    ]
                    
                    if supported_files:
                        futures.append(executor.submit(self._process_directory_files, supported_files))
                
                # Collecter les résultats
                for future in as_completed(futures):
                    try:
                        result = future.result()
                        files.extend(result)
                    except Exception as e:
                        self.logger.warning(f"⚠️ Erreur traitement répertoire: {e}")
            
        except Exception as e:
            self.logger.error(f"❌ Erreur scan récursif: {e}")
        
        return files
    
    def _scan_simple_optimized(self, directory_path: str) -> List[str]:
        """Scan simple optimisé"""
        try:
            with os.scandir(directory_path) as entries:
                files = [
                    entry.path for entry in entries
                    if entry.is_file() and self._is_supported_file(entry.name)
                ]
            return files
        except Exception as e:
            self.logger.error(f"❌ Erreur scan simple: {e}")
            return []
    
    def _process_directory_files(self, file_paths: List[str]) -> List[str]:
        """Traite les fichiers d'un répertoire en parallèle"""
        return file_paths  # Pour l'instant, retourne directement
    
    def _process_files_parallel(self, file_paths: List[str]) -> List[Dict]:
        """Traite les informations de fichiers en parallèle"""
        file_infos = []
        
        # Utiliser ThreadPoolExecutor pour traiter les fichiers en parallèle
        with ThreadPoolExecutor(max_workers=min(8, self.max_workers)) as executor:
            futures = [executor.submit(self._create_file_info, file_path) for file_path in file_paths]
            
            for future in as_completed(futures):
                try:
                    file_info = future.result()
                    if file_info:
                        file_infos.append(file_info)
                except Exception as e:
                    self.logger.warning(f"⚠️ Erreur traitement fichier: {e}")
        
        # Trier les fichiers par ordre naturel
        file_infos.sort(key=lambda x: self._natural_sort_key(x['name']))
        
        return file_infos
    
    def _is_supported_file(self, filename: str) -> bool:
        """Vérifie si un fichier est supporté avec cache"""
        # Vérifier le cache d'abord
        if filename in self._file_cache:
            return self._file_cache[filename].get('supported', False)
        
        # Extensions supportées
        supported_extensions = {'.epub', '.cbr', '.cbz'}
        file_ext = Path(filename).suffix.lower()
        is_supported = file_ext in supported_extensions
        
        # Mettre en cache
        self._add_to_file_cache(filename, {'supported': is_supported})
        
        return is_supported
    
    def _add_to_file_cache(self, filename: str, info: Dict):
        """Ajoute des informations au cache de fichiers"""
        if len(self._file_cache) >= self._max_cache_size:
            # Supprimer l'élément le plus ancien
            oldest_key = next(iter(self._file_cache))
            del self._file_cache[oldest_key]
        
        self._file_cache[filename] = info
    
    def _count_pages(self, file_path: str) -> int:
        """Compte les pages d'un fichier avec optimisations"""
        try:
            # Vérifier le cache d'abord
            if file_path in self._file_cache and 'page_count' in self._file_cache[file_path]:
                return self._file_cache[file_path]['page_count']
            
            file_ext = Path(file_path).suffix.lower()
            
            if file_ext in ['.cbr', '.cbz']:
                # Pour les archives, estimer le nombre de pages
                try:
                    import zipfile
                    import rarfile
                    
                    if file_ext == '.cbz':
                        with zipfile.ZipFile(file_path, 'r') as zip_file:
                            # Compter les fichiers d'images
                            image_files = [
                                f for f in zip_file.namelist() 
                                if self._is_image_file(f.lower())
                            ]
                            page_count = len(image_files)
                    else:  # .cbr
                        with rarfile.RarFile(file_path, 'r') as rar_file:
                            image_files = [
                                f for f in rar_file.namelist() 
                                if self._is_image_file(f.lower())
                            ]
                            page_count = len(image_files)
                    
                    # Mettre en cache
                    self._add_to_file_cache(file_path, {'page_count': page_count})
                    return page_count
                    
                except Exception as e:
                    self.logger.warning(f"⚠️ Erreur comptage pages {file_path}: {e}")
                    return 0
            else:
                # Pour les EPUB, estimation basée sur la taille
                try:
                    file_size = os.path.getsize(file_path)
                    # Estimation: 1 page par 50KB environ
                    estimated_pages = max(1, file_size // (50 * 1024))
                    
                    # Mettre en cache
                    self._add_to_file_cache(file_path, {'page_count': estimated_pages})
                    return estimated_pages
                    
                except Exception as e:
                    self.logger.warning(f"⚠️ Erreur estimation pages {file_path}: {e}")
                    return 0
                    
        except Exception as e:
            self.logger.warning(f"⚠️ Erreur comptage pages {file_path}: {e}")
            return 0
    
    def _is_image_file(self, filename: str) -> bool:
        """Vérifie si un fichier est une image"""
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}
        return Path(filename).suffix.lower() in image_extensions
    
    def _create_file_info(self, file_path):
        """Crée les informations d'un fichier avec optimisations"""
        try:
            # Vérifier le cache d'abord
            if file_path in self._file_cache and 'file_info' in self._file_cache[file_path]:
                return self._file_cache[file_path]['file_info']
            
            if not os.path.exists(file_path):
                return None
            
            # Obtenir les informations de base
            stat = os.stat(file_path)
            filename = Path(file_path).name
            file_ext = Path(file_path).suffix.lower()
            
            # Créer les informations du fichier
            file_info = {
                'path': file_path,
                'name': filename,
                'size': stat.st_size,
                'size_mb': round(stat.st_size / (1024 * 1024), 2),
                'modified': datetime.fromtimestamp(stat.st_mtime),
                'extension': file_ext,
                'selected': False,
                'converted': False,
                'error': None,
                'pages': self._count_pages(file_path),
                'status': 'pending'
            }
            
            # Extraire les métadonnées si possible
            try:
                series, volume, chapter = self._extract_metadata(filename)
                file_info.update({
                    'series': series,
                    'volume': volume,
                    'chapter': chapter
                })
            except Exception as e:
                self.logger.debug(f"⚠️ Erreur extraction métadonnées {filename}: {e}")
                file_info.update({
                    'series': '',
                    'volume': '',
                    'chapter': ''
                })
            
            # Mettre en cache
            self._add_to_file_cache(file_path, {'file_info': file_info})
            
            return file_info
            
        except Exception as e:
            self.logger.warning(f"⚠️ Erreur création info fichier {file_path}: {e}")
            return None
    
    def _extract_metadata(self, filename: str) -> Tuple[str, str, str]:
        """Extrait les métadonnées d'un nom de fichier"""
        # Supprimer l'extension
        name_without_ext = Path(filename).stem
        
        # Patterns courants pour les mangas/comics
        import re
        
        # Pattern: Series - Volume 01 - Chapter 001
        pattern1 = r'^(.+?)\s*[-_]\s*[Vv]olume\s*(\d+)\s*[-_]\s*[Cc]hapter\s*(\d+)'
        match = re.search(pattern1, name_without_ext)
        if match:
            return match.group(1).strip(), f"Volume {match.group(2)}", f"Chapter {match.group(3)}"
        
        # Pattern: Series Vol.01 Ch.001
        pattern2 = r'^(.+?)\s+[Vv]ol\.?\s*(\d+)\s+[Cc]h\.?\s*(\d+)'
        match = re.search(pattern2, name_without_ext)
        if match:
            return match.group(1).strip(), f"Vol.{match.group(2)}", f"Ch.{match.group(3)}"
        
        # Pattern: Series 01-001
        pattern3 = r'^(.+?)\s+(\d+)-(\d+)'
        match = re.search(pattern3, name_without_ext)
        if match:
            return match.group(1).strip(), f"Vol.{match.group(2)}", f"Ch.{match.group(3)}"
        
        # Fallback: retourner le nom complet
        return name_without_ext, '', ''
    
    def _natural_sort_key(self, filename: str) -> List:
        """Clé de tri naturel optimisée"""
        import re
        
        # Pattern pour extraire les nombres
        pattern = r'(\d+)'
        
        def convert(text):
            return int(text) if text.isdigit() else text.lower()
        
        return [convert(c) for c in re.split(pattern, filename)]
    
    def apply_filters(self, files, search_term="", series_filter="", volume_filter="", chapter_filter="", sort_by="name", reverse=False):
        """Applique les filtres avec optimisations"""
        try:
            filtered_files = files.copy()
            
            # Filtre de recherche globale
            if search_term:
                search_lower = search_term.lower()
                filtered_files = [
                    f for f in filtered_files 
                    if search_lower in f['name'].lower() or 
                       search_lower in f.get('series', '').lower()
                ]
            
            # Filtres spécifiques
            if series_filter:
                filtered_files = [
                    f for f in filtered_files 
                    if series_filter.lower() in f.get('series', '').lower()
                ]
            
            if volume_filter:
                filtered_files = [
                    f for f in filtered_files 
                    if volume_filter.lower() in f.get('volume', '').lower()
                ]
            
            if chapter_filter:
                filtered_files = [
                    f for f in filtered_files 
                    if chapter_filter.lower() in f.get('chapter', '').lower()
                ]
            
            # Tri optimisé
            if sort_by == "name":
                filtered_files.sort(key=lambda x: self._natural_sort_key(x['name']), reverse=reverse)
            elif sort_by == "size":
                filtered_files.sort(key=lambda x: x['size'], reverse=reverse)
            elif sort_by == "date":
                filtered_files.sort(key=lambda x: x['modified'], reverse=reverse)
            elif sort_by == "pages":
                filtered_files.sort(key=lambda x: x.get('pages', 0), reverse=reverse)
            
            return filtered_files
            
        except Exception as e:
            self.logger.error(f"❌ Erreur application filtres: {e}")
            return files
    
    def select_all_files(self, files):
        """Sélectionne tous les fichiers"""
        for file in files:
            file['selected'] = True
    
    def deselect_all_files(self, files):
        """Désélectionne tous les fichiers"""
        for file in files:
            file['selected'] = False
    
    def invert_selection(self, files):
        """Inverse la sélection des fichiers"""
        for file in files:
            file['selected'] = not file['selected']
    
    def get_selected_files(self, files):
        """Retourne les fichiers sélectionnés"""
        return [f for f in files if f.get('selected', False)]
    
    def convert_files(self, files_to_convert, callback=None):
        """Convertit les fichiers avec optimisations de performance"""
        try:
            if self.is_converting:
                self.logger.warning("⚠️ Conversion déjà en cours")
                return
            
            self.is_converting = True
            self._conversion_stats = {
                'total_files': len(files_to_convert),
                'converted_files': 0,
                'failed_files': 0,
                'start_time': time.time(),
                'end_time': None
            }
            
            self.logger.info(f"🚀 Début conversion de {len(files_to_convert)} fichiers")
            
            # Lancer la conversion en parallèle
            self._run_parallel_conversion(files_to_convert, callback)
            
        except Exception as e:
            self.logger.error(f"❌ Erreur conversion fichiers: {e}")
            self.is_converting = False
    
    def _run_parallel_conversion(self, files_to_convert, callback=None):
        """Exécute la conversion en parallèle avec optimisations"""
        try:
            # Utiliser ThreadPoolExecutor pour la conversion parallèle
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                # Soumettre toutes les tâches de conversion
                future_to_file = {
                    executor.submit(self._convert_single_file, file_info): file_info 
                    for file_info in files_to_convert
                }
                
                # Traiter les résultats au fur et à mesure
                for future in as_completed(future_to_file):
                    file_info = future_to_file[future]
                    
                    try:
                        success = future.result()
                        
                        if success:
                            file_info['converted'] = True
                            file_info['status'] = 'completed'
                            self._conversion_stats['converted_files'] += 1
                            self.logger.info(f"✅ Conversion réussie: {file_info['name']}")
                        else:
                            file_info['status'] = 'failed'
                            self._conversion_stats['failed_files'] += 1
                            self.logger.error(f"❌ Conversion échouée: {file_info['name']}")
                        
                        # Appeler le callback si fourni
                        if callback:
                            callback(file_info)
                            
                    except Exception as e:
                        file_info['status'] = 'failed'
                        file_info['error'] = str(e)
                        self._conversion_stats['failed_files'] += 1
                        self.logger.error(f"❌ Erreur conversion {file_info['name']}: {e}")
                        
                        if callback:
                            callback(file_info)
            
            # Finaliser les statistiques
            self._conversion_stats['end_time'] = time.time()
            elapsed_time = self._conversion_stats['end_time'] - self._conversion_stats['start_time']
            
            self.logger.info(f"✅ Conversion terminée: {self._conversion_stats['converted_files']} réussies, "
                           f"{self._conversion_stats['failed_files']} échouées en {elapsed_time:.2f}s")
            
        except Exception as e:
            self.logger.error(f"❌ Erreur conversion parallèle: {e}")
        finally:
            self.is_converting = False
    
    def _convert_single_file(self, file_info):
        """Convertit un seul fichier avec optimisations"""
        try:
            file_path = file_info['path']
            file_ext = file_info['extension']
            
            self.logger.info(f"🔄 Conversion: {file_info['name']}")
            
            # Déterminer le chemin de sortie
            output_dir = self._get_output_directory(file_path)
            output_filename = self._generate_output_filename(file_info)
            output_path = os.path.join(output_dir, output_filename)
            
            # Options de conversion
            conversion_options = self._get_conversion_options(file_info)
            
            # Conversion selon le type de fichier
            if file_ext == '.cbr':
                success = self.native_converter.convert_cbr_to_pdf(file_path, output_path, conversion_options)
            elif file_ext == '.cbz':
                success = self.native_converter.convert_cbz_to_pdf(file_path, output_path, conversion_options)
            elif file_ext == '.epub':
                success = self.native_converter.convert_epub_to_pdf(file_path, output_path, conversion_options)
            else:
                self.logger.warning(f"⚠️ Format non supporté: {file_ext}")
                return False
            
            if success:
                # Post-traitement optimisé
                self._post_process_converted_file(output_path, file_info)
                return True
            else:
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Erreur conversion {file_info['name']}: {e}")
            return False
    
    def _get_output_directory(self, file_path: str) -> str:
        """Détermine le répertoire de sortie"""
        # Pour l'instant, utiliser le même répertoire que le fichier source
        return str(Path(file_path).parent)
    
    def _generate_output_filename(self, file_info: Dict) -> str:
        """Génère le nom de fichier de sortie"""
        base_name = Path(file_info['name']).stem
        return f"{base_name}.pdf"
    
    def _get_conversion_options(self, file_info: Dict) -> Dict:
        """Récupère les options de conversion"""
        # Options par défaut - à adapter selon l'interface
        return {
            'resize': 'A4',
            'grayscale': False,
            'optimize': True,
            'merge_order': 'Naturel'
        }
    
    def _post_process_converted_file(self, output_path: str, file_info: Dict):
        """Post-traitement du fichier converti"""
        try:
            # Vérifier que le fichier a été créé
            if os.path.exists(output_path):
                file_size = os.path.getsize(output_path)
                size_mb = file_size / (1024 * 1024)
                self.logger.info(f"✅ Fichier créé: {output_path} ({size_mb:.1f} MB)")
                
                # Enrichir les métadonnées si possible
                try:
                    self._enrich_pdf_metadata(output_path, file_info['name'])
                except Exception as e:
                    self.logger.debug(f"⚠️ Erreur enrichissement métadonnées: {e}")
            else:
                self.logger.error(f"❌ Fichier de sortie non créé: {output_path}")
                
        except Exception as e:
            self.logger.warning(f"⚠️ Erreur post-traitement: {e}")
    
    def _enrich_pdf_metadata(self, pdf_path: str, original_filename: str):
        """Enrichit les métadonnées du PDF"""
        try:
            # Pour l'instant, placeholder pour l'enrichissement des métadonnées
            # TODO: Implémenter l'enrichissement des métadonnées
            pass
        except Exception as e:
            self.logger.debug(f"⚠️ Erreur enrichissement métadonnées: {e}")
    
    def stop_conversion(self):
        """Arrête la conversion en cours"""
        try:
            self.is_converting = False
            self.logger.info("⏹️ Arrêt de la conversion demandé")
        except Exception as e:
            self.logger.error(f"❌ Erreur arrêt conversion: {e}")
    
    def get_conversion_stats(self) -> Dict:
        """Retourne les statistiques de conversion"""
        return self._conversion_stats.copy()
    
    def clear_caches(self):
        """Nettoie tous les caches"""
        self._file_cache.clear()
        self._scan_cache.clear()
        self.logger.info("🧹 Caches nettoyés")
    
    def _finalize_merge(self):
        """Finalise la fusion des PDFs"""
        try:
            if not self.merge_pdfs:
                return
            
            # TODO: Implémenter la fusion finale
            self.logger.info("📄 Fusion finale des PDFs")
            
        except Exception as e:
            self.logger.error(f"❌ Erreur fusion finale: {e}") 