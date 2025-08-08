"""
Composant de liste des fichiers
"""

import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path

from .filter_panel import FilterPanel
from .action_buttons import ActionButtons
from ..utils.file_utils import get_file_info, open_file_with_default_app


class FileList:
    """Composant de liste des fichiers avec Treeview"""
    
    def __init__(self, main_window):
        self.main_window = main_window
        self.root = main_window.root
        self.files = []
        self.file_tree = None
        self.scrollbar = None
        self.filter_panel = None
        self.action_buttons = None
        
    def setup_ui(self, parent):
        """Configure l'interface de la liste des fichiers"""
        # Frame pour la liste des fichiers
        file_frame = ttk.LabelFrame(parent, text="Fichiers à convertir", padding=5)
        file_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        # Configuration des colonnes pour la réactivité
        file_frame.columnconfigure(0, weight=1)
        file_frame.rowconfigure(1, weight=1)  # Changé de 0 à 1 pour laisser de la place aux filtres
        
        # Treeview pour la liste des fichiers
        columns = ("nom", "type", "taille", "pages", "statut", "progression")
        self.file_tree = ttk.Treeview(file_frame, columns=columns, show="headings", height=10)
        
        # Configuration des colonnes
        self.file_tree.heading("nom", text="Nom du fichier")
        self.file_tree.heading("type", text="Type")
        self.file_tree.heading("taille", text="Taille")
        self.file_tree.heading("pages", text="Pages")
        self.file_tree.heading("statut", text="Statut")
        self.file_tree.heading("progression", text="Progression")
        
        # Largeur des colonnes
        self.file_tree.column("nom", width=300, minwidth=200)
        self.file_tree.column("type", width=80, minwidth=60)
        self.file_tree.column("taille", width=100, minwidth=80)
        self.file_tree.column("pages", width=80, minwidth=60)
        self.file_tree.column("statut", width=100, minwidth=80)
        self.file_tree.column("progression", width=150, minwidth=120)
        
        # Scrollbar
        self.scrollbar = ttk.Scrollbar(file_frame, orient="vertical", command=self.file_tree.yview)
        self.file_tree.configure(yscrollcommand=self.scrollbar.set)
        
        # Placement
        self.file_tree.grid(row=1, column=0, sticky="nsew")  # Changé de row=0 à row=1
        self.scrollbar.grid(row=1, column=1, sticky="ns")    # Changé de row=0 à row=1
        
        # Événements
        self.file_tree.bind("<Double-1>", self._on_file_double_click)
        self.file_tree.bind("<Button-1>", self._on_file_click)
        
        # Panneau de filtres
        self.filter_panel = FilterPanel(file_frame, self._apply_filters)
        
        # Boutons d'action
        self.action_buttons = ActionButtons(file_frame, self.main_window)
        

        
    def update_layout(self):
        """Met à jour la mise en page lors du redimensionnement"""
        try:
            # Ajuster la largeur des colonnes en fonction de la taille de la fenêtre
            tree_width = self.file_tree.winfo_width()
            if tree_width > 0:
                # Répartition proportionnelle
                total_width = tree_width - 20  # Marge pour la scrollbar
                self.file_tree.column("nom", width=int(total_width * 0.4))
                self.file_tree.column("type", width=int(total_width * 0.1))
                self.file_tree.column("taille", width=int(total_width * 0.15))
                self.file_tree.column("pages", width=int(total_width * 0.1))
                self.file_tree.column("statut", width=int(total_width * 0.15))
                self.file_tree.column("progression", width=int(total_width * 0.1))
        except Exception as e:
            # Ignorer les erreurs de redimensionnement
            pass
            
    def add_files(self, file_paths):
        """Ajoute des fichiers à la liste"""
        for file_path in file_paths:
            if file_path not in [f['path'] for f in self.files]:
                file_info = get_file_info(file_path)
                # Compter les pages avec le file_manager
                try:
                    file_info['pages'] = self.main_window.file_manager._count_pages(file_path)
                except:
                    file_info['pages'] = "?"
                self.files.append(file_info)
                
        # Appliquer les filtres après avoir ajouté les fichiers
        self._apply_filters()
            
    def _add_file_to_tree(self, file_info):
        """Ajoute un fichier au Treeview"""
        item = self.file_tree.insert("", "end", values=(
            file_info['name'],
            file_info['type'],
            file_info['size'],
            file_info['pages'],
            file_info['status'],
            f"{file_info['progress']}%"
        ))
        # Stocker l'ID de l'item pour les mises à jour
        file_info['item_id'] = item
        
    def get_selected_files(self):
        """Récupère les fichiers sélectionnés"""
        selected_items = self.file_tree.selection()
        selected_files = []
        
        for item in selected_items:
            # Trouver le fichier correspondant
            for file_info in self.files:
                if file_info.get('item_id') == item:
                    selected_files.append(file_info['path'])
                    break
                    
        return selected_files
        
    def get_all_files(self):
        """Récupère tous les fichiers"""
        return [f['path'] for f in self.files]
        

                
    def clear_files(self):
        """Efface tous les fichiers"""
        self.files.clear()
        for item in self.file_tree.get_children():
            self.file_tree.delete(item)
        self.filter_panel.update_count(0)
            
    def _on_file_double_click(self, event):
        """Gère le double-clic sur un fichier"""
        selection = self.file_tree.selection()
        if not selection:
            return
            
        item = selection[0]
        # Ouvrir le fichier avec l'application par défaut
        for file_info in self.files:
            if file_info.get('item_id') == item:
                if not open_file_with_default_app(file_info['path']):
                    messagebox.showerror("Erreur", "Impossible d'ouvrir le fichier")
                break
                
    def _on_file_click(self, event):
        """Gère le clic sur un fichier"""
        # Mettre à jour la sélection
        pass
        
    def _apply_filters(self):
        """Applique les filtres actuels"""
        # Récupérer les valeurs des filtres
        filters = self.filter_panel.get_filters()
        
        # Effacer la liste actuelle
        for item in self.file_tree.get_children():
            self.file_tree.delete(item)
            
        # Filtrer et afficher les fichiers
        visible_count = 0
        for file_info in self.files:
            if self._file_matches_filter(file_info, filters):
                self._add_file_to_tree(file_info)
                visible_count += 1
                
        # Mettre à jour le compteur
        self.filter_panel.update_count(visible_count)
        
    def _file_matches_filter(self, file_info, filters):
        """Vérifie si un fichier correspond aux filtres"""
        # Filtre de recherche textuelle
        if filters['search']:
            if filters['search'] not in file_info['name'].lower():
                return False
                
        # Filtre par type
        if filters['type'] != "Tous":
            if file_info['type'] != f".{filters['type'].lower()}":
                return False
                
        # Filtre par statut
        if filters['status'] != "Tous":
            if file_info['status'] != filters['status']:
                return False
                
        return True
        
    def update_file_progress(self, filename, progress, message=""):
        """Met à jour la progression d'un fichier"""
        for file_info in self.files:
            if file_info['name'] == filename:
                file_info['progress'] = progress
                
                # Mettre à jour le statut selon la progression et le message
                if progress == 100:
                    file_info['status'] = 'Terminé'
                elif progress == 0 and message and "Erreur" in message:
                    file_info['status'] = 'Erreur'
                elif progress > 0:
                    file_info['status'] = 'En cours'
                    
                # Mettre à jour l'affichage si le fichier est visible
                if 'item_id' in file_info:
                    try:
                        self.file_tree.set(file_info['item_id'], "progression", f"{progress}%")
                        self.file_tree.set(file_info['item_id'], "statut", file_info['status'])
                    except:
                        # L'item n'est peut-être plus visible à cause des filtres
                        pass
                break 