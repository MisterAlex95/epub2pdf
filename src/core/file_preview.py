#!/usr/bin/env python3
"""
Module pour la prévisualisation des fichiers
"""

import os
import zipfile
import tempfile
import shutil
from pathlib import Path
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import ttk, messagebox
import threading


class ImageManager:
    """Gestionnaire d'images pour éviter la garbage collection"""
    
    def __init__(self):
        self.images = []
    
    def add_image(self, photo):
        """Ajoute une image à la liste des références"""
        self.images.append(photo)
    
    def clear(self):
        """Vide la liste des références"""
        self.images.clear()

class FilePreview:
    """Gestionnaire de prévisualisation des fichiers"""
    
    def __init__(self):
        self.temp_dir = None
        
    def extract_preview_image(self, file_path, max_images=3):
        """
        Extrait les premières images d'un fichier pour la prévisualisation
        
        Args:
            file_path: Chemin vers le fichier
            max_images: Nombre maximum d'images à extraire
            
        Returns:
            list: Liste des objets PIL Image
        """
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                return []
                
            extracted_images = []
            
            if file_path.suffix.lower() in ['.cbz', '.cbr']:
                # Traitement des archives
                with zipfile.ZipFile(file_path, 'r') as archive:
                    # Lister les fichiers image
                    image_files = [f for f in archive.namelist() 
                                 if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp'))]
                    
                    # Trier par nom pour avoir un ordre logique
                    image_files.sort()
                    
                    # Extraire les premières images
                    for i, img_file in enumerate(image_files[:max_images]):
                        try:
                            # Extraire l'image en mémoire
                            with archive.open(img_file) as img_data:
                                with Image.open(img_data) as img:
                                    # Redimensionner pour la prévisualisation
                                    img.thumbnail((300, 300), Image.Resampling.LANCZOS)
                                    
                                    if img.mode != 'RGB':
                                        img = img.convert('RGB')
                                    
                                    # Garder l'image en mémoire
                                    extracted_images.append(img.copy())
                                    
                        except Exception as e:
                            print(f"Erreur lors de l'extraction de {img_file}: {e}")
                            continue
                            
            elif file_path.suffix.lower() == '.epub':
                # Pour les EPUB, on pourrait extraire la couverture
                # Pour l'instant, on retourne une image par défaut
                pass
                
            return extracted_images
            
        except Exception as e:
            print(f"Erreur lors de la prévisualisation de {file_path}: {e}")
            return []
            
    def get_file_info(self, file_path):
        """
        Récupère les informations sur un fichier
        
        Args:
            file_path: Chemin vers le fichier
            
        Returns:
            dict: Informations sur le fichier
        """
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                return {}
                
            stat = file_path.stat()
            
            info = {
                'name': file_path.name,
                'size': stat.st_size,
                'size_human': self._format_size(stat.st_size),
                'modified': stat.st_mtime,
                'extension': file_path.suffix.lower(),
                'path': str(file_path)
            }
            
            # Informations spécifiques selon le type
            if file_path.suffix.lower() in ['.cbz', '.cbr']:
                try:
                    with zipfile.ZipFile(file_path, 'r') as archive:
                        file_list = archive.namelist()
                        image_count = len([f for f in file_list 
                                         if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp'))])
                        info['image_count'] = image_count
                        info['total_files'] = len(file_list)
                except:
                    info['image_count'] = 0
                    info['total_files'] = 0
                    
            return info
            
        except Exception as e:
            print(f"Erreur lors de la récupération des infos de {file_path}: {e}")
            return {}
            
    def _format_size(self, size_bytes):
        """Formate la taille en bytes en format lisible"""
        if size_bytes == 0:
            return "0 B"
        size_names = ["B", "KB", "MB", "GB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        return f"{size_bytes:.1f} {size_names[i]}"
        
    def cleanup(self):
        """Nettoie les fichiers temporaires"""
        # Plus besoin de nettoyer des fichiers temporaires
        # Les images sont maintenant gardées en mémoire
        pass


class PreviewWindow:
    """Fenêtre de prévisualisation"""
    
    def __init__(self, parent, file_path):
        """Initialise la fenêtre de prévisualisation"""
        self.window = tk.Toplevel(parent)
        self.window.title(f"Prévisualisation - {Path(file_path).name}")
        self.window.geometry("700x600")
        self.window.transient(parent)
        self.window.grab_set()
        
        # Centrer la fenêtre
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (700 // 2)
        y = (self.window.winfo_screenheight() // 2) - (600 // 2)
        self.window.geometry(f"700x600+{x}+{y}")
        
        self.file_path = file_path
        self.preview = FilePreview()
        
        # Gestionnaire d'images
        self.image_manager = ImageManager()
        
        # Créer l'interface
        self._create_widgets()
        
        # Charger la prévisualisation
        self._load_preview()
        
        # Gérer la fermeture
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def _create_widgets(self):
        """Crée les widgets de l'interface"""
        # Frame principal
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")
        
        # Configuration du grid
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Titre
        title_label = ttk.Label(main_frame, text="Informations du fichier", 
                               font=("Arial", 14, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))
        
        # Informations du fichier
        info_frame = ttk.LabelFrame(main_frame, text="Détails", padding="5")
        info_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        
        self.info_text = tk.Text(info_frame, height=8, width=60, wrap="word")
        self.info_text.grid(row=0, column=0, sticky="ew")
        
        # Scrollbar pour les infos
        info_scrollbar = ttk.Scrollbar(info_frame, orient="vertical", command=self.info_text.yview)
        info_scrollbar.grid(row=0, column=1, sticky="ns")
        self.info_text.configure(yscrollcommand=info_scrollbar.set)
        
        # Frame pour les images
        images_frame = ttk.LabelFrame(main_frame, text="Aperçu", padding="5")
        images_frame.grid(row=2, column=0, columnspan=2, sticky="nsew")
        
        # Canvas pour les images
        self.canvas = tk.Canvas(images_frame, bg="white", width=600, height=400)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        
        # Scrollbar pour les images
        canvas_scrollbar = ttk.Scrollbar(images_frame, orient="vertical", command=self.canvas.yview)
        canvas_scrollbar.grid(row=0, column=1, sticky="ns")
        self.canvas.configure(yscrollcommand=canvas_scrollbar.set)
        
        # Configuration du grid pour les images
        images_frame.columnconfigure(0, weight=1)
        images_frame.rowconfigure(0, weight=1)
        
        # Initialiser la liste des références d'images
        self.photo_references = []
        
        # Bouton fermer
        close_button = ttk.Button(main_frame, text="Fermer", command=self.window.destroy)
        close_button.grid(row=3, column=0, columnspan=2, pady=(10, 0))
        
    def _load_preview(self):
        """Charge la prévisualisation"""
        try:
            # Récupérer les informations
            info = self.preview.get_file_info(self.file_path)
            
            # Afficher les informations
            info_text = f"""Nom: {info.get('name', 'N/A')}
Taille: {info.get('size_human', 'N/A')}
Type: {info.get('extension', 'N/A').upper()}
Chemin: {info.get('path', 'N/A')}
Modifié: {self._format_date(info.get('modified', 0))}"""
            
            if 'image_count' in info:
                info_text += f"\nImages: {info.get('image_count', 0)}"
            if 'total_files' in info:
                info_text += f"\nFichiers totaux: {info.get('total_files', 0)}"
                
            self.info_text.delete(1.0, tk.END)
            self.info_text.insert(1.0, info_text)
            
            # Extraire les images de prévisualisation
            preview_images = self.preview.extract_preview_image(self.file_path)
            
            # Afficher les images
            self._display_images(preview_images)
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du chargement de la prévisualisation: {e}")
        
    def _display_images(self, images):
        """Affiche les images dans le canvas"""
        try:
            # Nettoyer le canvas et le gestionnaire d'images
            self.canvas.delete("all")
            self.image_manager.clear()
            
            if not images:
                # Aucune image trouvée
                self.canvas.create_text(300, 100, text="Aucune image trouvée", 
                                      font=("Arial", 12))
                return
                
            # Afficher les images
            y_offset = 10
            for i, img in enumerate(images):
                try:
                    # S'assurer que l'image est en mode RGB
                    if img.mode != 'RGB':
                        img = img.convert('RGB')
                    
                    # Redimensionner pour l'affichage
                    display_width = 250
                    ratio = display_width / img.width
                    display_height = int(img.height * ratio)
                    
                    # Limiter la hauteur maximale
                    if display_height > 300:
                        ratio = 300 / img.height
                        display_width = int(img.width * ratio)
                        display_height = 300
                    
                    img = img.resize((display_width, display_height), Image.Resampling.LANCZOS)
                    
                    # Convertir pour tkinter
                    photo = ImageTk.PhotoImage(img)
                    
                    # Garder une référence via le gestionnaire d'images
                    self.image_manager.add_image(photo)
                    
                    # Afficher dans le canvas
                    self.canvas.create_image(10, y_offset, anchor="nw", image=photo)
                    y_offset += display_height + 10
                    
                except Exception as e:
                    print(f"Erreur lors de l'affichage de l'image {i}: {e}")
                    continue
                    
            # Configurer le scroll
            self.canvas.update_idletasks()
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
            
        except Exception as e:
            print(f"Erreur lors de l'affichage des images: {e}")
            self.canvas.create_text(300, 100, text=f"Erreur d'affichage: {e}", 
                                  font=("Arial", 12), fill="red")
            
    def _format_date(self, timestamp):
        """Formate un timestamp en date lisible"""
        if timestamp == 0:
            return "N/A"
        from datetime import datetime
        return datetime.fromtimestamp(timestamp).strftime("%d/%m/%Y %H:%M")
        
    def on_closing(self):
        """Appelé à la fermeture de la fenêtre"""
        self.preview.cleanup()
        self.window.destroy() 