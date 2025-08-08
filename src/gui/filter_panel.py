"""
Panneau de filtres pour la liste des fichiers
"""

import tkinter as tk
from tkinter import ttk
from src.utils.config_manager import ConfigManager


class FilterPanel:
    """Panneau de filtres pour la liste des fichiers"""
    
    def __init__(self, parent, on_filter_change_callback):
        self.parent = parent
        self.on_filter_change = on_filter_change_callback
        self.config_manager = ConfigManager()
        self.search_var = None
        self.type_var = None
        self.status_var = None
        self.count_label = None
        
        self._create_widgets()
        
    def _create_widgets(self):
        """Crée les widgets du panneau de filtres"""
        filter_frame = ttk.Frame(self.parent)
        filter_frame.grid(row=0, column=0, columnspan=2, pady=(0, 10), sticky="ew")
        
        # Configuration des colonnes pour un meilleur alignement
        filter_frame.columnconfigure(0, weight=0)  # Label Recherche
        filter_frame.columnconfigure(1, weight=1)  # Champ de recherche
        filter_frame.columnconfigure(2, weight=0)  # Label Type
        filter_frame.columnconfigure(3, weight=0)  # Combo Type
        filter_frame.columnconfigure(4, weight=0)  # Label Statut
        filter_frame.columnconfigure(5, weight=0)  # Combo Statut
        filter_frame.columnconfigure(6, weight=0)  # Bouton
        filter_frame.columnconfigure(7, weight=0)  # Compteur
        
        # Recherche textuelle
        ttk.Label(filter_frame, text="Recherche:", width=10).grid(row=0, column=0, sticky="w", padx=(0, 5))
        # Ne pas charger automatiquement le filtre de recherche au démarrage
        self.search_var = tk.StringVar(value="")
        self.search_var.trace_add("write", self._on_filter_change)
        search_entry = ttk.Entry(filter_frame, textvariable=self.search_var, width=25)
        search_entry.grid(row=0, column=1, sticky="ew", padx=(0, 15))
        
        # Filtre par type
        ttk.Label(filter_frame, text="Type:", width=8).grid(row=0, column=2, sticky="w", padx=(0, 5))
        self.type_var = tk.StringVar(value=self.config_manager.get('last_series_filter', 'Tous'))
        self.type_var.trace_add("write", self._on_filter_change)
        type_combo = ttk.Combobox(filter_frame, textvariable=self.type_var, 
                                 values=["Tous", "EPUB", "CBR", "CBZ"], 
                                 state="readonly", width=8)
        type_combo.grid(row=0, column=3, sticky="ew", padx=(0, 15))
        
        # Filtre par statut
        ttk.Label(filter_frame, text="Statut:", width=8).grid(row=0, column=4, sticky="w", padx=(0, 5))
        self.status_var = tk.StringVar(value=self.config_manager.get('last_volume_filter', 'Tous'))
        self.status_var.trace_add("write", self._on_filter_change)
        status_combo = ttk.Combobox(filter_frame, textvariable=self.status_var,
                                   values=["Tous", "En attente", "En cours", "Terminé"],
                                   state="readonly", width=10)
        status_combo.grid(row=0, column=5, sticky="ew", padx=(0, 15))
        
        # Bouton effacer filtres
        ttk.Button(filter_frame, text="Effacer filtres", command=self.clear_filters, width=12, style="Secondary.TButton").grid(row=0, column=6, padx=(0, 15))
        
        # Compteur de fichiers
        self.count_label = ttk.Label(filter_frame, text="0 fichiers", width=12)
        self.count_label.grid(row=0, column=7, sticky="e", padx=(0, 5))
        
    def _on_filter_change(self, *args):
        """Appelé quand les filtres changent"""
        # Sauvegarder les filtres seulement s'ils ne sont pas vides
        search_term = self.search_var.get().strip()
        series_filter = self.type_var.get()
        volume_filter = self.status_var.get()
        
        # Sauvegarder toujours, même si vide (pour effacer les anciens filtres)
        self.config_manager.update({
            'last_search_term': search_term,
            'last_series_filter': series_filter,
            'last_volume_filter': volume_filter
        })
        
        # Appeler le callback de filtrage
        self.on_filter_change()
        
    def clear_filters(self):
        """Efface tous les filtres"""
        self.search_var.set("")
        self.type_var.set("Tous")
        self.status_var.set("Tous")
        
    def get_filters(self):
        """Récupère les valeurs actuelles des filtres"""
        return {
            'search': self.search_var.get().lower(),
            'type': self.type_var.get(),
            'status': self.status_var.get()
        }
        
    def update_count(self, count):
        """Met à jour le compteur de fichiers"""
        self.count_label.config(text=f"{count} fichiers")
    
    def load_saved_filters(self):
        """Charge les filtres sauvegardés (optionnel)"""
        saved_search = self.config_manager.get('last_search_term', '')
        if saved_search and saved_search.strip():
            self.search_var.set(saved_search)
