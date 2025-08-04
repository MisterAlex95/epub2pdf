#!/usr/bin/env python3
"""
Module pour gérer les onglets de conversion
"""

import tkinter as tk
from tkinter import ttk
from pathlib import Path
from core.config import COLORS, FILE_FORMATS


class TabConverter:
    """Classe pour gérer un onglet de conversion de fichiers"""
    
    def __init__(self, parent, format_key):
        """
        Initialise un onglet de conversion
        
        Args:
            parent: Le widget parent (UnifiedGUI)
            format_key: Clé du format ('epub', 'cbr', 'cbz')
        """
        self.parent = parent
        self.format_key = format_key
        self.format_config = FILE_FORMATS[format_key]
        self.files = []
        self.create_widgets()
        
    def create_widgets(self):
        """Crée les widgets de l'onglet"""
        # Frame principal
        self.frame = ttk.Frame(self.parent.notebook)
        
        # Frame principal
        main_frame = ttk.LabelFrame(
            self.frame, 
            text=f"{self.format_config['icon']} {self.format_config['name']}", 
            padding="12"
        )
        main_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        
        # Frame d'information
        info_frame = ttk.Frame(main_frame)
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Label de compteur de fichiers
        self.file_count_label = ttk.Label(
            info_frame, 
            text="No files found",
            font=("TkDefaultFont", 10)
        )
        self.file_count_label.pack(anchor=tk.W)
        
        # Label de statut
        self.status_label = ttk.Label(
            info_frame,
            text="Ready",
            font=("TkDefaultFont", 9),
            foreground='gray'
        )
        self.status_label.pack(anchor=tk.W, pady=(2, 0))
        
        # Frame de progression
        progress_frame = ttk.Frame(main_frame)
        progress_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Barre de progression
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            mode='determinate',
            length=300
        )
        self.progress_bar.pack(fill=tk.X, pady=(0, 5))
        
        # Label de progression
        self.progress_label = ttk.Label(
            progress_frame,
            text="0%",
            font=("TkDefaultFont", 9),
            foreground='gray'
        )
        self.progress_label.pack(anchor=tk.CENTER)
        
        # Frame des statistiques
        stats_frame = ttk.Frame(main_frame)
        stats_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Statistiques
        self.stats_label = ttk.Label(
            stats_frame,
            text="",
            font=("TkDefaultFont", 9),
            foreground='gray'
        )
        self.stats_label.pack(anchor=tk.W)
        
        # Frame des boutons
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Bouton de conversion
        self.convert_button = ttk.Button(
            buttons_frame, 
            text="🔄 Convert", 
            command=self.convert_files, 
            style="Success.TButton"
        )
        self.convert_button.pack(side=tk.LEFT, padx=(0, 5))
        
        # Bouton de nettoyage
        self.clear_button = ttk.Button(
            buttons_frame, 
            text="🗑️ Clear", 
            command=self.clear_list
        )
        self.clear_button.pack(side=tk.LEFT)
        
    def scan_files(self, input_dir, recursive=False):
        """
        Scanne les fichiers du format spécifié
        
        Args:
            input_dir: Répertoire d'entrée
            recursive: Si True, scanne les sous-répertoires
            
        Returns:
            int: Nombre de fichiers trouvés
        """
        self.files = []
        self.update_status("Scanning for files...", "🔍")
        self.reset_progress()
        
        input_path = Path(input_dir)
        
        # Pattern de recherche
        if recursive:
            pattern = f"**/*.{self.format_key}"
        else:
            pattern = f"*.{self.format_key}"
            
        # Recherche des fichiers
        for file_path in input_path.glob(pattern):
            if file_path.is_file():
                self.files.append(str(file_path))
        
        # Mise à jour du compteur
        count = len(self.files)
        self._update_file_count(count)
        
        if count > 0:
            self.update_status("Ready to convert", "✅")
        else:
            self.update_status("No files found", "⚠️")
        
        return count
        
    def _update_file_count(self, count):
        """Met à jour l'affichage du compteur de fichiers"""
        if count == 0:
            self.file_count_label.config(
                text="No files found", 
                foreground='gray'
            )
        elif count == 1:
            self.file_count_label.config(
                text=f"1 file found", 
                foreground=COLORS['success']
            )
        else:
            self.file_count_label.config(
                text=f"{count} files found", 
                foreground=COLORS['success']
            )
        
    def update_status(self, message, icon="✅"):
        """Met à jour le statut de l'onglet"""
        self.status_label.config(text=f"{icon} {message}")
        
    def reset_progress(self):
        """Réinitialise la barre de progression"""
        self.progress_bar['value'] = 0
        self.progress_label.config(text="0%")
        self.stats_label.config(text="")
        
    def update_progress(self, current, total, completed=0, failed=0):
        """Met à jour la barre de progression"""
        if total > 0:
            percentage = (current / total) * 100
            self.progress_bar['value'] = percentage
            self.progress_label.config(text=f"{percentage:.1f}%")
            
            # Mise à jour des statistiques
            stats_text = f"Progress: {current}/{total} files"
            if completed > 0 or failed > 0:
                stats_text += f" | ✅ {completed} | ❌ {failed}"
            self.stats_label.config(text=stats_text)
        
    def clear_list(self):
        """Vide la liste des fichiers"""
        self.files = []
        self._update_file_count(0)
        self.reset_progress()
        self.update_status("Ready", "✅")
        
    def convert_files(self):
        """Lance la conversion des fichiers de cet onglet"""
        if not self.files:
            from tkinter import messagebox
            messagebox.showwarning(
                "Warning", 
                f"No {self.format_config['name']} files to convert"
            )
            return
            
        # Notifie le parent pour démarrer la conversion
        self.parent.start_conversion(self.format_key, self.files) 