"""
Dialogues de l'application
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
from pathlib import Path


class PreviewDialog:
    """Dialogue d'aperçu des fichiers"""
    
    def __init__(self, main_window, files):
        self.main_window = main_window
        self.root = main_window.root
        self.files = files
        self.dialog = None
        
    def show(self):
        """Affiche le dialogue d'aperçu"""
        self.dialog = tk.Toplevel(self.root)
        self.dialog.title("Aperçu des fichiers")
        self.dialog.geometry("600x400")
        self.dialog.transient(self.root)
        self.dialog.grab_set()
        
        # Centrer le dialogue
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (400 // 2)
        self.dialog.geometry(f"600x400+{x}+{y}")
        
        # Configuration de l'interface
        self._setup_ui()
        
        # Événements
        self.dialog.protocol("WM_DELETE_WINDOW", self._on_close)
        
    def _setup_ui(self):
        """Configure l'interface du dialogue"""
        # Frame principal
        main_frame = ttk.Frame(self.dialog, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Titre
        ttk.Label(main_frame, text="Fichiers sélectionnés:", font=("Arial", 12, "bold")).pack(anchor="w", pady=(0, 10))
        
        # Liste des fichiers
        list_frame = ttk.Frame(main_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Treeview pour la liste
        columns = ("nom", "type", "taille", "pages")
        self.file_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)
        
        # Configuration des colonnes
        self.file_tree.heading("nom", text="Nom du fichier")
        self.file_tree.heading("type", text="Type")
        self.file_tree.heading("taille", text="Taille")
        self.file_tree.heading("pages", text="Pages")
        
        # Largeur des colonnes
        self.file_tree.column("nom", width=300)
        self.file_tree.column("type", width=80)
        self.file_tree.column("taille", width=100)
        self.file_tree.column("pages", width=80)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.file_tree.yview)
        self.file_tree.configure(yscrollcommand=scrollbar.set)
        
        # Placement
        self.file_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Remplir la liste
        self._populate_file_list()
        
        # Boutons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(button_frame, text="Fermer", command=self._on_close).pack(side=tk.RIGHT)
        
    def _populate_file_list(self):
        """Remplit la liste des fichiers"""
        for file_path in self.files:
            path = Path(file_path)
            file_info = {
                'name': path.name,
                'type': path.suffix.lower(),
                'size': self._format_size(path.stat().st_size),
                'pages': self._count_pages(file_path)
            }
            
            self.file_tree.insert("", "end", values=(
                file_info['name'],
                file_info['type'],
                file_info['size'],
                file_info['pages']
            ))
            
    def _format_size(self, size_bytes):
        """Formate la taille en bytes"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
        
    def _count_pages(self, file_path):
        """Compte le nombre de pages d'un fichier"""
        try:
            return self.main_window.file_manager._count_pages(file_path)
        except:
            return "?"
            
    def _on_close(self):
        """Ferme le dialogue"""
        if self.dialog:
            self.dialog.destroy()


class MergeDialog:
    """Dialogue pour la fusion de fichiers"""
    
    def __init__(self, main_window):
        self.main_window = main_window
        self.root = main_window.root
        self.dialog = None
        self.merge_filename = None
        
    def show(self):
        """Affiche le dialogue de fusion"""
        self.dialog = tk.Toplevel(self.root)
        self.dialog.title("Fusion de fichiers")
        self.dialog.geometry("500x200")
        self.dialog.transient(self.root)
        self.dialog.grab_set()
        
        # Centrer le dialogue
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (200 // 2)
        self.dialog.geometry(f"500x200+{x}+{y}")
        
        # Configuration de l'interface
        self._setup_ui()
        
        # Événements
        self.dialog.protocol("WM_DELETE_WINDOW", self._on_cancel)
        
    def _setup_ui(self):
        """Configure l'interface du dialogue"""
        # Frame principal
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Titre
        ttk.Label(main_frame, text="Fusion en un seul fichier", font=("Arial", 12, "bold")).pack(pady=(0, 20))
        
        # Nom du fichier fusionné
        ttk.Label(main_frame, text="Nom du fichier fusionné:").pack(anchor="w", pady=(0, 5))
        
        self.filename_var = tk.StringVar()
        filename_entry = ttk.Entry(main_frame, textvariable=self.filename_var, width=50)
        filename_entry.pack(fill=tk.X, pady=(0, 20))
        filename_entry.focus()
        
        # Boutons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="Annuler", command=self._on_cancel).pack(side=tk.RIGHT, padx=(10, 0))
        ttk.Button(button_frame, text="Fusionner", command=self._on_merge).pack(side=tk.RIGHT)
        
        # Raccourcis clavier
        self.dialog.bind('<Return>', lambda e: self._on_merge())
        self.dialog.bind('<Escape>', lambda e: self._on_cancel())
        
    def _on_merge(self):
        """Confirme la fusion"""
        filename = self.filename_var.get().strip()
        if not filename:
            messagebox.showwarning("Attention", "Veuillez entrer un nom de fichier")
            return
            
        # Ajouter l'extension .pdf si nécessaire
        if not filename.lower().endswith('.pdf'):
            filename += '.pdf'
            
        self.merge_filename = filename
        self.dialog.destroy()
        
    def _on_cancel(self):
        """Annule la fusion"""
        self.merge_filename = None
        self.dialog.destroy()
        
    def get_filename(self):
        """Récupère le nom du fichier fusionné"""
        return self.merge_filename


class CustomOrderDialog:
    """Dialogue pour l'ordre personnalisé"""
    
    def __init__(self, main_window):
        self.main_window = main_window
        self.root = main_window.root
        self.dialog = None
        self.custom_order = []
        
    def show(self):
        """Affiche le dialogue d'ordre personnalisé"""
        self.dialog = tk.Toplevel(self.root)
        self.dialog.title("Ordre personnalisé")
        self.dialog.geometry("700x500")
        self.dialog.transient(self.root)
        self.dialog.grab_set()
        
        # Centrer le dialogue
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (700 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (500 // 2)
        self.dialog.geometry(f"700x500+{x}+{y}")
        
        # Configuration de l'interface
        self._setup_ui()
        
        # Événements
        self.dialog.protocol("WM_DELETE_WINDOW", self._on_cancel)
        
    def _setup_ui(self):
        """Configure l'interface du dialogue"""
        # Frame principal
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Titre
        ttk.Label(main_frame, text="Ordre personnalisé des fichiers", font=("Arial", 12, "bold")).pack(pady=(0, 20))
        
        # Instructions
        ttk.Label(main_frame, text="Réorganisez les fichiers dans l'ordre souhaité:").pack(anchor="w", pady=(0, 10))
        
        # Frame pour la liste et les boutons
        list_frame = ttk.Frame(main_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Treeview pour la liste des fichiers
        columns = ("ordre", "nom", "type")
        self.order_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)
        
        # Configuration des colonnes
        self.order_tree.heading("ordre", text="Ordre")
        self.order_tree.heading("nom", text="Nom du fichier")
        self.order_tree.heading("type", text="Type")
        
        # Largeur des colonnes
        self.order_tree.column("ordre", width=80)
        self.order_tree.column("nom", width=400)
        self.order_tree.column("type", width=100)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.order_tree.yview)
        self.order_tree.configure(yscrollcommand=scrollbar.set)
        
        # Placement
        self.order_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Boutons de contrôle
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Button(control_frame, text="Monter", command=self._move_up).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(control_frame, text="Descendre", command=self._move_down).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Réinitialiser", command=self._reset_order).pack(side=tk.LEFT, padx=5)
        
        # Boutons de validation
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="Annuler", command=self._on_cancel).pack(side=tk.RIGHT, padx=(10, 0))
        ttk.Button(button_frame, text="OK", command=self._on_ok).pack(side=tk.RIGHT)
        
        # Remplir la liste
        self._populate_file_list()
        
    def _populate_file_list(self):
        """Remplit la liste des fichiers"""
        files = self.main_window.file_list.get_all_files()
        
        for i, file_path in enumerate(files, 1):
            path = Path(file_path)
            self.order_tree.insert("", "end", values=(
                i,
                path.name,
                path.suffix.lower()
            ))
            
    def _move_up(self):
        """Déplace l'élément sélectionné vers le haut"""
        selection = self.order_tree.selection()
        if not selection:
            return
            
        item = selection[0]
        prev_item = self.order_tree.prev(item)
        if prev_item:
            self._swap_items(item, prev_item)
            
    def _move_down(self):
        """Déplace l'élément sélectionné vers le bas"""
        selection = self.order_tree.selection()
        if not selection:
            return
            
        item = selection[0]
        next_item = self.order_tree.next(item)
        if next_item:
            self._swap_items(item, next_item)
            
    def _swap_items(self, item1, item2):
        """Échange deux éléments dans la liste"""
        # Récupérer les valeurs
        values1 = self.order_tree.item(item1, 'values')
        values2 = self.order_tree.item(item2, 'values')
        
        # Échanger les valeurs
        self.order_tree.item(item1, values=values2)
        self.order_tree.item(item2, values=values1)
        
        # Mettre à jour les numéros d'ordre
        self._update_order_numbers()
        
    def _update_order_numbers(self):
        """Met à jour les numéros d'ordre"""
        items = self.order_tree.get_children()
        for i, item in enumerate(items, 1):
            values = list(self.order_tree.item(item, 'values'))
            values[0] = i
            self.order_tree.item(item, values=values)
            
    def _reset_order(self):
        """Réinitialise l'ordre"""
        self.order_tree.delete(*self.order_tree.get_children())
        self._populate_file_list()
        
    def _on_ok(self):
        """Confirme l'ordre personnalisé"""
        # Récupérer l'ordre actuel
        items = self.order_tree.get_children()
        self.custom_order = []
        
        for item in items:
            values = self.order_tree.item(item, 'values')
            filename = values[1]  # Nom du fichier
            
            # Trouver le chemin complet
            all_files = self.main_window.file_list.get_all_files()
            for file_path in all_files:
                if Path(file_path).name == filename:
                    self.custom_order.append(file_path)
                    break
                    
        self.dialog.destroy()
        
    def _on_cancel(self):
        """Annule l'ordre personnalisé"""
        self.custom_order = []
        self.dialog.destroy()
        
    def get_custom_order(self):
        """Récupère l'ordre personnalisé"""
        return self.custom_order 