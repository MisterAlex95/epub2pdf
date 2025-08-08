"""
Boutons d'action pour la liste des fichiers
"""

import tkinter as tk
from tkinter import ttk, messagebox


class ActionButtons:
    """Boutons d'action pour la liste des fichiers"""
    
    def __init__(self, parent, main_window):
        self.parent = parent
        self.main_window = main_window
        
        self._create_widgets()
        
    def _create_widgets(self):
        """Crée les boutons d'action"""
        button_frame = ttk.Frame(self.parent)
        button_frame.grid(row=2, column=0, columnspan=2, pady=(10, 0), sticky="ew")
        
        # Configuration des colonnes pour la réactivité
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)
        button_frame.columnconfigure(2, weight=1)
        button_frame.columnconfigure(3, weight=1)
        
        # Boutons avec largeur uniforme et styles
        ttk.Button(button_frame, text="Ajouter fichiers", command=self._add_files, width=15, style="Primary.TButton").grid(row=0, column=0, padx=(0, 8), sticky="ew")
        ttk.Button(button_frame, text="Ajouter dossier", command=self._add_folder, width=15, style="Primary.TButton").grid(row=0, column=1, padx=4, sticky="ew")
        ttk.Button(button_frame, text="Convertir sélection", command=self._convert_selection, width=15, style="Success.TButton").grid(row=0, column=2, padx=4, sticky="ew")
        ttk.Button(button_frame, text="Convertir tout", command=self._convert_all, width=15, style="Success.TButton").grid(row=0, column=3, padx=(8, 0), sticky="ew")
        
    def _add_files(self):
        """Ouvre le dialogue d'ajout de fichiers"""
        self.main_window._browse_files()
        
    def _add_folder(self):
        """Ouvre le dialogue d'ajout de dossier"""
        self.main_window._browse_folder()
        
    def _convert_selection(self):
        """Convertit les fichiers sélectionnés"""
        selected = self.main_window.file_list.get_selected_files()
        if selected:
            self.main_window._start_conversion(selected)
        else:
            messagebox.showwarning("Attention", "Aucun fichier sélectionné")
            
    def _convert_all(self):
        """Convertit tous les fichiers"""
        all_files = self.main_window.file_list.get_all_files()
        if all_files:
            self.main_window._start_conversion(all_files)
        else:
            messagebox.showwarning("Attention", "Aucun fichier à convertir")
