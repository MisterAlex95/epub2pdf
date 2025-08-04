#!/usr/bin/env python3
"""
Interface graphique unifiée pour epub2pdf, cbr2pdf et cbz2pdf
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import threading
import subprocess
import os
import sys

# Imports des modules existants
from core.settings_manager import SettingsManager
from core.conversion_manager import ConversionManager
from core.config import VERSION, AUTHOR, DESCRIPTION

# Imports des nouveaux modules de gestion des fichiers
from core.file_preview import PreviewWindow
from core.file_filters import FileFilter, FileSorter, SearchEngine
from core.file_selection import FileSelection, SelectionListbox, GroupManager


class UnifiedGUI:
    """Interface unifiée pour la conversion de fichiers"""
    
    def __init__(self, root):
        """Initialise l'interface graphique unifiée"""
        self.root = root
        
        # Configuration de la fenêtre
        self.root.title(f"epub2pdf, cbr2pdf & cbz2pdf - Unified Converter v{VERSION}")
        self.root.geometry("1200x800")
        
        # Initialisation du gestionnaire de paramètres
        self.settings_manager = SettingsManager()
        
        # Initialisation des variables
        self._init_variables()
        
        # Initialisation des composants UI
        self._init_ui_components()
        
        # Chargement des paramètres
        self._load_settings()
        
        # Configuration des événements
        self._setup_events()
        
        # Configuration des événements de fenêtre
        self._setup_window_events()
        
        # Affichage du message initial
        self._show_initial_message()
        
    def _init_variables(self):
        """Initialise les variables de l'interface"""
        # Variables pour les chemins
        self.input_dir = tk.StringVar()
        self.output_dir = tk.StringVar()
        
        # Variables pour les options de conversion
        self.recursive = tk.BooleanVar(value=False)
        self.force = tk.BooleanVar(value=False)
        self.grayscale = tk.BooleanVar(value=False)
        self.zip_output = tk.BooleanVar(value=False)
        self.clean_tmp = tk.BooleanVar(value=True)
        self.open_output = tk.BooleanVar(value=False)
        self.parallel = tk.BooleanVar(value=True)
        self.max_workers = tk.IntVar(value=2)
        
        # Variables pour le redimensionnement
        self.resize_var = tk.StringVar(value="")
        self.custom_resize_var = tk.StringVar(value="")
        
        # Variables pour les métadonnées
        self.edit_metadata = tk.BooleanVar(value=False)
        self.auto_rename = tk.BooleanVar(value=False)
        self.custom_title = tk.StringVar(value="")
        self.custom_author = tk.StringVar(value="")
        self.custom_subject = tk.StringVar(value="")
        self.custom_keywords = tk.StringVar(value="")
        
        # Variables pour la conversion
        self.is_converting = tk.BooleanVar(value=False)
        self.should_stop = tk.BooleanVar(value=False)
        
        # Variables pour le statut
        self.status_var = tk.StringVar(value="Ready")
        self.progress_var = tk.DoubleVar(value=0)
        
        # Gestionnaires de fichiers
        self.file_filter = FileFilter()
        self.file_sorter = FileSorter()
        self.search_engine = SearchEngine()
        self.file_selection = FileSelection()
        
        # Variables pour les fichiers
        self.all_files = []
        self.filtered_files = []
        self.files_by_format = {'epub': [], 'cbr': [], 'cbz': []}
        
        # Variables pour la recherche et les filtres
        self.search_var = tk.StringVar()
        self.sort_var = tk.StringVar(value="name")
        self.sort_reverse = tk.BooleanVar(value=False)
        self.series_var = tk.StringVar()
        self.volume_var = tk.StringVar()
        self.chapter_var = tk.StringVar()
        
        # Variables pour l'interface
        self.files_listbox = None
        self.files_count_label = None
        
    def _init_ui_components(self):
        """Initialise les composants de l'interface"""
        # Configuration de la fenêtre principale
        self.root.title("epub2pdf - Convertisseur Unifié")
        self.root.geometry("1200x800")
        
        # Frame principal avec scrollbar
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Configuration du grid
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Titre
        title_label = ttk.Label(main_frame, text="epub2pdf - Convertisseur Unifié", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Frame pour les chemins
        self._create_path_frame(main_frame)
        
        # Frame pour les filtres et recherche
        self._create_filters_frame(main_frame)
        
        # Frame pour la liste des fichiers
        self._create_files_frame(main_frame)
        
        # Frame pour les options de conversion
        self._create_options_frame(main_frame)
        
        # Frame pour la conversion
        self._create_conversion_frame(main_frame)
        
        # Frame pour le statut
        self._create_status_frame(main_frame)
        
    def _create_path_frame(self, parent):
        """Crée le frame pour les chemins"""
        path_frame = ttk.LabelFrame(parent, text="Chemins", padding="5")
        path_frame.grid(row=1, column=0, columnspan=3, sticky="ew", pady=(0, 10))
        
        # Configuration du grid
        path_frame.columnconfigure(1, weight=1)
        path_frame.columnconfigure(3, weight=1)
        
        # Répertoire d'entrée
        ttk.Label(path_frame, text="Répertoire d'entrée:").grid(row=0, column=0, sticky="w", padx=(0, 5))
        ttk.Entry(path_frame, textvariable=self.input_dir, width=50).grid(row=0, column=1, sticky="ew", padx=(0, 10))
        ttk.Button(path_frame, text="Parcourir", command=self.browse_input).grid(row=0, column=2, padx=(0, 10))
        
        # Répertoire de sortie
        ttk.Label(path_frame, text="Répertoire de sortie:").grid(row=1, column=0, sticky="w", padx=(0, 5))
        ttk.Entry(path_frame, textvariable=self.output_dir, width=50).grid(row=1, column=1, sticky="ew", padx=(0, 10))
        ttk.Button(path_frame, text="Parcourir", command=self.browse_output).grid(row=1, column=2, padx=(0, 10))
        
        # Bouton de scan
        ttk.Button(path_frame, text="Scanner les fichiers", command=self.scan_all_files).grid(row=1, column=3)
        
    def _create_filters_frame(self, parent):
        """Crée le frame pour les filtres et la recherche"""
        filters_frame = ttk.LabelFrame(parent, text="Filtres et Recherche", padding="5")
        filters_frame.grid(row=2, column=0, columnspan=3, sticky="ew", pady=(0, 10))
        
        # Configuration du grid
        filters_frame.columnconfigure(1, weight=1)
        filters_frame.columnconfigure(3, weight=1)
        
        # Recherche
        ttk.Label(filters_frame, text="Recherche:").grid(row=0, column=0, sticky="w", padx=(0, 5))
        self.search_entry = ttk.Entry(filters_frame, textvariable=self.search_var)
        self.search_entry.grid(row=0, column=1, sticky="ew", padx=(0, 10))
        self.search_entry.bind('<KeyRelease>', self._on_search_change)
        
        # Tri
        ttk.Label(filters_frame, text="Tri:").grid(row=0, column=2, sticky="w", padx=(0, 5))
        sort_combo = ttk.Combobox(filters_frame, textvariable=self.sort_var, 
                                 values=["name", "size", "date", "volume", "chapter"], 
                                 state="readonly", width=10)
        sort_combo.grid(row=0, column=3, sticky="ew", padx=(0, 10))
        sort_combo.bind('<<ComboboxSelected>>', self._on_sort_change)
        
        # Ordre de tri
        reverse_check = ttk.Checkbutton(filters_frame, text="Ordre décroissant", 
                                      variable=self.sort_reverse, command=self._apply_filters)
        reverse_check.grid(row=0, column=4)
        
        # Filtres avancés
        advanced_frame = ttk.Frame(filters_frame)
        advanced_frame.grid(row=1, column=0, columnspan=5, sticky="ew", pady=(10, 0))
        
        # Filtre par série
        ttk.Label(advanced_frame, text="Série:").grid(row=0, column=0, sticky="w", padx=(0, 5))
        series_entry = ttk.Entry(advanced_frame, textvariable=self.series_var, width=15)
        series_entry.grid(row=0, column=1, sticky="ew", padx=(0, 10))
        series_entry.bind('<KeyRelease>', self._on_filter_change)
        
        # Filtre par volume
        ttk.Label(advanced_frame, text="Volume:").grid(row=0, column=2, sticky="w", padx=(0, 5))
        volume_entry = ttk.Entry(advanced_frame, textvariable=self.volume_var, width=8)
        volume_entry.grid(row=0, column=3, sticky="ew", padx=(0, 10))
        volume_entry.bind('<KeyRelease>', self._on_filter_change)
        
        # Filtre par chapitre
        ttk.Label(advanced_frame, text="Chapitre:").grid(row=0, column=4, sticky="w", padx=(0, 5))
        chapter_entry = ttk.Entry(advanced_frame, textvariable=self.chapter_var, width=8)
        chapter_entry.grid(row=0, column=5, sticky="ew", padx=(0, 10))
        chapter_entry.bind('<KeyRelease>', self._on_filter_change)
        
        # Bouton pour effacer les filtres
        clear_button = ttk.Button(advanced_frame, text="Effacer les filtres", 
                                 command=self._clear_filters)
        clear_button.grid(row=0, column=6, padx=(10, 0))
        
    def _create_files_frame(self, parent):
        """Crée le frame pour la liste des fichiers"""
        files_frame = ttk.LabelFrame(parent, text="Fichiers", padding="5")
        files_frame.grid(row=3, column=0, columnspan=3, sticky="nsew", pady=(0, 10))
        
        # Configuration du grid
        files_frame.columnconfigure(0, weight=1)
        files_frame.rowconfigure(1, weight=1)
        
        # Frame pour les contrôles de sélection
        selection_controls = ttk.Frame(files_frame)
        selection_controls.grid(row=0, column=0, sticky="ew", pady=(0, 5))
        
        # Boutons de sélection
        select_all_btn = ttk.Button(selection_controls, text="Tout sélectionner", 
                                   command=self._select_all_files)
        select_all_btn.pack(side="left", padx=(0, 5))
        
        deselect_all_btn = ttk.Button(selection_controls, text="Tout désélectionner", 
                                     command=self._deselect_all_files)
        deselect_all_btn.pack(side="left", padx=(0, 5))
        
        invert_btn = ttk.Button(selection_controls, text="Inverser la sélection", 
                               command=self._invert_selection)
        invert_btn.pack(side="left", padx=(0, 5))
        
        preview_btn = ttk.Button(selection_controls, text="Prévisualiser", 
                                command=self._preview_selected_file)
        preview_btn.pack(side="left", padx=(0, 5))
        
        # Label pour le nombre de fichiers
        self.files_count_label = ttk.Label(selection_controls, text="0 fichier(s)")
        self.files_count_label.pack(side="right")
        
        # Liste des fichiers avec sélection multiple
        self.files_listbox = SelectionListbox(files_frame, on_selection_change=self._on_files_selection_change)
        self.files_listbox.grid(row=1, column=0, sticky="nsew")
        
    def _create_options_frame(self, parent):
        """Crée le frame pour les options de conversion"""
        options_frame = ttk.LabelFrame(parent, text="Options de Conversion", padding="5")
        options_frame.grid(row=4, column=0, columnspan=3, sticky="ew", pady=(0, 10))
        
        # Configuration du grid
        options_frame.columnconfigure(1, weight=1)
        options_frame.columnconfigure(3, weight=1)
        
        # Options de base
        ttk.Checkbutton(options_frame, text="Récursif", variable=self.recursive).grid(row=0, column=0, sticky="w")
        ttk.Checkbutton(options_frame, text="Forcer", variable=self.force).grid(row=0, column=1, sticky="w")
        ttk.Checkbutton(options_frame, text="Niveaux de gris", variable=self.grayscale).grid(row=0, column=2, sticky="w")
        ttk.Checkbutton(options_frame, text="Zipper la sortie", variable=self.zip_output).grid(row=0, column=3, sticky="w")
        
        # Options de métadonnées
        ttk.Checkbutton(options_frame, text="📊 Métadonnées", variable=self.edit_metadata).grid(row=1, column=0, sticky="w")
        ttk.Checkbutton(options_frame, text="🏷️ Auto-rename", variable=self.auto_rename).grid(row=1, column=1, sticky="w")
        
        # Champs de métadonnées personnalisées
        metadata_frame = ttk.Frame(options_frame)
        metadata_frame.grid(row=2, column=0, columnspan=4, sticky="ew", pady=(10, 0))
        
        ttk.Label(metadata_frame, text="Titre:").grid(row=0, column=0, sticky="w", padx=(0, 5))
        ttk.Entry(metadata_frame, textvariable=self.custom_title, width=20).grid(row=0, column=1, sticky="ew", padx=(0, 10))
        
        ttk.Label(metadata_frame, text="Auteur:").grid(row=0, column=2, sticky="w", padx=(0, 5))
        ttk.Entry(metadata_frame, textvariable=self.custom_author, width=20).grid(row=0, column=3, sticky="ew", padx=(0, 10))
        
        ttk.Label(metadata_frame, text="Sujet:").grid(row=1, column=0, sticky="w", padx=(0, 5))
        ttk.Entry(metadata_frame, textvariable=self.custom_subject, width=20).grid(row=1, column=1, sticky="ew", padx=(0, 10))
        
        ttk.Label(metadata_frame, text="Mots-clés:").grid(row=1, column=2, sticky="w", padx=(0, 5))
        ttk.Entry(metadata_frame, textvariable=self.custom_keywords, width=20).grid(row=1, column=3, sticky="ew")
        
        # Configuration du grid pour les métadonnées
        metadata_frame.columnconfigure(1, weight=1)
        metadata_frame.columnconfigure(3, weight=1)
        
    def _create_status_frame(self, parent):
        """Crée le frame pour le statut"""
        status_frame = ttk.Frame(parent)
        status_frame.grid(row=6, column=0, columnspan=3, sticky="ew", pady=(10, 0))
        
        # Barre de progression
        self.progress_bar = ttk.Progressbar(status_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill="x", pady=(0, 5))
        
        # Label de statut
        self.status_label = ttk.Label(status_frame, textvariable=self.status_var)
        self.status_label.pack(side="left")
        
        # Bouton stop
        self.stop_button = ttk.Button(status_frame, text="⏹️ Stop", command=self.stop_conversion, state="disabled")
        self.stop_button.pack(side="right")
            
    def _load_settings(self):
        """Charge les paramètres sauvegardés"""
        try:
            settings = self.settings_manager.load_settings()
            
            # Restaurer les chemins
            if settings.get('input_path'):
                self.input_dir.set(settings['input_path'])
            if settings.get('output_path'):
                self.output_dir.set(settings['output_path'])
                
            # Restaurer les options de métadonnées
            self.edit_metadata.set(settings.get('edit_metadata', False))
            self.auto_rename.set(settings.get('auto_rename', False))
            
            # Restaurer les champs personnalisés
            self.custom_title.set(settings.get('custom_title', ''))
            self.custom_author.set(settings.get('custom_author', ''))
            self.custom_subject.set(settings.get('custom_subject', ''))
            self.custom_keywords.set(settings.get('custom_keywords', ''))
            
            # Restaurer la taille de la fenêtre
            window_width = settings.get('window_width', 800)
            window_height = settings.get('window_height', 600)
            self.root.geometry(f"{window_width}x{window_height}")
            
            print("📝 Paramètres chargés avec succès")
            
        except Exception as e:
            print(f"❌ Erreur lors du chargement des paramètres: {e}")
        
    def _save_settings(self):
        """Sauvegarde les paramètres actuels"""
        try:
            settings = {
                'input_path': self.input_dir.get(),
                'output_path': self.output_dir.get(),
                'edit_metadata': self.edit_metadata.get(),
                'auto_rename': self.auto_rename.get(),
                'custom_title': self.custom_title.get(),
                'custom_author': self.custom_author.get(),
                'custom_subject': self.custom_subject.get(),
                'custom_keywords': self.custom_keywords.get(),
                'window_width': self.root.winfo_width(),
                'window_height': self.root.winfo_height()
            }
            
            self.settings_manager.save_settings(settings)
            print("💾 Paramètres sauvegardés avec succès")
            
        except Exception as e:
            print(f"❌ Erreur lors de la sauvegarde des paramètres: {e}")
            
    def _setup_window_events(self):
        """Configure les événements de la fenêtre"""
        # Sauvegarder les paramètres quand la fenêtre est fermée
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        # Sauvegarder la taille quand elle change
        self.root.bind('<Configure>', self._on_window_resize)
        
    def _on_window_resize(self, event):
        """Appelé quand la taille de la fenêtre change"""
        # Éviter les appels multiples en vérifiant que c'est bien la fenêtre principale
        if event.widget == self.root:
            # Annuler le timer précédent s'il existe
            if hasattr(self, '_resize_timer'):
                self.root.after_cancel(self._resize_timer)
            
            # Programmer une nouvelle sauvegarde après 2 secondes
            self._resize_timer = self.root.after(2000, self._save_settings)
            
    def _on_closing(self):
        """Appelé quand la fenêtre est fermée"""
        self._save_settings()
        self.root.destroy()
        
    def _show_initial_message(self):
        """Affiche le message initial"""
        self.update_status("Ready - Select input directory and scan for files", "✅")
        
    def browse_input(self):
        """Ouvre le dialogue pour sélectionner le répertoire d'entrée"""
        # Utiliser le dernier chemin sauvegardé ou le répertoire courant
        initial_dir = self.input_dir.get() if self.input_dir.get() else str(Path.cwd())
        directory = filedialog.askdirectory(
            title="Select Input Directory",
            initialdir=initial_dir
        )
        if directory:
            self.input_dir.set(directory)
            self.scan_all_files()
            
    def browse_output(self):
        """Ouvre le dialogue pour sélectionner le répertoire de sortie"""
        # Utiliser le dernier chemin sauvegardé ou le répertoire courant
        initial_dir = self.output_dir.get() if self.output_dir.get() else str(Path.cwd())
        directory = filedialog.askdirectory(
            title="Select Output Directory",
            initialdir=initial_dir
        )
        if directory:
            self.output_dir.set(directory)
            
    def on_resize_change(self, event):
        """Gère le changement de taille d'image"""
        resize_value = self.resize_var.get()
        if resize_value == "Custom":
            self.custom_resize_entry.grid()
        else:
            self.custom_resize_entry.grid_remove()
            
    def _setup_events(self):
        """Configure les événements de l'interface"""
        # Ici, on ne lie plus rien à resize_combo
        # Lier d'autres événements si besoin
        pass
        
    def show_about(self):
        """Affiche la boîte de dialogue À propos"""
        about_text = f"""
📘 epub2pdf, cbr2pdf & cbz2pdf - Unified Converter

Version: {VERSION}
Author: {AUTHOR}

Description: {DESCRIPTION}

Features:
• Convert EPUB, CBR, and CBZ files to PDF
• Parallel processing for faster conversion
• Multiple output options (grayscale, resize, etc.)
• Clean and modern interface

Keyboard Shortcuts:
• Ctrl+O: Browse input directory
• Ctrl+S: Browse output directory
• Ctrl+F: Scan for files
• Ctrl+R: Convert all files
• Ctrl+D: Dry run
• Ctrl+Q: Exit
• F1: About
        """
        messagebox.showinfo("About", about_text.strip())
        
    def on_closing(self):
        """Gère la fermeture de l'application"""
        self._save_settings()
        self.root.quit()

    def clear_all(self):
        """Vide tous les fichiers et réinitialise l'interface"""
        self.all_files = []
        self.files_by_format = {'epub': [], 'cbr': [], 'cbz': []}
        self.update_file_count(0)
        self.reset_progress()
        self.update_conversion_status("Ready", "✅")
        self.log_message("🗑️ Tous les fichiers ont été supprimés")
        self.update_status("Interface réinitialisée", "🔄")
            
    def log_message(self, message):
        """Ajoute un message au log (console seulement)"""
        # Log uniquement dans la console, pas dans l'interface
        print(f"📝 {message}")
        
    def update_status(self, message, icon="✅"):
        """Met à jour le statut de l'interface"""
        # Affiche le statut dans la barre de statut
        self.status_var.set(f"{icon} {message}")
        if hasattr(self, 'status_label'):
            self.status_label.config(text=f"{icon} {message}")
        self.root.update_idletasks()
        
    def get_conversion_options(self):
        """Récupère les options de conversion actuelles"""
        resize_option = self.resize_var.get()
        if resize_option == "Custom":
            resize_option = self.custom_resize_var.get()
        return {
            'output_dir': self.output_dir.get(),
            'recursive': self.recursive.get(),
            'force': self.force.get(),
            'grayscale': self.grayscale.get(),
            'resize': resize_option,
            'zip_output': self.zip_output.get(),
            'clean_tmp': self.clean_tmp.get(),
            'open_output': self.open_output.get(),
            'parallel': self.parallel.get(),
            'max_workers': self.max_workers.get(),
            'edit_metadata': self.edit_metadata.get(),
            'auto_rename': self.auto_rename.get(),
            'custom_title': self.custom_title.get(),
            'custom_author': self.custom_author.get(),
            'custom_subject': self.custom_subject.get(),
            'custom_keywords': self.custom_keywords.get()
        }
        
    def _on_search_change(self, event=None):
        """Appelé quand la recherche change"""
        query = self.search_var.get()
        if query:
            self.filtered_files = self.search_engine.search(query, self.all_files)
        else:
            self.filtered_files = self.all_files.copy()
            
        self._apply_filters()
        
    def _on_sort_change(self, event=None):
        """Appelé quand le tri change"""
        self._apply_filters()
        
    def _on_filter_change(self, event=None):
        """Appelé quand les filtres changent"""
        self._apply_filters()
        
    def _apply_filters(self):
        """Applique tous les filtres et le tri"""
        # Appliquer les filtres
        files_to_filter = self.filtered_files if self.filtered_files else self.all_files
        
        # Filtre par série
        if self.series_var.get():
            self.file_filter.set_filter('series', self.series_var.get())
            
        # Filtre par volume
        if self.volume_var.get():
            try:
                volume = int(self.volume_var.get())
                self.file_filter.set_filter('volume', volume)
            except ValueError:
                pass
                
        # Filtre par chapitre
        if self.chapter_var.get():
            try:
                chapter = int(self.chapter_var.get())
                self.file_filter.set_filter('chapter', chapter)
            except ValueError:
                pass
                
        # Appliquer les filtres
        filtered_files = self.file_filter.apply_filters(files_to_filter)
        
        # Appliquer le tri
        sort_by = self.sort_var.get()
        reverse = self.sort_reverse.get()
        sorted_files = self.file_sorter.sort_files(filtered_files, sort_by, reverse)
        
        # Mettre à jour la liste
        self.files_listbox.set_files(sorted_files)
        self.update_file_count(len(sorted_files))
        
    def _clear_filters(self):
        """Efface tous les filtres"""
        self.search_var.set("")
        self.series_var.set("")
        self.volume_var.set("")
        self.chapter_var.set("")
        self.sort_var.set("name")
        self.sort_reverse.set(False)
        
        self.file_filter.clear_filters()
        self.filtered_files = self.all_files.copy()
        self._apply_filters()
        
    def _select_all_files(self):
        """Sélectionne tous les fichiers"""
        self.file_selection.select_all(self.all_files)
        self.files_listbox.select_files(self.all_files)
        
    def _deselect_all_files(self):
        """Désélectionne tous les fichiers"""
        self.file_selection.deselect_all()
        self.files_listbox.listbox.selection_clear(0, tk.END)
        
    def _invert_selection(self):
        """Inverse la sélection"""
        self.file_selection.invert_selection(self.all_files)
        # Mettre à jour l'affichage
        selected_files = self.file_selection.get_selected_files()
        self.files_listbox.select_files(selected_files)
        
    def _preview_selected_file(self):
        """Prévisualise le fichier sélectionné"""
        selected_files = self.files_listbox.get_selected_files()
        if not selected_files:
            messagebox.showwarning("Attention", "Aucun fichier sélectionné")
            return
            
        if len(selected_files) > 1:
            messagebox.showinfo("Information", "Prévisualisation du premier fichier sélectionné")
            
        # Ouvrir la fenêtre de prévisualisation
        preview_window = PreviewWindow(self.root, selected_files[0])
        
    def _on_files_selection_change(self, selected_files):
        """Appelé quand la sélection de fichiers change"""
        # Mettre à jour le gestionnaire de sélection
        self.file_selection.selected_files = set(selected_files)
        
        # Mettre à jour le label de compte
        count = len(selected_files)
        self.files_count_label.config(text=f"{count} fichier(s) sélectionné(s)")
        
    def scan_all_files(self):
        """Scanne tous les fichiers dans le répertoire d'entrée"""
        try:
            input_path = self.input_dir.get()
            if not input_path:
                messagebox.showwarning("Attention", "Veuillez sélectionner un répertoire d'entrée")
                return
                
            input_dir = Path(input_path)
            if not input_dir.exists():
                messagebox.showerror("Erreur", "Le répertoire d'entrée n'existe pas")
                return
                
            # Réinitialiser les listes
            self.all_files = []
            self.files_by_format = {'epub': [], 'cbr': [], 'cbz': []}
            
            # Scanner les fichiers
            for file_path in input_dir.rglob("*"):
                if file_path.is_file():
                    extension = file_path.suffix.lower()
                    if extension in ['.epub', '.cbr', '.cbz']:
                        self.all_files.append(str(file_path))
                        
                        if extension == '.epub':
                            self.files_by_format['epub'].append(str(file_path))
                        elif extension == '.cbr':
                            self.files_by_format['cbr'].append(str(file_path))
                        elif extension == '.cbz':
                            self.files_by_format['cbz'].append(str(file_path))
                            
            # Construire l'index de recherche
            self.search_engine.build_index(self.all_files)
            
            # Appliquer les filtres
            self.filtered_files = self.all_files.copy()
            self._apply_filters()
            
            # Mettre à jour l'interface
            total_files = len(self.all_files)
            self.update_file_count(total_files)
            
            # Afficher les statistiques
            stats = f"📊 Trouvé {total_files} fichiers: "
            stats += f"{len(self.files_by_format['epub'])} EPUB, "
            stats += f"{len(self.files_by_format['cbr'])} CBR, "
            stats += f"{len(self.files_by_format['cbz'])} CBZ"
            
            self.log_message(stats)
            self.update_status(f"Scan terminé - {total_files} fichiers trouvés", "✅")
            
        except Exception as e:
            error_msg = f"Erreur lors du scan: {e}"
            self.log_message(error_msg)
            self.update_status("Erreur lors du scan", "❌")
            messagebox.showerror("Erreur", error_msg)

    def stop_conversion(self):
        """Arrête la conversion en cours"""
        self.should_stop.set(True)
        self.stop_button.config(state="disabled")
        self.update_status("Conversion stopped by user", "⏹️")
        self.log_message("⏹️ Conversion stopped by user")

    def _reset_stop_flag(self):
        """Réinitialise le flag d'arrêt"""
        self.should_stop.set(False)
        self.stop_button.config(state="normal")

    def convert_all(self):
        """Convertit tous les fichiers"""
        try:
            if not self.all_files:
                messagebox.showinfo("Aucun fichier", "Aucun fichier à convertir.")
                return
                
            self.log_message(f"🔄 Conversion de {len(self.all_files)} fichier(s)...")
            self.update_status(f"Conversion de {len(self.all_files)} fichier(s)", "🔄")
            
            # Désactiver les boutons pendant la conversion
            self.convert_button.config(state="disabled")
            self.convert_selection_button.config(state="disabled")
            self.merge_selection_button.config(state="disabled")
            self.dry_run_button.config(state="disabled")
            self.stop_button.config(state="normal")
            
            # Réinitialiser le flag d'arrêt
            self._reset_stop_flag()
            
            # Démarrer la conversion dans un thread séparé
            conversion_thread = threading.Thread(target=self._run_conversion, args=(self.all_files,))
            conversion_thread.daemon = True
            conversion_thread.start()
            
        except Exception as e:
            self.log_message(f"❌ Erreur lors de la conversion: {str(e)}")
            self.update_status("Erreur lors de la conversion", "❌")

    def convert_selection(self):
        """Convertit uniquement les fichiers sélectionnés"""
        try:
            selected_files = self.file_selection.get_selected_files()
            if not selected_files:
                messagebox.showinfo("Aucune sélection", "Aucun fichier sélectionné.")
                return
                
            self.log_message(f"🔄 Conversion de {len(selected_files)} fichier(s) sélectionné(s)...")
            self.update_status(f"Conversion de {len(selected_files)} fichier(s) sélectionné(s)", "🔄")
            
            # Désactiver les boutons pendant la conversion
            self.convert_button.config(state="disabled")
            self.convert_selection_button.config(state="disabled")
            self.merge_selection_button.config(state="disabled")
            self.dry_run_button.config(state="disabled")
            self.stop_button.config(state="normal")
            
            # Réinitialiser le flag d'arrêt
            self._reset_stop_flag()
            
            # Démarrer la conversion dans un thread séparé
            conversion_thread = threading.Thread(target=self._run_conversion, args=(selected_files,))
            conversion_thread.daemon = True
            conversion_thread.start()
            
        except Exception as e:
            self.log_message(f"❌ Erreur lors de la conversion: {str(e)}")
            self.update_status("Erreur lors de la conversion", "❌")

    def merge_selection(self):
        """Fusionne les fichiers sélectionnés en un seul PDF"""
        try:
            selected_files = self.file_selection.get_selected_files()
            if len(selected_files) < 2:
                messagebox.showinfo("Sélection insuffisante", "Sélectionnez au moins 2 fichiers pour fusionner.")
                return
                
            # Demander l'ordre des fichiers
            ordered_files = self._show_file_order_dialog(selected_files)
            if not ordered_files:
                return  # L'utilisateur a annulé
                
            # Demander le nom du fichier fusionné
            from tkinter import simpledialog
            merged_filename = simpledialog.askstring(
                "Nom du fichier fusionné", 
                "Entrez le nom du fichier fusionné (sans .pdf):",
                initialvalue=f"merged_{len(ordered_files)}_files"
            )
            
            if not merged_filename:
                return  # L'utilisateur a annulé
                
            # Ajouter l'extension .pdf si pas présente
            if not merged_filename.endswith('.pdf'):
                merged_filename += '.pdf'
                
            self.log_message(f"🔄 Fusion de {len(ordered_files)} fichier(s) en '{merged_filename}'...")
            self.update_status(f"Fusion de {len(ordered_files)} fichier(s) en '{merged_filename}'", "🔄")
            
            # Désactiver les boutons pendant la conversion
            self.convert_button.config(state="disabled")
            self.convert_selection_button.config(state="disabled")
            self.merge_selection_button.config(state="disabled")
            self.dry_run_button.config(state="disabled")
            self.stop_button.config(state="normal")
            
            # Réinitialiser le flag d'arrêt
            self._reset_stop_flag()
            
            # Démarrer la fusion dans un thread séparé
            conversion_thread = threading.Thread(target=self._run_merge, args=(ordered_files, merged_filename))
            conversion_thread.daemon = True
            conversion_thread.start()
            
        except Exception as e:
            self.log_message(f"❌ Erreur lors de la fusion: {str(e)}")
            self.update_status("Erreur lors de la fusion", "❌")

    def _show_file_order_dialog(self, files):
        """Affiche une fenêtre pour réorganiser l'ordre des fichiers"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Réorganiser l'ordre des fichiers")
        dialog.geometry("600x400")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Centrer la fenêtre
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (600 // 2)
        y = (dialog.winfo_screenheight() // 2) - (400 // 2)
        dialog.geometry(f"600x400+{x}+{y}")
        
        # Variables
        file_list = list(files)
        result_files = None
        
        # Frame principal
        main_frame = ttk.Frame(dialog, padding="10")
        main_frame.pack(fill="both", expand=True)
        
        # Label d'instruction
        instruction_label = ttk.Label(main_frame, 
                                    text="Réorganisez l'ordre des fichiers.\nUtilisez les boutons pour déplacer les fichiers.",
                                    font=("Arial", 10, "bold"))
        instruction_label.pack(pady=(0, 10))
        
        # Frame pour la liste et les boutons
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill="both", expand=True)
        
        # Liste des fichiers
        list_frame = ttk.Frame(content_frame)
        list_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        list_label = ttk.Label(list_frame, text="Ordre des fichiers:")
        list_label.pack(anchor="w")
        
        # Listbox avec scrollbar
        listbox_frame = ttk.Frame(list_frame)
        listbox_frame.pack(fill="both", expand=True)
        
        listbox = tk.Listbox(listbox_frame, selectmode="single", height=15)
        scrollbar = ttk.Scrollbar(listbox_frame, orient="vertical", command=listbox.yview)
        listbox.configure(yscrollcommand=scrollbar.set)
        
        listbox.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Remplir la liste
        for i, file_path in enumerate(file_list, 1):
            filename = Path(file_path).name
            listbox.insert(tk.END, f"{i:2d}. {filename}")
        
        # Boutons de contrôle
        button_frame = ttk.Frame(content_frame)
        button_frame.pack(side="right", fill="y")
        
        def move_up():
            selection = listbox.curselection()
            if selection and selection[0] > 0:
                index = selection[0]
                # Échanger dans la liste
                file_list[index], file_list[index-1] = file_list[index-1], file_list[index]
                # Mettre à jour l'affichage
                listbox.delete(index)
                listbox.delete(index-1)
                filename = Path(file_list[index-1]).name
                listbox.insert(index-1, f"{index:2d}. {filename}")
                filename = Path(file_list[index]).name
                listbox.insert(index, f"{index+1:2d}. {filename}")
                listbox.selection_set(index-1)
        
        def move_down():
            selection = listbox.curselection()
            if selection and selection[0] < len(file_list) - 1:
                index = selection[0]
                # Échanger dans la liste
                file_list[index], file_list[index+1] = file_list[index+1], file_list[index]
                # Mettre à jour l'affichage
                listbox.delete(index)
                listbox.delete(index)
                filename = Path(file_list[index]).name
                listbox.insert(index, f"{index+1:2d}. {filename}")
                filename = Path(file_list[index+1]).name
                listbox.insert(index+1, f"{index+2:2d}. {filename}")
                listbox.selection_set(index+1)
        
        def move_top():
            selection = listbox.curselection()
            if selection and selection[0] > 0:
                index = selection[0]
                # Déplacer en haut
                file_path = file_list.pop(index)
                file_list.insert(0, file_path)
                # Mettre à jour l'affichage
                listbox.delete(0, tk.END)
                for i, file_path in enumerate(file_list, 1):
                    filename = Path(file_path).name
                    listbox.insert(tk.END, f"{i:2d}. {filename}")
                listbox.selection_set(0)
        
        def move_bottom():
            selection = listbox.curselection()
            if selection and selection[0] < len(file_list) - 1:
                index = selection[0]
                # Déplacer en bas
                file_path = file_list.pop(index)
                file_list.append(file_path)
                # Mettre à jour l'affichage
                listbox.delete(0, tk.END)
                for i, file_path in enumerate(file_list, 1):
                    filename = Path(file_path).name
                    listbox.insert(tk.END, f"{i:2d}. {filename}")
                listbox.selection_set(len(file_list) - 1)
        
        def confirm():
            nonlocal result_files
            result_files = file_list.copy()
            dialog.destroy()
        
        def cancel():
            dialog.destroy()
        
        # Boutons
        ttk.Button(button_frame, text="⬆️ Haut", command=move_up).pack(pady=2)
        ttk.Button(button_frame, text="⬇️ Bas", command=move_down).pack(pady=2)
        ttk.Button(button_frame, text="⬆️⬆️ Premier", command=move_top).pack(pady=2)
        ttk.Button(button_frame, text="⬇️⬇️ Dernier", command=move_bottom).pack(pady=2)
        
        # Séparateur
        ttk.Separator(button_frame, orient="horizontal").pack(fill="x", pady=10)
        
        # Boutons de confirmation
        ttk.Button(button_frame, text="✅ Confirmer", command=confirm).pack(pady=2)
        ttk.Button(button_frame, text="❌ Annuler", command=cancel).pack(pady=2)
        
        # Attendre la fermeture de la fenêtre
        dialog.wait_window()
        
        return result_files

    def _run_conversion(self, files_to_convert):
        """Exécute la conversion dans un thread séparé"""
        try:
            success_count = 0
            total_files = len(files_to_convert)
            
            for i, file_path in enumerate(files_to_convert):
                # Vérifier si l'arrêt a été demandé
                if self.should_stop.get():
                    self.conversion_completed("Conversion stopped", "⏹️")
                    return
                
                # Mettre à jour la progression
                percentage = (i / total_files) * 100
                self.progress_var.set(percentage)
                self.update_status(f"Conversion en cours... {percentage:.1f}%", "🔄")
                
                # Déterminer le script à utiliser
                extension = Path(file_path).suffix.lower()
                if extension == '.epub':
                    script = './scripts/epub2pdf.sh'
                elif extension == '.cbr':
                    script = './scripts/cbr2pdf.sh'
                elif extension == '.cbz':
                    script = './scripts/cbz2pdf.sh'
                else:
                    self.log_message(f"❌ Format non supporté: {file_path}")
                    continue
                
                try:
                    # Préparer les arguments (options d'abord, puis fichier)
                    output_dir = self.output_dir.get() if self.output_dir.get() else str(Path(file_path).parent)
                    args = [script, '--output-dir', output_dir, file_path]
                    
                    # Ajouter les options si configurées
                    if self.edit_metadata_var.get():
                        args.extend(['--edit-metadata'])
                    if self.auto_rename_var.get():
                        args.extend(['--auto-rename'])
                    
                    result = subprocess.run(args, capture_output=True, text=True, timeout=300)
                    
                    if result.returncode == 0:
                        success_count += 1
                        self.log_message(f"✅ Converted: {Path(file_path).name}")
                    else:
                        self.log_message(f"❌ Error converting {Path(file_path).name}: {result.stderr}")
                        
                except subprocess.TimeoutExpired:
                    self.log_message(f"⏰ Timeout converting {Path(file_path).name}")
                except Exception as e:
                    self.log_message(f"❌ Error converting {Path(file_path).name}: {str(e)}")
            
            # Finaliser la conversion
            if self.should_stop.get():
                self.conversion_completed("Conversion stopped", "⏹️")
            else:
                stats_text = f"Conversion terminée: {success_count}/{total_files} succès"
                self.conversion_completed(stats_text, "✅")
                
        except Exception as e:
            self.log_message(f"❌ Erreur lors de la conversion: {str(e)}")
            self.conversion_completed("Erreur lors de la conversion", "❌")

    def _run_merge(self, files_to_merge, merged_filename):
        """Exécute la fusion dans un thread séparé"""
        try:
            import tempfile
            import shutil
            
            # Créer un répertoire temporaire
            temp_dir = tempfile.mkdtemp()
            converted_files = []
            
            self.log_message(f"🔄 Conversion de {len(files_to_merge)} fichiers pour fusion...")
            
            for i, file_path in enumerate(files_to_merge):
                # Vérifier si l'arrêt a été demandé
                if self.should_stop.get():
                    self.conversion_completed("Fusion stopped", "⏹️")
                    return
                
                # Mettre à jour la progression
                percentage = (i / len(files_to_merge)) * 50  # Première moitié pour conversion
                self.progress_var.set(percentage)
                self.update_status(f"Conversion pour fusion... {percentage:.1f}%", "🔄")
                
                # Déterminer le script à utiliser
                extension = Path(file_path).suffix.lower()
                if extension == '.epub':
                    script = './scripts/epub2pdf.sh'
                elif extension == '.cbr':
                    script = './scripts/cbr2pdf.sh'
                elif extension == '.cbz':
                    script = './scripts/cbz2pdf.sh'
                else:
                    self.log_message(f"❌ Format non supporté: {file_path}")
                    continue
                
                try:
                    # Convertir en PDF temporaire
                    temp_output = Path(temp_dir) / f"temp_{i:03d}.pdf"
                    args = [script, '--output-dir', str(temp_output.parent), file_path]
                    
                    result = subprocess.run(args, capture_output=True, text=True, timeout=300)
                    
                    if result.returncode == 0:
                        # Chercher le PDF généré dans le répertoire temporaire
                        pdf_files = list(Path(temp_dir).glob("*.pdf"))
                        if pdf_files:
                            # Prendre le plus récent
                            latest_pdf = max(pdf_files, key=lambda x: x.stat().st_mtime)
                            converted_files.append(latest_pdf)
                            self.log_message(f"✅ Converted: {Path(file_path).name}")
                        else:
                            self.log_message(f"❌ No PDF generated for {Path(file_path).name}")
                    else:
                        self.log_message(f"❌ Error converting {Path(file_path).name}")
                        
                except subprocess.TimeoutExpired:
                    self.log_message(f"⏰ Timeout converting {Path(file_path).name}")
                except Exception as e:
                    self.log_message(f"❌ Error converting {Path(file_path).name}: {str(e)}")
            
            if not converted_files:
                self.conversion_completed("Aucun fichier converti pour fusion", "❌")
                return
            
            # Fusionner les PDFs
            if self.should_stop.get():
                self.conversion_completed("Fusion stopped", "⏹️")
                return
            
            self.log_message(f"🔄 Fusion de {len(converted_files)} PDFs...")
            self.update_status("Fusion des PDFs...", "🔄")
            self.progress_var.set(75)
            
            try:
                # Créer le nom du fichier fusionné
                output_dir = self.output_dir.get() if self.output_dir.get() else str(Path(files_to_merge[0]).parent)
                merged_path = Path(output_dir) / merged_filename
                
                # Fusionner avec pdftk
                pdf_list = " ".join(str(pdf) for pdf in converted_files)
                merge_cmd = f"pdftk {pdf_list} cat output \"{merged_path}\""
                
                result = subprocess.run(merge_cmd, shell=True, capture_output=True, text=True, timeout=300)
                
                if result.returncode == 0:
                    self.log_message(f"✅ Fusion réussie: {merged_path}")
                    stats_text = f"Fusion terminée: {len(converted_files)} fichiers → {merged_filename}"
                    self.conversion_completed(stats_text, "✅")
                else:
                    self.log_message(f"❌ Erreur lors de la fusion: {result.stderr}")
                    self.conversion_completed("Erreur lors de la fusion", "❌")
                    
            except subprocess.TimeoutExpired:
                self.log_message("⏰ Timeout lors de la fusion")
                self.conversion_completed("Timeout lors de la fusion", "⏰")
            except Exception as e:
                self.log_message(f"❌ Erreur lors de la fusion: {str(e)}")
                self.conversion_completed("Erreur lors de la fusion", "❌")
            finally:
                # Nettoyer les fichiers temporaires
                try:
                    shutil.rmtree(temp_dir)
                except:
                    pass
                    
        except Exception as e:
            self.log_message(f"❌ Erreur lors de la fusion: {str(e)}")
            self.conversion_completed("Erreur lors de la fusion", "❌")

    def conversion_completed(self, message, icon="✅"):
        """Finalise la conversion"""
        self.progress_var.set(100)
        self.update_status(message, icon)
        self.log_message(f"{icon} {message}")
        
        # Réactiver les boutons
        self.convert_button.config(state="normal")
        self.convert_selection_button.config(state="normal")
        self.merge_selection_button.config(state="normal")
        self.dry_run_button.config(state="normal")
        self.stop_button.config(state="disabled")
        
        # Réinitialiser le flag d'arrêt
        self._reset_stop_flag()

    def dry_run(self):
        """Simulation de conversion (dry run)"""
        try:
            if not self.all_files:
                messagebox.showinfo("Aucun fichier", "Aucun fichier à simuler.")
                return
            self.log_message(f"🧪 Simulation de conversion de {len(self.all_files)} fichiers...")
            for file_path in self.all_files:
                self.log_message(f"[DRY RUN] {file_path}")
            self.update_status("Simulation terminée", "✅")
        except Exception as e:
            self.log_message(f"Erreur dry run: {e}")
            self.update_status("Erreur dry run", "❌")

    def update_conversion_status(self, message, icon="✅"):
        """Met à jour le statut de conversion"""
        self.conversion_status_label.config(text=f"{icon} {message}")
        
    def update_file_count(self, count):
        """Met à jour le label du nombre de fichiers"""
        summary_text = f"{count} fichier(s) trouvé(s)"
        if hasattr(self, 'files_count_label') and self.files_count_label:
            self.files_count_label.config(text=summary_text, foreground='green')
            
    def reset_progress(self):
        """Réinitialise la barre de progression"""
        self.progress_bar['value'] = 0
        self.progress_var.set(0)
        self.status_var.set("Ready")
        
    def update_progress(self, current, total, completed=0, failed=0):
        """Met à jour la barre de progression avec des statistiques détaillées"""
        if total > 0:
            percentage = (current / total) * 100
            self.progress_bar['value'] = percentage
            self.progress_var.set(percentage)
            self.status_var.set(f"Progression : {percentage:.1f}%")
            
            # Mise à jour des statistiques avec répartition par format
            stats_text = f"Progress: {current}/{total} files"
            if completed > 0 or failed > 0:
                stats_text += f" | ✅ {completed} | ❌ {failed}"
                
                # Ajouter la répartition par format si des conversions ont eu lieu
                if completed > 0:
                    format_stats = []
                    for format_key, files in self.files_by_format.items():
                        if files:
                            format_stats.append(f"{format_key.upper()}: {len(files)}")
                    if format_stats:
                        stats_text += f" | Formats: {', '.join(format_stats)}"
                        
            self.status_var.set(stats_text)

    def _create_conversion_frame(self, parent):
        """Crée le frame de conversion"""
        conversion_frame = ttk.LabelFrame(parent, text="Conversion", padding="10")
        conversion_frame.grid(row=4, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        
        # Boutons de conversion
        buttons_frame = ttk.Frame(conversion_frame)
        buttons_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        
        # Bouton Convertir
        self.convert_button = ttk.Button(buttons_frame, text="Convertir", 
                                        command=self.convert_all, style="Accent.TButton")
        self.convert_button.grid(row=0, column=0, padx=(0, 5))
        
        # Bouton Convertir la sélection
        self.convert_selection_button = ttk.Button(buttons_frame, text="Convertir la sélection", 
                                                 command=self.convert_selection)
        self.convert_selection_button.grid(row=0, column=1, padx=5)
        
        # Bouton Fusionner la sélection
        self.merge_selection_button = ttk.Button(buttons_frame, text="Fusionner en 1 tome", 
                                               command=self.merge_selection)
        self.merge_selection_button.grid(row=0, column=2, padx=5)
        
        # Bouton Dry Run
        self.dry_run_button = ttk.Button(buttons_frame, text="Dry Run", 
                                        command=self.dry_run)
        self.dry_run_button.grid(row=0, column=3, padx=5)
        
        # Bouton Stop
        self.stop_button = ttk.Button(buttons_frame, text="Stop", 
                                     command=self.stop_conversion, state="disabled")
        self.stop_button.grid(row=0, column=4, padx=5)
        
        # Bouton Clear All
        self.clear_button = ttk.Button(buttons_frame, text="Clear All", 
                                      command=self.clear_all)
        self.clear_button.grid(row=0, column=5, padx=(5, 0))
        
        # Label de statut de conversion
        self.conversion_status_label = ttk.Label(conversion_frame, text="Prêt à convertir", 
                                               font=("Arial", 10))
        self.conversion_status_label.grid(row=1, column=0, columnspan=2, pady=(5, 0))


def main():
    """Point d'entrée principal de l'application"""
    print("🔍 Démarrage de l'application epub2pdf...")
    
    # Vérifier que les scripts existent
    required_scripts = [
        "scripts/epub2pdf.sh",
        "scripts/cbr2pdf.sh",
        "scripts/cbz2pdf.sh"
    ]
    missing_scripts = []
    
    print("📋 Vérification des scripts requis...")
    for script in required_scripts:
        if not os.path.exists(script):
            missing_scripts.append(script)
            print(f"❌ Script manquant: {script}")
        else:
            print(f"✅ Script trouvé: {script}")
            
    if missing_scripts:
        error_msg = f"Missing scripts: {', '.join(missing_scripts)}"
        print(f"❌ Erreur: {error_msg}")
        messagebox.showerror("Error", error_msg)
        return
        
    print("✅ Tous les scripts sont présents")
    print("🚀 Lancement de l'interface graphique...")
        
    # Créer et lancer l'interface
    root = tk.Tk()
    app = UnifiedGUI(root)
    
    # Faire apparaître la fenêtre au premier plan
    root.lift()
    root.attributes('-topmost', True)
    root.after_idle(root.attributes, '-topmost', False)
    
    print("🎨 Interface graphique initialisée")
    root.mainloop()


if __name__ == "__main__":
    main() 