#!/usr/bin/env python3
"""
Module pour la sélection multiple de fichiers
"""

import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
import json


class FileSelection:
    """Gestionnaire de sélection multiple de fichiers"""
    
    def __init__(self):
        self.selected_files = set()
        self.file_groups = {}
        self.selection_history = []
        
    def toggle_selection(self, file_path):
        """Bascule la sélection d'un fichier"""
        if file_path in self.selected_files:
            self.selected_files.remove(file_path)
        else:
            self.selected_files.add(file_path)
            
    def select_all(self, files):
        """Sélectionne tous les fichiers"""
        self.selected_files.update(files)
        
    def deselect_all(self):
        """Désélectionne tous les fichiers"""
        self.selected_files.clear()
        
    def select_range(self, start_file, end_file, all_files):
        """Sélectionne une plage de fichiers"""
        try:
            start_index = all_files.index(start_file)
            end_index = all_files.index(end_file)
            
            if start_index > end_index:
                start_index, end_index = end_index, start_index
                
            for i in range(start_index, end_index + 1):
                self.selected_files.add(all_files[i])
                
        except ValueError:
            pass
            
    def invert_selection(self, all_files):
        """Inverse la sélection"""
        for file_path in all_files:
            if file_path in self.selected_files:
                self.selected_files.remove(file_path)
            else:
                self.selected_files.add(file_path)
                
    def get_selected_files(self):
        """Retourne la liste des fichiers sélectionnés"""
        return list(self.selected_files)
        
    def get_selection_count(self):
        """Retourne le nombre de fichiers sélectionnés"""
        return len(self.selected_files)
        
    def create_group(self, group_name, files=None):
        """Crée un groupe de fichiers"""
        if files is None:
            files = list(self.selected_files)
            
        self.file_groups[group_name] = files
        return group_name
        
    def get_group(self, group_name):
        """Récupère un groupe de fichiers"""
        return self.file_groups.get(group_name, [])
        
    def delete_group(self, group_name):
        """Supprime un groupe de fichiers"""
        if group_name in self.file_groups:
            del self.file_groups[group_name]
            
    def get_all_groups(self):
        """Retourne tous les groupes"""
        return list(self.file_groups.keys())
        
    def save_groups(self, file_path):
        """Sauvegarde les groupes dans un fichier"""
        try:
            with open(file_path, 'w') as f:
                json.dump(self.file_groups, f, indent=2)
        except Exception as e:
            print(f"Erreur lors de la sauvegarde des groupes: {e}")
            
    def load_groups(self, file_path):
        """Charge les groupes depuis un fichier"""
        try:
            with open(file_path, 'r') as f:
                self.file_groups = json.load(f)
        except Exception as e:
            print(f"Erreur lors du chargement des groupes: {e}")


class SelectionListbox(ttk.Frame):
    """Widget de liste avec sélection multiple"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent)
        
        # Variables
        self.files = []
        self.selected_indices = set()
        self.on_selection_change = kwargs.get('on_selection_change', None)
        
        # Créer les widgets
        self._create_widgets()
        
    def _create_widgets(self):
        """Crée les widgets de l'interface"""
        # Frame principal
        main_frame = ttk.Frame(self)
        main_frame.pack(fill="both", expand=True)
        
        # Liste avec scrollbar
        list_frame = ttk.Frame(main_frame)
        list_frame.pack(fill="both", expand=True)
        
        # Listbox
        self.listbox = tk.Listbox(list_frame, selectmode="extended")
        self.listbox.pack(side="left", fill="both", expand=True)
        
        # Scrollbar verticale
        v_scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.listbox.yview)
        v_scrollbar.pack(side="right", fill="y")
        self.listbox.configure(yscrollcommand=v_scrollbar.set)
        
        # Scrollbar horizontale
        h_scrollbar = ttk.Scrollbar(main_frame, orient="horizontal", command=self.listbox.xview)
        h_scrollbar.pack(side="bottom", fill="x")
        self.listbox.configure(xscrollcommand=h_scrollbar.set)
        
        # Bindings
        self.listbox.bind('<<ListboxSelect>>', self._on_selection_change)
        self.listbox.bind('<Control-a>', self._select_all)
        self.listbox.bind('<Control-i>', self._invert_selection)
        
    def set_files(self, files):
        """Définit la liste des fichiers"""
        self.files = files
        self.listbox.delete(0, tk.END)
        
        for file_path in files:
            filename = Path(file_path).name
            self.listbox.insert(tk.END, filename)
            
    def get_selected_files(self):
        """Retourne les fichiers sélectionnés"""
        selected_indices = self.listbox.curselection()
        return [self.files[i] for i in selected_indices if i < len(self.files)]
        
    def select_files(self, file_paths):
        """Sélectionne des fichiers spécifiques"""
        self.listbox.selection_clear(0, tk.END)
        
        for file_path in file_paths:
            try:
                index = self.files.index(file_path)
                self.listbox.selection_set(index)
            except ValueError:
                pass
                
    def _on_selection_change(self, event):
        """Appelé quand la sélection change"""
        if self.on_selection_change:
            self.on_selection_change(self.get_selected_files())
            
    def _select_all(self, event):
        """Sélectionne tous les fichiers"""
        self.listbox.selection_set(0, tk.END)
        return "break"
        
    def _invert_selection(self, event):
        """Inverse la sélection"""
        all_indices = set(range(self.listbox.size()))
        selected_indices = set(self.listbox.curselection())
        
        # Désélectionner tous
        self.listbox.selection_clear(0, tk.END)
        
        # Sélectionner ceux qui n'étaient pas sélectionnés
        for index in all_indices - selected_indices:
            self.listbox.selection_set(index)
            
        return "break"


class GroupManager(ttk.Frame):
    """Widget pour gérer les groupes de fichiers"""
    
    def __init__(self, parent, file_selection, **kwargs):
        super().__init__(parent)
        
        self.file_selection = file_selection
        self.on_group_change = kwargs.get('on_group_change', None)
        
        self._create_widgets()
        
    def _create_widgets(self):
        """Crée les widgets de l'interface"""
        # Titre
        title_label = ttk.Label(self, text="Groupes de fichiers", font=("Arial", 12, "bold"))
        title_label.pack(pady=(0, 10))
        
        # Frame pour les contrôles
        controls_frame = ttk.Frame(self)
        controls_frame.pack(fill="x", pady=(0, 10))
        
        # Entrée pour le nom du groupe
        ttk.Label(controls_frame, text="Nom du groupe:").pack(side="left")
        self.group_name_var = tk.StringVar()
        self.group_name_entry = ttk.Entry(controls_frame, textvariable=self.group_name_var)
        self.group_name_entry.pack(side="left", padx=(5, 10))
        
        # Bouton pour créer un groupe
        create_button = ttk.Button(controls_frame, text="Créer", command=self._create_group)
        create_button.pack(side="left", padx=(0, 5))
        
        # Bouton pour supprimer un groupe
        delete_button = ttk.Button(controls_frame, text="Supprimer", command=self._delete_group)
        delete_button.pack(side="left")
        
        # Liste des groupes
        groups_frame = ttk.LabelFrame(self, text="Groupes existants", padding="5")
        groups_frame.pack(fill="both", expand=True)
        
        # Combobox pour les groupes
        self.groups_var = tk.StringVar()
        self.groups_combo = ttk.Combobox(groups_frame, textvariable=self.groups_var, state="readonly")
        self.groups_combo.pack(fill="x", pady=(0, 5))
        self.groups_combo.bind('<<ComboboxSelected>>', self._on_group_selected)
        
        # Bouton pour charger un groupe
        load_button = ttk.Button(groups_frame, text="Charger le groupe", command=self._load_group)
        load_button.pack(fill="x")
        
        # Mettre à jour la liste des groupes
        self._update_groups_list()
        
    def _create_group(self):
        """Crée un nouveau groupe"""
        group_name = self.group_name_var.get().strip()
        if not group_name:
            messagebox.showwarning("Attention", "Veuillez entrer un nom de groupe")
            return
            
        selected_files = self.file_selection.get_selected_files()
        if not selected_files:
            messagebox.showwarning("Attention", "Aucun fichier sélectionné")
            return
            
        self.file_selection.create_group(group_name, selected_files)
        self.group_name_var.set("")
        self._update_groups_list()
        
        if self.on_group_change:
            self.on_group_change()
            
    def _delete_group(self):
        """Supprime le groupe sélectionné"""
        group_name = self.groups_var.get()
        if group_name:
            if messagebox.askyesno("Confirmation", f"Supprimer le groupe '{group_name}' ?"):
                self.file_selection.delete_group(group_name)
                self._update_groups_list()
                
                if self.on_group_change:
                    self.on_group_change()
                    
    def _load_group(self):
        """Charge le groupe sélectionné"""
        group_name = self.groups_var.get()
        if group_name:
            files = self.file_selection.get_group(group_name)
            if self.on_group_change:
                self.on_group_change(files)
                
    def _on_group_selected(self, event):
        """Appelé quand un groupe est sélectionné"""
        group_name = self.groups_var.get()
        if group_name:
            files = self.file_selection.get_group(group_name)
            # Afficher le nombre de fichiers dans le groupe
            self.groups_combo.set(f"{group_name} ({len(files)} fichiers)")
            
    def _update_groups_list(self):
        """Met à jour la liste des groupes"""
        groups = self.file_selection.get_all_groups()
        self.groups_combo['values'] = groups
        if groups:
            self.groups_combo.set(groups[0])
        else:
            self.groups_combo.set("") 