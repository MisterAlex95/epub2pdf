"""
Fenêtre principale de l'application
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import logging
import os
from pathlib import Path

from src.gui.file_list import FileList
from src.gui.options_panel import OptionsPanel
from src.gui.progress_panel import ProgressPanel
from src.core.file_manager import FileManager
from src.theme import DarkTheme
from src.utils.path_manager import PathManager
from src.utils.cleanup import cleanup_temp_files
from src.utils.config_manager import ConfigManager


class MainWindow:
    """Fenêtre principale de l'application de conversion"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Convertisseur EPUB/CBR/CBZ vers PDF")
        
        # Gestionnaire de configuration
        self.config_manager = ConfigManager()
        
        # Charger la taille et position de la fenêtre depuis la config
        window_width = self.config_manager.get('window_width', 1200)
        window_height = self.config_manager.get('window_height', 800)
        self.root.geometry(f"{window_width}x{window_height}")
        
        # Configuration du thème sombre
        self.theme = DarkTheme()
        
        # Gestionnaire de chemins
        self.path_manager = PathManager()
        
        # Initialisation des composants
        self.file_manager = FileManager()  # Pas de paramètre pour scripts_dir
        self.file_list = FileList(self)
        self.options_panel = OptionsPanel(self)
        self.progress_panel = ProgressPanel(self)
        
        # Variables d'état
        self.converting = False
        self.selected_files = []
        
        # Configuration de l'interface
        self._setup_ui()
        self._setup_bindings()
        
        # Logging
        self._setup_logging()
        
        # Nettoyage des fichiers temporaires au démarrage
        cleanup_temp_files()
        
        # Charger automatiquement le dernier chemin utilisé
        self._load_last_path()
        

        
    def _setup_ui(self):
        """Configure l'interface utilisateur"""
        # Frame principal avec scrollbar
        self.main_container = ttk.Frame(self.root)
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Canvas pour le scroll
        self.canvas = tk.Canvas(self.main_container, bg=self.theme.colors['bg_dark'])
        self.scrollbar = ttk.Scrollbar(self.main_container, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        # Configuration du scroll
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        # Créer la fenêtre dans le canvas
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Binding pour redimensionner la fenêtre du canvas
        self.canvas.bind('<Configure>', self._on_canvas_configure)
        
        # Configuration des colonnes pour la réactivité
        self.scrollable_frame.columnconfigure(0, weight=1)
        self.scrollable_frame.columnconfigure(1, weight=0)
        self.scrollable_frame.rowconfigure(0, weight=1)
        self.scrollable_frame.rowconfigure(1, weight=0)
        
        # Zone de fichiers (gauche)
        self.file_list.setup_ui(self.scrollable_frame)
        
        # Panneau d'options (droite)
        self.options_panel.setup_ui(self.scrollable_frame)
        
        # Barre de progression (bas)
        self.progress_panel.setup_ui(self.scrollable_frame)
        
        # Pack du canvas et scrollbar
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # Binding pour le scroll avec la souris
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)
        
    def _setup_bindings(self):
        """Configure les événements"""
        # Redimensionnement de la fenêtre
        self.root.bind('<Configure>', self._on_window_resize)
        
        # Raccourcis clavier
        self.root.bind('<Control-o>', self._browse_files)
        self.root.bind('<Control-d>', self._browse_folder)
        self.root.bind('<Control-r>', self._scan_files)
        self.root.bind('<Control-c>', self._convert_selection)
        self.root.bind('<Control-a>', self._convert_all)
        
    def _setup_logging(self):
        """Configure le système de logging"""
        # Utiliser le logger principal déjà configuré
        self.logger = logging.getLogger('epub2pdf')
        
    def _on_window_resize(self, event):
        """Gère le redimensionnement de la fenêtre"""
        if event.widget == self.root:
            try:
                self.file_list.update_layout()
            except Exception as e:
                # Ignorer les erreurs de redimensionnement
                pass
            
            # Sauvegarder la nouvelle taille de la fenêtre
            self.config_manager.update({
                'window_width': self.root.winfo_width(),
                'window_height': self.root.winfo_height()
            })
            
    def _browse_files(self, event=None):
        """Ouvre le dialogue de sélection de fichiers"""
        files = filedialog.askopenfilenames(
            title="Sélectionner des fichiers",
            initialdir=self.path_manager.get_last_file_path(),
            filetypes=[
                ("Fichiers supportés", "*.epub *.cbr *.cbz"),
                ("EPUB", "*.epub"),
                ("CBR", "*.cbr"),
                ("CBZ", "*.cbz"),
                ("Tous les fichiers", "*.*")
            ]
        )
        if files:
            self.path_manager.set_last_file_path(files[0])
            self.file_list.add_files(files)
            
    def _browse_folder(self, event=None):
        """Ouvre le dialogue de sélection de dossier"""
        folder = filedialog.askdirectory(
            title="Sélectionner un dossier",
            initialdir=self.path_manager.get_last_folder_path()
        )
        if folder:
            self.path_manager.set_last_folder_path(folder)
            # Utiliser scan_directory au lieu de scan_folder
            files = self.file_manager.scan_directory(folder, recursive=True)
            if files:
                self.file_list.add_files([f['path'] for f in files])
            
    def _scan_files(self, event=None):
        """Scanne les fichiers dans le dossier sélectionné"""
        # Cette méthode peut être implémentée plus tard
        pass
        
    def _convert_selection(self, event=None):
        """Convertit les fichiers sélectionnés"""
        selected = self.file_list.get_selected_files()
        if selected:
            self._start_conversion(selected)
            
    def _convert_all(self, event=None):
        """Convertit tous les fichiers"""
        all_files = self.file_list.get_all_files()
        if all_files:
            self._start_conversion(all_files)
            
    def _start_conversion(self, files):
        """Démarre la conversion en arrière-plan"""
        if self.converting:
            return
            
        # Convertir les chemins de fichiers en dictionnaires file_info
        files_to_convert = []
        for file_path in files:
            file_info = self.file_manager._create_file_info(file_path)
            if file_info is not None:  # Filtrer les fichiers None
                files_to_convert.append(file_info)
            
        self.converting = True
        self.progress_panel.start_conversion()
        
        # Démarrer la conversion dans un thread séparé
        thread = threading.Thread(
            target=self._run_conversion,
            args=(files_to_convert,),
            daemon=True
        )
        thread.start()
        
    def _run_conversion(self, files_to_convert):
        """Exécute la conversion"""
        try:
            self.file_manager.convert_files(files_to_convert)
        except Exception as e:
            logging.error(f"Erreur lors de la conversion: {e}")
            self.root.after(0, lambda: messagebox.showerror("Erreur", str(e)))
        finally:
            self.root.after(0, self._conversion_finished)
            
    def _conversion_finished(self):
        """Appelé quand la conversion est terminée"""
        self.converting = False
        self.progress_panel.stop_conversion()
        
    def update_file_progress(self, filename, progress, message=""):
        """Met à jour la progression d'un fichier"""
        self.file_list.update_file_progress(filename, progress, message)
        
    def update_global_progress(self, progress):
        """Met à jour la progression globale"""
        self.progress_panel.update_progress(progress)
        
    def log_message(self, message):
        """Ajoute un message au log"""
        self.progress_panel.add_log(message)
        
    def _on_mousewheel(self, event):
        """Gère le scroll avec la souris"""
        try:
            if event.num == 4:
                self.canvas.yview_scroll(-1, "units")
            elif event.num == 5:
                self.canvas.yview_scroll(1, "units")
            else:
                self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        except Exception as e:
            # Fallback si le scroll ne fonctionne pas
            pass
            
    def _on_canvas_configure(self, event):
        """Redimensionne la fenêtre du canvas quand le canvas change de taille"""
        self.canvas.itemconfig(self.canvas_window, width=event.width)
        
    def _load_last_path(self):
        """Charge automatiquement le dernier chemin utilisé"""
        try:
            # Essayer d'abord le dernier dossier utilisé
            last_folder = self.path_manager.get_last_folder_path()
            
            if last_folder and os.path.exists(last_folder):
                # Scanner le dossier pour les fichiers supportés
                files = self.file_manager.scan_directory(last_folder, recursive=True)
                
                if files:
                    # Ajouter les fichiers à la liste
                    file_paths = [f['path'] for f in files]
                    self.file_list.add_files(file_paths)
                    
                    # Afficher un message informatif
                    self.logger.info(f"✅ Dernier dossier chargé automatiquement: {last_folder} ({len(files)} fichiers)")
                    
                    # Mettre à jour le statut
                    self.progress_panel.add_log(f"📁 Dernier dossier chargé: {Path(last_folder).name}")
                    return
                else:
                    self.logger.info(f"📁 Dernier dossier trouvé mais vide: {last_folder}")
            
            # Si pas de dossier, essayer le dernier fichier utilisé
            last_file_path = self.path_manager.get_last_file_path()
            if last_file_path and os.path.exists(last_file_path):
                # Vérifier si c'est un fichier supporté
                if Path(last_file_path).suffix.lower() in ['.epub', '.cbr', '.cbz']:
                    self.file_list.add_files([last_file_path])
                    self.logger.info(f"✅ Dernier fichier chargé automatiquement: {Path(last_file_path).name}")
                    self.progress_panel.add_log(f"📄 Dernier fichier chargé: {Path(last_file_path).name}")
                    return
                else:
                    # Si c'est un dossier, essayer de le scanner
                    if os.path.isdir(last_file_path):
                        files = self.file_manager.scan_directory(last_file_path, recursive=True)
                        if files:
                            file_paths = [f['path'] for f in files]
                            self.file_list.add_files(file_paths)
                            self.logger.info(f"✅ Dernier chemin chargé automatiquement: {last_file_path} ({len(files)} fichiers)")
                            self.progress_panel.add_log(f"📁 Dernier chemin chargé: {Path(last_file_path).name}")
                            return
            
            self.logger.debug("Aucun dernier chemin à charger")
                
        except Exception as e:
            self.logger.warning(f"Erreur lors du chargement du dernier chemin: {e}")
    
    def cleanup_on_exit(self):
        """Nettoie les fichiers temporaires à la fermeture"""
        try:
            cleanup_temp_files()
        except Exception as e:
            logging.error(f"Erreur lors du nettoyage: {e}") 