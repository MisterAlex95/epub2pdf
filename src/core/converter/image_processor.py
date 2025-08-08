"""
Module de traitement d'images pour la conversion PDF - Version optimisée
"""

import os
import time
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from .base_converter import BaseConverter


class ImageProcessor(BaseConverter):
    """Processeur d'images optimisé pour la conversion PDF"""
    
    def __init__(self, max_workers: int = 5, logger=None):
        super().__init__(max_workers, logger)
        # Initialiser le PDFMerger
        from .pdf_merger import PDFMerger
        self.pdf_merger = PDFMerger(max_workers, logger)
        
        # Optimisations de performance
        self._image_cache = {}  # Cache pour les images fréquemment utilisées
        self._max_cache_size = 50  # Taille maximale du cache
        
    def convert_images_to_pdf(self, image_paths: List[str], output_path: str, options: Dict) -> bool:
        """Convertit les images en PDF avec parallélisme optimisé et ordre personnalisable"""
        try:
            start_time = time.time()
            
            # Dédupliquer les chemins d'images
            unique_paths = list(set(image_paths))
            if len(unique_paths) != len(image_paths):
                self.logger.warning(f"⚠️ {len(image_paths) - len(unique_paths)} images dupliquées supprimées")
                image_paths = unique_paths
            
            # Trier les images une fois de plus pour garantir l'ordre
            self.logger.info(f"🔄 Tri final de {len(image_paths)} images...")
            image_paths.sort(key=lambda x: self._natural_sort_key(x))
            
            # Appliquer l'ordre de fusion selon les options
            merge_order = options.get('merge_order', 'Naturel')
            if merge_order == "Alphabétique":
                image_paths.sort(key=lambda x: Path(x).name.lower())
                self.logger.info("📝 Tri alphabétique appliqué")
            elif merge_order == "Inversé":
                image_paths.reverse()
                self.logger.info("🔄 Ordre inversé appliqué")
            elif merge_order == "Personnalisé":
                # Pour l'instant, garder l'ordre naturel
                # TODO: Implémenter l'ordre personnalisé avec interface
                self.logger.info("⚙️ Ordre personnalisé (utilise l'ordre naturel)")
            
            # Diviser les images en groupes optimisés
            group_size = self._calculate_optimal_group_size(len(image_paths), options)
            groups = [image_paths[i:i + group_size] for i in range(0, len(image_paths), group_size)]
            
            self.logger.info(f"📦 Division en {len(groups)} groupes de {group_size} images max")
            
            # Conversion parallèle optimisée avec ThreadPoolExecutor
            temp_pdfs = self._convert_groups_parallel(groups, options)
            
            if not temp_pdfs:
                self.logger.error("❌ Aucun PDF temporaire créé")
                return False
            
            # Trier les PDFs par numéro de groupe pour maintenir l'ordre
            temp_pdfs.sort(key=lambda x: x[0])
            sorted_pdfs = [pdf for _, pdf in temp_pdfs]
            
            # Dédupliquer les PDFs avant fusion
            unique_pdfs = list(set(sorted_pdfs))
            if len(unique_pdfs) != len(sorted_pdfs):
                self.logger.warning(f"⚠️ {len(sorted_pdfs) - len(unique_pdfs)} PDFs dupliqués supprimés avant fusion")
            
            # Fusionner les PDFs temporaires
            if unique_pdfs:
                self.logger.info(f"🔄 Fusion de {len(unique_pdfs)} PDFs...")
                success = self.pdf_merger.merge_pdfs(unique_pdfs, output_path)
                
                if success:
                    elapsed_time = time.time() - start_time
                    self.logger.info(f"✅ Conversion terminée en {elapsed_time:.2f}s")
                    
                    # Nettoyer le cache
                    self._clear_cache()
                    
                return success
            else:
                self.logger.error("❌ Aucun PDF temporaire créé")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Erreur conversion parallèle: {e}")
            return False
    
    def _convert_groups_parallel(self, groups: List[List[str]], options: Dict) -> List[Tuple[int, str]]:
        """Convertit les groupes en parallèle avec ThreadPoolExecutor"""
        temp_pdfs = []
        successful_groups = 0
        min_success_rate = max(1, len(groups) // 3)  # Au moins 33% des groupes
        
        # Utiliser ThreadPoolExecutor pour le parallélisme
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Soumettre toutes les tâches
            future_to_group = {
                executor.submit(self._convert_group_to_pdf, group, i, options): i 
                for i, group in enumerate(groups)
            }
            
            # Traiter les résultats au fur et à mesure
            for future in as_completed(future_to_group):
                group_num = future_to_group[future]
                try:
                    temp_pdf = future.result()
                    if temp_pdf:
                        temp_pdfs.append((group_num, temp_pdf))
                        successful_groups += 1
                        self.logger.info(f"✅ Groupe {group_num + 1}/{len(groups)} terminé")
                    else:
                        self.logger.warning(f"⚠️ Groupe {group_num + 1}/{len(groups)} échoué")
                except Exception as e:
                    self.logger.error(f"❌ Erreur groupe {group_num + 1}: {e}")
        
        # Vérifier le taux de succès
        success_rate = successful_groups / len(groups) * 100
        self.logger.info(f"📊 Taux de succès: {success_rate:.1f}% ({successful_groups}/{len(groups)} groupes)")
        
        if successful_groups < min_success_rate:
            self.logger.error(f"❌ Taux de succès trop faible: {success_rate:.1f}% < 33.3%")
            return []
        
        return temp_pdfs
    
    def _calculate_optimal_group_size(self, total_images: int, options: Dict) -> int:
        """Calcule la taille optimale des groupes avec heuristiques avancées"""
        veryfast = options.get('veryfast_mode', False)
        fast = options.get('fast_mode', False)
        
        # Taille de base selon le mode
        if veryfast:
            base_size = 60  # Plus grand pour plus de vitesse
        elif fast:
            base_size = 40
        else:
            base_size = 25
        
        # Ajuster selon le nombre de workers et la mémoire disponible
        if self.max_workers > 6:
            group_size = base_size // 2
        elif self.max_workers < 3:
            group_size = base_size * 1.5
        else:
            group_size = base_size
        
        # Ajuster selon le nombre total d'images
        if total_images > 1000:
            group_size = min(group_size, 30)  # Limiter pour éviter la surcharge mémoire
        elif total_images < 100:
            group_size = max(group_size, 15)  # Groupe minimum pour l'efficacité
        
        # Taille minimale et maximale
        return max(10, min(group_size, total_images // max(1, self.max_workers)))
    
    def _convert_group_to_pdf(self, image_paths: List[str], group_num: int, options: Dict) -> Optional[str]:
        """Convertit un groupe d'images en PDF temporaire avec optimisations"""
        try:
            if not image_paths:
                self.logger.warning(f"⚠️ Groupe {group_num}: Aucune image fournie")
                return None
            
            # Vérifier que les images existent et sont valides
            valid_images = self._validate_images(image_paths, group_num)
            if not valid_images:
                return None
            
            # Créer le PDF temporaire avec chemin relatif
            temp_pdf = str(self.temp_dir / f"group_{group_num}.pdf")
            self.logger.debug(f"📄 Création PDF temporaire: {temp_pdf}")
            
            # Utiliser Pillow avec optimisations
            try:
                self.logger.debug(f"🔄 Chargement de {len(valid_images)} images valides")
                images = self._load_images_optimized(valid_images, options)
                
                if not images:
                    self.logger.warning(f"⚠️ Groupe {group_num}: Aucune image chargée")
                    return None
                
                # Sauvegarder en PDF de manière optimisée
                success = self._save_pdf_optimized(images, temp_pdf, group_num)
                
                # Forcer la fermeture des images pour libérer la mémoire
                for img in images:
                    img.close()
                
                return temp_pdf if success else None
                        
            except Exception as e:
                self.logger.error(f"❌ Erreur conversion groupe {group_num}: {e}")
                return None
                
        except Exception as e:
            self.logger.error(f"❌ Erreur générale groupe {group_num}: {e}")
            return None
    
    def _validate_images(self, image_paths: List[str], group_num: int) -> List[str]:
        """Valide les images et retourne les chemins valides"""
        valid_images = []
        for img_path in image_paths:
            if os.path.exists(img_path) and os.path.getsize(img_path) > 0:
                valid_images.append(img_path)
            else:
                self.logger.warning(f"⚠️ Fichier inexistant ou vide: {img_path}")
        
        if not valid_images:
            self.logger.warning(f"⚠️ Groupe {group_num}: Aucune image valide")
        
        return valid_images
    
    def _load_images_optimized(self, image_paths: List[str], options: Dict) -> List:
        """Charge les images avec optimisations de mémoire et cache"""
        images = []
        
        for i, img_path in enumerate(image_paths):
            try:
                # Vérifier le cache d'abord
                if img_path in self._image_cache:
                    self.logger.debug(f"📷 Cache hit: {Path(img_path).name}")
                    cached_img = self._image_cache[img_path].copy()
                    images.append(cached_img)
                    continue
                
                self.logger.debug(f"📷 Chargement image {i+1}/{len(image_paths)}: {Path(img_path).name}")
                
                with self._open_image(img_path) as img:
                    # Appliquer les options
                    img = self._apply_image_options(img, options)
                    
                    # Copie pour éviter les problèmes
                    img_copy = img.copy()
                    images.append(img_copy)
                    
                    # Mettre en cache si possible
                    self._add_to_cache(img_path, img_copy)
                    
            except Exception as e:
                self.logger.warning(f"⚠️ Erreur ouverture {img_path}: {e}")
                continue
        
        return images
    
    def _save_pdf_optimized(self, images: List, temp_pdf: str, group_num: int) -> bool:
        """Sauvegarde optimisée en PDF"""
        try:
            self.logger.debug(f"🔄 Sauvegarde PDF groupe {group_num}: {len(images)} images")
            
            # Méthode optimisée selon le nombre d'images
            if len(images) == 1:
                # Un seul PDF
                self.logger.debug(f"📄 Sauvegarde PDF unique: {temp_pdf}")
                images[0].save(temp_pdf, 'PDF', resolution=100.0, optimize=True)
            else:
                # Plusieurs images - méthode séquentielle optimisée
                first_image = images[0]
                other_images = images[1:]
                
                self.logger.debug(f"📄 Sauvegarde PDF multiple: {temp_pdf} ({len(other_images)} images supplémentaires)")
                
                # Créer le PDF avec la première image et optimisations
                first_image.save(temp_pdf, 'PDF', resolution=100.0, save_all=True, 
                             append_images=other_images, optimize=True)
            
            # Attendre un peu pour s'assurer que le fichier est bien écrit
            time.sleep(0.1)  # Réduit pour plus de performance
            
            # Vérification rapide du PDF
            return self._verify_pdf_file(temp_pdf, group_num, len(images))
                
        except Exception as e:
            self.logger.error(f"❌ Erreur sauvegarde PDF groupe {group_num}: {e}")
            return False
    
    def _verify_pdf_file(self, temp_pdf: str, group_num: int, num_images: int) -> bool:
        """Vérification rapide et optimisée du fichier PDF"""
        if not os.path.exists(temp_pdf):
            self.logger.warning(f"⚠️ Groupe {group_num}: PDF non créé: {temp_pdf}")
            return False
        
        file_size = os.path.getsize(temp_pdf)
        self.logger.debug(f"📏 Taille du PDF créé: {file_size} bytes")
        
        if file_size < 1000:  # Au moins 1KB
            self.logger.warning(f"⚠️ Groupe {group_num}: PDF trop petit ({file_size} bytes)")
            return False
        
        # Vérification rapide du header PDF
        try:
            with open(temp_pdf, 'rb') as f:
                header = f.read(4)
                if header != b'%PDF':
                    self.logger.warning(f"⚠️ Groupe {group_num}: PDF invalide (header incorrect: {header})")
                    return False
                
                # Vérification rapide de la fin
                f.seek(-50, 2)  # Aller à 50 bytes de la fin
                end_content = f.read()
                if b'%%EOF' not in end_content:
                    self.logger.warning(f"⚠️ Groupe {group_num}: PDF incomplet (pas de %%EOF)")
                    return False
                
                self.logger.debug(f"✅ Groupe {group_num}: PDF valide créé ({num_images} images, {file_size} bytes)")
                return True
                
        except Exception as e:
            self.logger.warning(f"⚠️ Groupe {group_num}: Erreur vérification PDF: {e}")
            return False
    
    def _add_to_cache(self, img_path: str, img):
        """Ajoute une image au cache avec gestion de la taille"""
        if len(self._image_cache) >= self._max_cache_size:
            # Supprimer l'élément le plus ancien
            oldest_key = next(iter(self._image_cache))
            del self._image_cache[oldest_key]
        
        self._image_cache[img_path] = img
    
    def _clear_cache(self):
        """Nettoie le cache d'images"""
        self._image_cache.clear()
    
    def _open_image(self, img_path: str):
        """Ouvre une image avec Pillow"""
        from PIL import Image
        return Image.open(img_path)
    
    def _apply_image_options(self, img, options: Dict):
        """Applique les options de traitement à une image avec optimisations"""
        # Convertir en RGB si nécessaire
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Appliquer les options
        if options.get('grayscale', False):
            img = img.convert('L').convert('RGB')
        
        resize = options.get('resize')
        if resize:
            img = self._resize_image(img, resize)
        
        return img
    
    def _resize_image(self, img, resize: str):
        """Redimensionne une image selon les paramètres avec optimisations"""
        try:
            from PIL import Image
            
            # Définir les tailles cibles optimisées
            target_sizes = {
                "A4": (595, 842),      # A4: 210x297mm à 72dpi
                "Letter": (612, 792),   # Letter: 8.5x11" à 72dpi
                "A3": (842, 1191),     # A3: 297x420mm à 72dpi
                "A5": (420, 595),      # A5: 148x210mm à 72dpi
                "HD": (1280, 720),     # HD standard
                "FHD": (1920, 1080),   # Full HD
            }
            
            target_size = target_sizes.get(resize)
            if not target_size:
                return img
            
            # Redimensionner en conservant les proportions avec LANCZOS (meilleure qualité)
            img.thumbnail(target_size, Image.Resampling.LANCZOS)
            return img
            
        except Exception as e:
            self.logger.warning(f"⚠️ Erreur redimensionnement: {e}")
            return img
