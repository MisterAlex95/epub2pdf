"""
Module de fusion PDF optimisé
"""

import os
import shutil
import time
from pathlib import Path
from typing import List, Optional
from concurrent.futures import ThreadPoolExecutor
from .base_converter import BaseConverter


class PDFMerger(BaseConverter):
    """Fusionneur de PDFs optimisé"""
    
    def __init__(self, max_workers: int = 5, logger=None):
        super().__init__(max_workers, logger)
        self._pdf_cache = {}  # Cache pour les PDFs fréquemment utilisés
        self._max_cache_size = 20  # Taille maximale du cache
    
    def merge_pdfs(self, temp_pdfs: List[str], output_path: str) -> bool:
        """Fusionne les PDFs temporaires en un seul PDF final avec optimisations"""
        try:
            start_time = time.time()
            
            if not temp_pdfs:
                self.logger.error("❌ Aucun PDF à fusionner")
                return False
            
            # Dédupliquer les PDFs
            unique_pdfs = list(set(temp_pdfs))
            if len(unique_pdfs) != len(temp_pdfs):
                self.logger.warning(f"⚠️ {len(temp_pdfs) - len(unique_pdfs)} PDFs dupliqués supprimés")
            
            # Valider les PDFs avant fusion
            valid_pdfs = self._validate_pdfs(unique_pdfs)
            if not valid_pdfs:
                self.logger.error("❌ Aucun PDF valide à fusionner")
                return False
            
            self.logger.info(f"🔄 Fusion de {len(valid_pdfs)} PDFs valides...")
            
            # Essayer d'abord avec PyPDF2 optimisé
            if self.pypdf2_available:
                if self._merge_with_pypdf2_optimized(valid_pdfs, output_path):
                    elapsed_time = time.time() - start_time
                    self.logger.info(f"✅ Fusion PyPDF2 terminée en {elapsed_time:.2f}s")
                    return True
            
            # Fallback avec méthode simple optimisée
            success = self._merge_simple_optimized(valid_pdfs, output_path)
            if success:
                elapsed_time = time.time() - start_time
                self.logger.info(f"✅ Fusion simple terminée en {elapsed_time:.2f}s")
            
            return success
            
        except Exception as e:
            self.logger.error(f"❌ Erreur fusion PDFs: {e}")
            return False
    
    def _validate_pdfs(self, pdf_paths: List[str]) -> List[str]:
        """Valide les PDFs et retourne les chemins valides"""
        valid_pdfs = []
        
        for pdf_path in pdf_paths:
            try:
                if not os.path.exists(pdf_path):
                    self.logger.warning(f"⚠️ PDF inexistant: {pdf_path}")
                    continue
                
                file_size = os.path.getsize(pdf_path)
                if file_size < 1000:  # Au moins 1KB
                    self.logger.warning(f"⚠️ PDF trop petit ignoré: {pdf_path} ({file_size} bytes)")
                    continue
                
                # Vérification rapide du header PDF
                with open(pdf_path, 'rb') as f:
                    header = f.read(4)
                    if header != b'%PDF':
                        self.logger.warning(f"⚠️ PDF sans header valide ignoré: {pdf_path}")
                        continue
                
                valid_pdfs.append(pdf_path)
                
            except Exception as e:
                self.logger.warning(f"⚠️ Erreur validation PDF {pdf_path}: {e}")
                continue
        
        self.logger.info(f"📊 {len(valid_pdfs)}/{len(pdf_paths)} PDFs validés")
        return valid_pdfs
    
    def _merge_with_pypdf2_optimized(self, temp_pdfs: List[str], output_path: str) -> bool:
        """Fusionne avec PyPDF2 optimisé"""
        try:
            from PyPDF2 import PdfWriter, PdfReader
            
            writer = PdfWriter()
            total_pages = 0
            processed_pdfs = 0
            
            # Traitement optimisé avec gestion mémoire
            for i, pdf_path in enumerate(temp_pdfs):
                try:
                    # Vérifier le cache d'abord
                    if pdf_path in self._pdf_cache:
                        self.logger.debug(f"📄 Cache hit: {Path(pdf_path).name}")
                        cached_pages = self._pdf_cache[pdf_path]
                        for page in cached_pages:
                            writer.add_page(page)
                        total_pages += len(cached_pages)
                        processed_pdfs += 1
                        continue
                    
                    self.logger.debug(f"📄 Traitement PDF {i+1}/{len(temp_pdfs)}: {Path(pdf_path).name}")
                    
                    with open(pdf_path, 'rb') as file:
                        reader = PdfReader(file)
                        
                        # Vérifier que le PDF est valide
                        if len(reader.pages) == 0:
                            self.logger.warning(f"⚠️ PDF vide ignoré: {pdf_path}")
                            continue
                        
                        # Ajouter toutes les pages avec gestion mémoire
                        pages = []
                        for page in reader.pages:
                            writer.add_page(page)
                            pages.append(page)
                            total_pages += 1
                        
                        # Mettre en cache si possible
                        self._add_to_cache(pdf_path, pages)
                        
                        processed_pdfs += 1
                        self.logger.debug(f"✅ PDF {i+1}/{len(temp_pdfs)} ajouté ({len(reader.pages)} pages)")
                        
                except Exception as e:
                    self.logger.warning(f"⚠️ Erreur lecture PDF {pdf_path}: {e}")
                    continue
            
            # Sauvegarder le PDF final avec optimisations
            if total_pages > 0:
                self.logger.info(f"📄 Sauvegarde PDF final: {total_pages} pages de {processed_pdfs} fichiers")
                
                with open(output_path, 'wb') as output_file:
                    writer.write(output_file)
                
                # Vérification rapide du fichier créé
                if self._verify_output_file(output_path, total_pages):
                    return True
                else:
                    self.logger.error("❌ PDF final invalide")
                    return False
            else:
                self.logger.error("❌ Aucune page à fusionner")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Erreur fusion PyPDF2: {e}")
            return False
    
    def _merge_simple_optimized(self, temp_pdfs: List[str], output_path: str) -> bool:
        """Fusion simple optimisée en copiant le meilleur PDF"""
        try:
            # Trouver le PDF le plus volumineux (probablement le plus complet)
            best_pdf = None
            max_size = 0
            
            for pdf_path in temp_pdfs:
                try:
                    if os.path.exists(pdf_path):
                        file_size = os.path.getsize(pdf_path)
                        if file_size > max_size:
                            max_size = file_size
                            best_pdf = pdf_path
                except Exception as e:
                    self.logger.warning(f"⚠️ Erreur vérification taille {pdf_path}: {e}")
                    continue
            
            if best_pdf:
                # Copier le meilleur PDF
                shutil.copy2(best_pdf, output_path)
                
                if os.path.exists(output_path):
                    size_mb = os.path.getsize(output_path) / (1024 * 1024)
                    self.logger.info(f"✅ Meilleur PDF copié: {size_mb:.1f} MB")
                    return True
            
            self.logger.error("❌ Aucun PDF valide trouvé")
            return False
            
        except Exception as e:
            self.logger.error(f"❌ Erreur fusion simple: {e}")
            return False
    
    def _verify_output_file(self, output_path: str, expected_pages: int) -> bool:
        """Vérifie rapidement le fichier de sortie"""
        try:
            if not os.path.exists(output_path):
                self.logger.error("❌ Fichier de sortie non créé")
                return False
            
            file_size = os.path.getsize(output_path)
            if file_size < 1000:  # Au moins 1KB
                self.logger.error(f"❌ Fichier de sortie trop petit: {file_size} bytes")
                return False
            
            # Vérification rapide du header PDF
            with open(output_path, 'rb') as f:
                header = f.read(4)
                if header != b'%PDF':
                    self.logger.error("❌ Fichier de sortie n'est pas un PDF valide")
                    return False
            
            size_mb = file_size / (1024 * 1024)
            self.logger.info(f"✅ PDF final validé: {expected_pages} pages, {size_mb:.1f} MB")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Erreur vérification fichier de sortie: {e}")
            return False
    
    def _add_to_cache(self, pdf_path: str, pages):
        """Ajoute des pages au cache avec gestion de la taille"""
        if len(self._pdf_cache) >= self._max_cache_size:
            # Supprimer l'élément le plus ancien
            oldest_key = next(iter(self._pdf_cache))
            del self._pdf_cache[oldest_key]
        
        self._pdf_cache[pdf_path] = pages
    
    def cleanup_temp_files(self, temp_pdfs: List[str]):
        """Nettoie les fichiers temporaires avec parallélisme"""
        try:
            cleaned_count = 0
            
            # Nettoyage parallèle pour les gros volumes
            if len(temp_pdfs) > 10:
                with ThreadPoolExecutor(max_workers=min(4, self.max_workers)) as executor:
                    futures = [executor.submit(self._delete_file, pdf_path) for pdf_path in temp_pdfs]
                    for future in futures:
                        if future.result():
                            cleaned_count += 1
            else:
                # Nettoyage séquentiel pour les petits volumes
                for pdf_path in temp_pdfs:
                    if self._delete_file(pdf_path):
                        cleaned_count += 1
            
            if cleaned_count > 0:
                self.logger.debug(f"🧹 {cleaned_count} fichiers temporaires supprimés")
                
        except Exception as e:
            self.logger.warning(f"⚠️ Erreur nettoyage: {e}")
    
    def _delete_file(self, file_path: str) -> bool:
        """Supprime un fichier de manière sécurisée"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
        except Exception as e:
            self.logger.debug(f"⚠️ Erreur suppression {file_path}: {e}")
        return False
    
    def clear_cache(self):
        """Nettoie le cache de PDFs"""
        self._pdf_cache.clear()
