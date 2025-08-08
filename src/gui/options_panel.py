"""
Panneau d'options de conversion
"""

import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
from src.utils.config_manager import ConfigManager


class OptionsPanel:
    """Panneau d'options de conversion"""
    
    def __init__(self, main_window):
        self.main_window = main_window
        self.root = main_window.root
        self.config_manager = ConfigManager()
        
        # Variables pour les options (chargées depuis la config)
        self.merge_volumes_var = tk.BooleanVar(value=self.config_manager.get('merge_volumes', False))
        self.fetch_metadata_var = tk.BooleanVar(value=self.config_manager.get('fetch_metadata', True))
        self.merge_order_var = tk.StringVar(value=self.config_manager.get('merge_order', 'Naturel'))
        self.custom_order_var = tk.BooleanVar(value=self.config_manager.get('custom_order', False))
        self.max_workers_var = tk.IntVar(value=self.config_manager.get('max_workers', 5))
        self.speed_mode_var = tk.StringVar(value=self.config_manager.get('speed_mode', 'Normal'))
        self.auto_rename_var = tk.BooleanVar(value=self.config_manager.get('auto_rename', True))
        self.output_folder_var = tk.StringVar(value=self.config_manager.get('output_folder', ''))
        
        # Options de destination
        self.destination_mode_var = tk.StringVar(value=self.config_manager.get('destination_mode', 'Dossier personnalisé'))
        self.create_subfolders_var = tk.BooleanVar(value=self.config_manager.get('create_subfolders', False))
        self.overwrite_existing_var = tk.BooleanVar(value=self.config_manager.get('overwrite_existing', False))
        
        # Configurer les callbacks pour sauvegarder automatiquement
        self._setup_auto_save()
        
    def setup_ui(self, parent):
        """Configure l'interface du panneau d'options"""
        # Frame pour les options avec scroll
        self.options_container = ttk.Frame(parent)
        self.options_container.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        
        # Canvas pour le scroll des options
        self.options_canvas = tk.Canvas(self.options_container, width=300, bg=self.main_window.theme.colors['bg_dark'])
        self.options_scrollbar = ttk.Scrollbar(self.options_container, orient="vertical", command=self.options_canvas.yview)
        self.options_frame = ttk.LabelFrame(self.options_canvas, text="Options de conversion", padding=5)
        
        # Configuration du scroll des options
        self.options_frame.bind(
            "<Configure>",
            lambda e: self.options_canvas.configure(scrollregion=self.options_canvas.bbox("all"))
        )
        
        # Créer la fenêtre dans le canvas des options
        self.options_canvas_window = self.options_canvas.create_window((0, 0), window=self.options_frame, anchor="nw")
        self.options_canvas.configure(yscrollcommand=self.options_scrollbar.set)
        
        # Binding pour redimensionner la fenêtre du canvas des options
        self.options_canvas.bind('<Configure>', self._on_options_canvas_configure)
        
        # Configuration des colonnes pour la réactivité
        self.options_frame.columnconfigure(0, weight=1)
        
        # Options de fusion
        self._create_merge_options(self.options_frame)
        
        # Options de métadonnées
        self._create_metadata_options(self.options_frame)
        
        # Options de performance
        self._create_performance_options(self.options_frame)
        
        # Options de sortie
        self._create_output_options(self.options_frame)
        
        # Options de dossier de sortie
        self._create_output_folder_options(self.options_frame)
        
        # Boutons d'action
        self._create_action_buttons(self.options_frame)
        
        # Pack du canvas et scrollbar
        self.options_canvas.pack(side="left", fill="both", expand=True)
        self.options_scrollbar.pack(side="right", fill="y")
        
        # Binding pour le scroll avec la souris sur les options
        self.options_canvas.bind_all("<MouseWheel>", self._on_options_mousewheel)
        self.options_canvas.bind_all("<Button-4>", self._on_options_mousewheel)
        self.options_canvas.bind_all("<Button-5>", self._on_options_mousewheel)
        
        # Forcer la mise à jour du scroll après un délai
        self.options_canvas.after(100, self._update_options_scroll)
    
    def _setup_auto_save(self):
        """Configure les callbacks pour sauvegarder automatiquement les changements"""
        # Callbacks pour les variables de fusion
        self.merge_volumes_var.trace_add("write", lambda *args: self._save_merge_options())
        self.fetch_metadata_var.trace_add("write", lambda *args: self._save_metadata_options())
        self.merge_order_var.trace_add("write", lambda *args: self._save_merge_options())
        self.custom_order_var.trace_add("write", lambda *args: self._save_merge_options())
        
        # Callbacks pour les variables de performance
        self.max_workers_var.trace_add("write", lambda *args: self._save_performance_options())
        self.speed_mode_var.trace_add("write", lambda *args: self._save_performance_options())
        
        # Callbacks pour les variables de sortie
        self.auto_rename_var.trace_add("write", lambda *args: self._save_output_options())
        self.output_folder_var.trace_add("write", lambda *args: self._save_output_options())
        
        # Callbacks pour les variables de destination
        self.destination_mode_var.trace_add("write", lambda *args: self._save_destination_options())
        self.create_subfolders_var.trace_add("write", lambda *args: self._save_destination_options())
        self.overwrite_existing_var.trace_add("write", lambda *args: self._save_destination_options())
    
    def _save_merge_options(self):
        """Sauvegarde les options de fusion"""
        self.config_manager.update({
            'merge_volumes': self.merge_volumes_var.get(),
            'merge_order': self.merge_order_var.get(),
            'custom_order': self.custom_order_var.get()
        })
    
    def _save_metadata_options(self):
        """Sauvegarde les options de métadonnées"""
        self.config_manager.set('fetch_metadata', self.fetch_metadata_var.get())
    
    def _save_performance_options(self):
        """Sauvegarde les options de performance"""
        self.config_manager.update({
            'max_workers': self.max_workers_var.get(),
            'speed_mode': self.speed_mode_var.get()
        })
    
    def _save_output_options(self):
        """Sauvegarde les options de sortie"""
        self.config_manager.update({
            'auto_rename': self.auto_rename_var.get(),
            'output_folder': self.output_folder_var.get()
        })
    
    def _save_destination_options(self):
        """Sauvegarde les options de destination"""
        self.config_manager.update({
            'destination_mode': self.destination_mode_var.get(),
            'create_subfolders': self.create_subfolders_var.get(),
            'overwrite_existing': self.overwrite_existing_var.get()
        })
        
    def _create_merge_options(self, parent):
        """Crée les options de fusion"""
        merge_frame = ttk.LabelFrame(parent, text="Fusion", padding=3)
        merge_frame.grid(row=0, column=0, sticky="ew", pady=(0, 5))
        
        # Fusion en un seul tome
        ttk.Checkbutton(
            merge_frame, 
            text="Fusionner en 1 tome",
            variable=self.merge_volumes_var,
            command=self._on_merge_option_change
        ).grid(row=0, column=0, sticky="w", pady=2)
        
        # Ordre de fusion
        ttk.Label(merge_frame, text="Ordre de fusion:").grid(row=1, column=0, sticky="w", pady=(5, 2))
        order_combo = ttk.Combobox(
            merge_frame,
            textvariable=self.merge_order_var,
            values=["Naturel", "Alphabétique", "Inversé", "Personnalisé"],
            state="readonly",
            width=15
        )
        order_combo.grid(row=2, column=0, sticky="w", pady=2)
        order_combo.bind("<<ComboboxSelected>>", self._on_order_change)
        
        # Ordre personnalisé
        ttk.Checkbutton(
            merge_frame,
            text="Personnaliser l'ordre",
            variable=self.custom_order_var,
            command=self._on_custom_order_change
        ).grid(row=3, column=0, sticky="w", pady=2)
        
    def _create_metadata_options(self, parent):
        """Crée les options de métadonnées"""
        metadata_frame = ttk.LabelFrame(parent, text="Métadonnées", padding=3)
        metadata_frame.grid(row=1, column=0, sticky="ew", pady=(0, 5))
        
        # Récupération depuis une source
        ttk.Checkbutton(
            metadata_frame,
            text="Récupérer metadata depuis une source",
            variable=self.fetch_metadata_var
        ).grid(row=0, column=0, sticky="w", pady=2)
        
    def _create_performance_options(self, parent):
        """Crée les options de performance"""
        perf_frame = ttk.LabelFrame(parent, text="Performance", padding=3)
        perf_frame.grid(row=2, column=0, sticky="ew", pady=(0, 5))
        
        # Nombre de workers
        ttk.Label(perf_frame, text="Nombre de workers:").grid(row=0, column=0, sticky="w", pady=2)
        workers_spin = ttk.Spinbox(
            perf_frame,
            from_=1,
            to=10,
            textvariable=self.max_workers_var,
            width=10
        )
        workers_spin.grid(row=1, column=0, sticky="w", pady=2)
        
        # Mode de vitesse
        ttk.Label(perf_frame, text="Mode de vitesse:").grid(row=2, column=0, sticky="w", pady=(5, 2))
        speed_combo = ttk.Combobox(
            perf_frame,
            textvariable=self.speed_mode_var,
            values=["Normal", "Rapide", "Très rapide"],
            state="readonly",
            width=15
        )
        speed_combo.grid(row=3, column=0, sticky="w", pady=2)
        
    def _create_output_options(self, parent):
        """Crée les options de sortie"""
        output_frame = ttk.LabelFrame(parent, text="Sortie", padding=3)
        output_frame.grid(row=3, column=0, sticky="ew", pady=(0, 5))
        
        # Auto-rename
        ttk.Checkbutton(
            output_frame,
            text="Auto-rename des fichiers",
            variable=self.auto_rename_var
        ).grid(row=0, column=0, sticky="w", pady=2)
        
    def _create_output_folder_options(self, parent):
        """Crée les options de dossier de sortie"""
        folder_frame = ttk.LabelFrame(parent, text="Destination des fichiers", padding=3)
        folder_frame.grid(row=4, column=0, sticky="ew", pady=(0, 5))
        
        # Mode de destination
        ttk.Label(folder_frame, text="Mode de destination:").grid(row=0, column=0, sticky="w", pady=2)
        destination_combo = ttk.Combobox(
            folder_frame,
            textvariable=self.destination_mode_var,
            values=["Dossier personnalisé", "Même dossier que source", "Bureau", "Documents"],
            state="readonly",
            width=20
        )
        destination_combo.grid(row=1, column=0, sticky="w", pady=2)
        destination_combo.bind("<<ComboboxSelected>>", self._on_destination_mode_change)
        
        # Dossier de sortie personnalisé
        self.custom_folder_frame = ttk.Frame(folder_frame)
        self.custom_folder_frame.grid(row=2, column=0, sticky="ew", pady=2)
        self.custom_folder_frame.columnconfigure(0, weight=1)
        self.custom_folder_frame.columnconfigure(1, weight=0)
        
        ttk.Label(self.custom_folder_frame, text="Dossier de sortie:").grid(row=0, column=0, sticky="w", pady=2)
        
        # Frame pour le chemin et le bouton
        path_frame = ttk.Frame(self.custom_folder_frame)
        path_frame.grid(row=1, column=0, sticky="ew", pady=2)
        path_frame.columnconfigure(0, weight=1)
        path_frame.columnconfigure(1, weight=0)
        
        # Champ de saisie du chemin
        self.output_path_entry = ttk.Entry(path_frame, textvariable=self.output_folder_var, state="readonly")
        self.output_path_entry.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        
        # Bouton de sélection
        ttk.Button(path_frame, text="Parcourir", command=self._browse_output_folder, width=10).grid(row=0, column=1)
        
        # Options supplémentaires
        options_frame = ttk.Frame(folder_frame)
        options_frame.grid(row=3, column=0, sticky="ew", pady=(5, 0))
        
        ttk.Checkbutton(
            options_frame,
            text="Créer des sous-dossiers par série",
            variable=self.create_subfolders_var
        ).grid(row=0, column=0, sticky="w", pady=2)
        
        ttk.Checkbutton(
            options_frame,
            text="Écraser les fichiers existants",
            variable=self.overwrite_existing_var
        ).grid(row=1, column=0, sticky="w", pady=2)
        
        # Initialiser avec le dernier chemin utilisé
        if hasattr(self.main_window, 'path_manager'):
            last_path = self.main_window.path_manager.get_last_output_path()
            self.output_folder_var.set(last_path)
            
    def _browse_output_folder(self):
        """Ouvre le dialogue de sélection du dossier de sortie"""
        from tkinter import filedialog
        folder = filedialog.askdirectory(
            title="Sélectionner le dossier de sortie",
            initialdir=self.main_window.path_manager.get_last_output_path()
        )
        if folder:
            self.main_window.path_manager.set_last_output_path(folder)
            self.output_folder_var.set(folder)
            
    def _on_options_canvas_configure(self, event):
        """Redimensionne la fenêtre du canvas des options"""
        self.options_canvas.itemconfig(self.options_canvas_window, width=event.width)
        
    def _on_options_mousewheel(self, event):
        """Gère le scroll avec la souris pour les options"""
        try:
            if event.num == 4:
                self.options_canvas.yview_scroll(-1, "units")
            elif event.num == 5:
                self.options_canvas.yview_scroll(1, "units")
            else:
                self.options_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        except Exception as e:
            # Fallback si le scroll ne fonctionne pas
            pass
            
    def _update_options_scroll(self):
        """Met à jour la région de scroll des options"""
        try:
            self.options_canvas.configure(scrollregion=self.options_canvas.bbox("all"))
        except Exception as e:
            pass
            
    def _on_destination_mode_change(self, event=None):
        """Appelé quand le mode de destination change"""
        mode = self.destination_mode_var.get()
        
        if mode == "Dossier personnalisé":
            self.custom_folder_frame.grid()
        else:
            self.custom_folder_frame.grid_remove()
            
        # Mettre à jour le chemin selon le mode
        if mode == "Même dossier que source":
            # Sera déterminé lors de la conversion
            self.output_folder_var.set("(Dossier source)")
        elif mode == "Bureau":
            desktop = Path.home() / "Desktop"
            self.output_folder_var.set(str(desktop))
        elif mode == "Documents":
            documents = Path.home() / "Documents"
            self.output_folder_var.set(str(documents))
        
    def _create_action_buttons(self, parent):
        """Crée les boutons d'action"""
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=5, column=0, sticky="ew", pady=(5, 0))
        
        # Configuration des colonnes pour la réactivité
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)
        
        # Boutons
        ttk.Button(
            button_frame,
            text="Aperçu",
            command=self._preview_files
        ).grid(row=0, column=0, padx=(0, 5), sticky="ew")
        
        ttk.Button(
            button_frame,
            text="Arrêter",
            command=self._stop_conversion
        ).grid(row=0, column=1, padx=(5, 0), sticky="ew")
        
    def _on_merge_option_change(self):
        """Appelé quand l'option de fusion change"""
        if self.merge_volumes_var.get():
            # Activer les options d'ordre
            pass
        else:
            # Désactiver les options d'ordre
            self.custom_order_var.set(False)
            
    def _on_order_change(self, event=None):
        """Appelé quand l'ordre de fusion change"""
        if self.merge_order_var.get() == "Personnalisé":
            self.custom_order_var.set(True)
            self._open_custom_order_dialog()
            
    def _on_custom_order_change(self):
        """Appelé quand l'option d'ordre personnalisé change"""
        if self.custom_order_var.get():
            self.merge_order_var.set("Personnalisé")
            self._open_custom_order_dialog()
            
    def _open_custom_order_dialog(self):
        """Ouvre le dialogue d'ordre personnalisé"""
        from .dialogs import CustomOrderDialog
        dialog = CustomOrderDialog(self.main_window)
        dialog.show()
        
    def _preview_files(self):
        """Affiche l'aperçu des fichiers"""
        selected_files = self.main_window.file_list.get_selected_files()
        if selected_files:
            from .dialogs import PreviewDialog
            dialog = PreviewDialog(self.main_window, selected_files)
            dialog.show()
        else:
            messagebox.showwarning("Attention", "Aucun fichier sélectionné pour l'aperçu")
            
    def _stop_conversion(self):
        """Arrête la conversion en cours"""
        if self.main_window.converting:
            self.main_window.converting = False
            self.main_window.log_message("Conversion arrêtée par l'utilisateur")
        else:
            messagebox.showinfo("Information", "Aucune conversion en cours")
            
    def get_options(self):
        """Récupère toutes les options actuelles"""
        return {
            'merge_volumes': self.merge_volumes_var.get(),
            'fetch_metadata': self.fetch_metadata_var.get(),
            'merge_order': self.merge_order_var.get(),
            'custom_order': self.custom_order_var.get(),
            'max_workers': self.max_workers_var.get(),
            'speed_mode': self.speed_mode_var.get(),
            'auto_rename': self.auto_rename_var.get(),
            'output_folder': self.output_folder_var.get(),
            'destination_mode': self.destination_mode_var.get(),
            'create_subfolders': self.create_subfolders_var.get(),
            'overwrite_existing': self.overwrite_existing_var.get()
        }
        
    def set_options(self, options):
        """Définit les options"""
        if 'merge_volumes' in options:
            self.merge_volumes_var.set(options['merge_volumes'])
        if 'fetch_metadata' in options:
            self.fetch_metadata_var.set(options['fetch_metadata'])
        if 'merge_order' in options:
            self.merge_order_var.set(options['merge_order'])
        if 'custom_order' in options:
            self.custom_order_var.set(options['custom_order'])
        if 'max_workers' in options:
            self.max_workers_var.set(options['max_workers'])
        if 'speed_mode' in options:
            self.speed_mode_var.set(options['speed_mode'])
        if 'auto_rename' in options:
            self.auto_rename_var.set(options['auto_rename']) 