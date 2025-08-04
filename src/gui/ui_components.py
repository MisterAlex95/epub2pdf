#!/usr/bin/env python3
"""
Module pour les composants UI réutilisables
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox

# Constantes pour les couleurs et styles
COLORS = {
    'primary': '#007bff',
    'success': '#28a745',
    'warning': '#ffc107',
    'danger': '#dc3545',
    'info': '#17a2b8',
    'light': '#f8f9fa',
    'dark': '#343a40',
    'gray': '#6c757d',
    'white': '#ffffff',
    'black': '#000000'
}

STATUS_MESSAGES = {
    'ready': 'Ready to convert',
    'scanning': 'Scanning for files...',
    'converting': 'Converting files...',
    'completed': 'Conversion completed',
    'error': 'Error occurred'
}

SHORTCUTS = {
    'scan': 'Ctrl+S',
    'convert': 'Ctrl+C',
    'clear': 'Ctrl+L',
    'browse_input': 'Ctrl+O',
    'browse_output': 'Ctrl+Shift+O',
    'exit': 'Ctrl+Q',
    'scan_files': 'Ctrl+Shift+S',
    'convert_all': 'Ctrl+Shift+C',
    'clear_all': 'Ctrl+Shift+L',
    'dry_run': 'Ctrl+D',
    'about': 'F1'
}

RESIZE_OPTIONS = ["", "A4", "A3", "A5", "HD", "FHD", "Custom"]

WINDOW_SIZE = "800x600"
MIN_WINDOW_SIZE = "600x400"
PADDING = 10
STATUS_ICONS = {
    'ready': '✅',
    'scanning': '🔍',
    'converting': '🔄',
    'completed': '✅',
    'error': '❌'
}


class UIComponents:
    """Composants d'interface utilisateur réutilisables"""
    
    @staticmethod
    def setup_window(root, title):
        """Configure la fenêtre principale"""
        root.title(title)
        root.geometry(WINDOW_SIZE)
        # Correction : parser correctement MIN_WINDOW_SIZE
        if isinstance(MIN_WINDOW_SIZE, str):
            min_width, min_height = map(int, MIN_WINDOW_SIZE.split('x'))
        elif isinstance(MIN_WINDOW_SIZE, (tuple, list)) and len(MIN_WINDOW_SIZE) == 2:
            min_width, min_height = MIN_WINDOW_SIZE
        else:
            min_width, min_height = 600, 400
        root.minsize(min_width, min_height)
        # Centrer la fenêtre
        root.update_idletasks()
        width = root.winfo_width()
        height = root.winfo_height()
        x = (root.winfo_screenwidth() // 2) - (width // 2)
        y = (root.winfo_screenheight() // 2) - (height // 2)
        root.geometry(f"{width}x{height}+{x}+{y}")
        
    @staticmethod
    def setup_theme():
        """Configure le thème de l'interface"""
        style = ttk.Style()
        
        # Essayer d'utiliser un thème moderne
        try:
            style.theme_use('clam')
        except:
            try:
                style.theme_use('vista')
            except:
                style.theme_use('default')
        
        # Configuration des styles
        style.configure('Title.TLabel', 
                       font=('Arial', 18, 'bold'), 
                       foreground=COLORS['primary'])
        style.configure('Subtitle.TLabel', 
                       font=('Arial', 10), 
                       foreground=COLORS['gray'])
        style.configure('Success.TLabel', 
                       foreground=COLORS['success'])
        style.configure('Warning.TLabel', 
                       foreground=COLORS['warning'])
        style.configure('Error.TLabel', 
                       foreground=COLORS['danger'])
        
        # Styles des boutons
        style.configure('Primary.TButton', 
                       background=COLORS['primary'], 
                       foreground=COLORS['white'],
                       font=('Arial', 9, 'bold'))
        style.configure('Success.TButton', 
                       background=COLORS['success'], 
                       foreground=COLORS['white'],
                       font=('Arial', 9, 'bold'))
        style.configure('Warning.TButton', 
                       background=COLORS['warning'], 
                       foreground=COLORS['dark'],
                       font=('Arial', 9, 'bold'))
        
        # Styles des frames
        style.configure('Card.TFrame', relief='solid', borderwidth=1)
        style.configure('Header.TFrame', background=COLORS['light'])
        
        return style
        
    @staticmethod
    def create_header_frame(parent):
        """Crée le frame d'en-tête"""
        header_frame = ttk.Frame(parent, style="Header.TFrame")
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        title_frame = ttk.Frame(header_frame)
        title_frame.pack(pady=8)
        
        title_label = ttk.Label(title_frame, 
                               text="📘 epub2pdf, cbr2pdf & cbz2pdf", 
                               style="Title.TLabel")
        title_label.pack()
        
        subtitle_label = ttk.Label(title_frame, 
                                  text="Unified PDF Converter", 
                                  style="Subtitle.TLabel")
        subtitle_label.pack()
        
        version_label = ttk.Label(title_frame, 
                                 text=f"Version 1.0.0", 
                                 style="Subtitle.TLabel")
        version_label.pack(pady=(2, 0))
        
        return header_frame
        
    @staticmethod
    def create_directory_frame(parent, input_var, output_var, browse_input_cmd, browse_output_cmd, scan_cmd):
        """Crée le frame des répertoires"""
        dir_frame = ttk.LabelFrame(parent, text="📁 Directories", padding="8")
        dir_frame.pack(fill=tk.X, pady=(0, 8))
        
        # Répertoire d'entrée
        input_frame = ttk.Frame(dir_frame)
        input_frame.pack(fill=tk.X, pady=4)
        
        ttk.Label(input_frame, text="📂 Input:").pack(side=tk.LEFT, padx=(0, 5))
        input_entry = ttk.Entry(input_frame, textvariable=input_var)
        input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        ttk.Button(input_frame, text="📁", command=browse_input_cmd, width=3).pack(side=tk.LEFT, padx=(0, 2))
        ttk.Button(input_frame, text="🔍", command=scan_cmd, width=3).pack(side=tk.LEFT)
        
        # Répertoire de sortie
        output_frame = ttk.Frame(dir_frame)
        output_frame.pack(fill=tk.X, pady=4)
        
        ttk.Label(output_frame, text="📁 Output:").pack(side=tk.LEFT, padx=(0, 5))
        output_entry = ttk.Entry(output_frame, textvariable=output_var)
        output_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        ttk.Button(output_frame, text="📁", command=browse_output_cmd, width=3).pack(side=tk.LEFT)
        
        return dir_frame
        
    @staticmethod
    def create_options_frame(parent, variables):
        """Crée le frame des options"""
        options_frame = ttk.LabelFrame(parent, text="⚙️ Options", padding="8")
        options_frame.pack(fill=tk.X, pady=(0, 8))
        
        options_grid = ttk.Frame(options_frame)
        options_grid.pack(fill=tk.X, pady=4)
        
        # Ligne 1 - Options de fichiers
        ttk.Checkbutton(options_grid, text="🔍 Subdirs",
                       variable=variables['recursive']).grid(row=0, column=0, sticky=tk.W, padx=(0, 15), pady=1)
        ttk.Checkbutton(options_grid, text="🔄 Overwrite",
                       variable=variables['force']).grid(row=0, column=1, sticky=tk.W, padx=(0, 15), pady=1)
        ttk.Checkbutton(options_grid, text="🧹 Clean",
                       variable=variables['clean_tmp']).grid(row=0, column=2, sticky=tk.W, padx=(0, 15), pady=1)
        ttk.Checkbutton(options_grid, text="📁 Open",
                       variable=variables['open_output']).grid(row=0, column=3, sticky=tk.W, pady=1)
        
        # Ligne 2 - Options de conversion
        ttk.Checkbutton(options_grid, text="⚡ Parallel",
                       variable=variables['parallel']).grid(row=1, column=0, sticky=tk.W, padx=(0, 15), pady=1)
        ttk.Checkbutton(options_grid, text="📝 Verbose",
                       variable=variables['verbose']).grid(row=1, column=1, sticky=tk.W, padx=(0, 15), pady=1)
        ttk.Checkbutton(options_grid, text="📊 Metadata",
                       variable=variables['edit_metadata']).grid(row=1, column=2, sticky=tk.W, padx=(0, 15), pady=1)
        ttk.Checkbutton(options_grid, text="🏷️ Auto-rename",
                       variable=variables['auto_rename']).grid(row=1, column=3, sticky=tk.W, pady=1)
        
        # Ligne 3 - Options d'image
        ttk.Checkbutton(options_grid, text="⚫ Grayscale",
                       variable=variables['grayscale']).grid(row=2, column=0, sticky=tk.W, padx=(0, 15), pady=1)
        ttk.Checkbutton(options_grid, text="📦 ZIP Output",
                       variable=variables['zip_output']).grid(row=2, column=1, sticky=tk.W, padx=(0, 15), pady=1)
        
        # Ligne 4 - Redimensionnement
        ttk.Label(options_grid, text="📏 Resize:").grid(row=3, column=0, sticky=tk.W, padx=(0, 5), pady=1)
        resize_combo = ttk.Combobox(options_grid, textvariable=variables['resize'], 
                                   values=RESIZE_OPTIONS, width=10, state="readonly")
        resize_combo.grid(row=3, column=1, sticky=tk.W, padx=(0, 5), pady=1)
        
        # Entry pour le redimensionnement personnalisé
        custom_resize_entry = ttk.Entry(options_grid, textvariable=variables['custom_resize'], 
                                       width=15, placeholder="e.g., 1920x1080")
        custom_resize_entry.grid(row=3, column=2, sticky=tk.W, padx=(0, 5), pady=1)
        custom_resize_entry.grid_remove()  # Caché par défaut
        
        # Ligne 5 - Workers (si parallel activé)
        ttk.Label(options_grid, text="👥 Workers:").grid(row=4, column=0, sticky=tk.W, padx=(0, 5), pady=1)
        workers_spin = ttk.Spinbox(options_grid, from_=1, to=8, width=5,
                                  textvariable=variables['max_workers'])
        workers_spin.grid(row=4, column=1, sticky=tk.W, padx=(0, 5), pady=1)
        
        # Ajout des champs de métadonnées personnalisées
        meta_frame = ttk.Frame(options_frame)
        meta_frame.pack(fill=tk.X, pady=(8, 0))
        
        def toggle_meta_fields(*_):
            if variables['edit_metadata'].get():
                meta_frame.pack(fill=tk.X, pady=(8, 0))
            else:
                meta_frame.pack_forget()
        variables['edit_metadata'].trace_add('write', toggle_meta_fields)
        # Titre par défaut
        ttk.Label(meta_frame, text="Titre par défaut:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        title_entry = ttk.Entry(meta_frame, textvariable=variables['custom_title'], width=30)
        title_entry.grid(row=0, column=1, sticky=tk.W, padx=(0, 10))
        # Auteur
        ttk.Label(meta_frame, text="Auteur:").grid(row=0, column=2, sticky=tk.W, padx=(0, 5))
        author_entry = ttk.Entry(meta_frame, textvariable=variables['custom_author'], width=20)
        author_entry.grid(row=0, column=3, sticky=tk.W, padx=(0, 10))
        # Sujet
        ttk.Label(meta_frame, text="Sujet:").grid(row=1, column=0, sticky=tk.W, padx=(0, 5))
        subject_entry = ttk.Entry(meta_frame, textvariable=variables['custom_subject'], width=20)
        subject_entry.grid(row=1, column=1, sticky=tk.W, padx=(0, 10))
        # Mots-clés
        ttk.Label(meta_frame, text="Mots-clés:").grid(row=1, column=2, sticky=tk.W, padx=(0, 5))
        keywords_entry = ttk.Entry(meta_frame, textvariable=variables['custom_keywords'], width=20)
        keywords_entry.grid(row=1, column=3, sticky=tk.W, padx=(0, 10))
        # Afficher/masquer au démarrage
        toggle_meta_fields()
        return options_frame, resize_combo, custom_resize_entry
        
    @staticmethod
    def create_buttons_frame(parent, convert_cmd, dry_run_cmd, clear_cmd, exit_cmd):
        """Crée le frame des boutons"""
        buttons_frame = ttk.Frame(parent)
        buttons_frame.pack(fill=tk.X, pady=(0, 8))
        
        ttk.Button(buttons_frame, text="🔄 Convert All", 
                  command=convert_cmd, style="Success.TButton").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(buttons_frame, text="🧪 Dry Run", 
                  command=dry_run_cmd, style="Warning.TButton").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(buttons_frame, text="🗑️ Clear", 
                  command=clear_cmd).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(buttons_frame, text="❌ Exit", 
                  command=exit_cmd).pack(side=tk.RIGHT)
        
        return buttons_frame
        
    @staticmethod
    def create_progress_frame(parent):
        """Crée le frame de progression"""
        progress_frame = ttk.Frame(parent)
        progress_frame.pack(fill=tk.X, pady=(0, 5))
        
        progress_bar = ttk.Progressbar(progress_frame, mode='determinate')
        progress_bar.pack(fill=tk.X, pady=2)
        
        progress_label = ttk.Label(progress_frame, text="Ready")
        progress_label.pack(anchor=tk.W)
        
        return progress_bar, progress_label
        
    @staticmethod
    def create_log_frame(parent):
        """Crée le frame de logs"""
        log_frame = ttk.LabelFrame(parent, text="📝 Log", padding="5")
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        log_text = scrolledtext.ScrolledText(
            log_frame, 
            height=8,
            background='#F8F9FA',
            foreground='#212529',
            insertbackground='#2E86AB'
        )
        log_text.pack(fill=tk.BOTH, expand=True)
        
        return log_text
        
    @staticmethod
    def create_status_bar(parent):
        """Crée la barre de statut"""
        status_frame = ttk.Frame(parent)
        status_frame.pack(fill=tk.X, pady=(5, 0))
        
        status_icon = ttk.Label(status_frame, text="✅")
        status_icon.pack(side=tk.LEFT, padx=(2, 2))
        
        status_var = tk.StringVar()
        status_var.set(STATUS_MESSAGES['ready'])
        status_bar = ttk.Label(status_frame, textvariable=status_var, 
                              relief=tk.SUNKEN, padding=(2, 1))
        status_bar.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        quick_info = ttk.Label(status_frame, text="Ctrl+O/F/R")
        quick_info.pack(side=tk.RIGHT, padx=(0, 2))
        
        return status_icon, status_var, status_bar
        
    @staticmethod
    def create_menu(root, browse_input_cmd, browse_output_cmd, scan_cmd, convert_cmd, dry_run_cmd, about_cmd, exit_cmd):
        """Crée le menu de l'application"""
        menubar = tk.Menu(root)
        root.config(menu=menubar)
        
        # Menu Fichier
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Browse Input Directory", command=browse_input_cmd, accelerator="Ctrl+O")
        file_menu.add_command(label="Browse Output Directory", command=browse_output_cmd, accelerator="Ctrl+S")
        file_menu.add_separator()
        file_menu.add_command(label="Scan All Files", command=scan_cmd, accelerator="Ctrl+F")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=exit_cmd, accelerator="Ctrl+Q")
        
        # Menu Convertir
        convert_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Convert", menu=convert_menu)
        convert_menu.add_command(label="Convert All", command=convert_cmd, accelerator="Ctrl+R")
        convert_menu.add_command(label="Dry Run", command=dry_run_cmd, accelerator="Ctrl+D")
        
        # Menu Aide
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=about_cmd, accelerator="F1")
        
        # Raccourcis clavier
        root.bind(SHORTCUTS['browse_input'], lambda e: browse_input_cmd())
        root.bind(SHORTCUTS['browse_output'], lambda e: browse_output_cmd())
        root.bind(SHORTCUTS['scan_files'], lambda e: scan_cmd())
        root.bind(SHORTCUTS['convert_all'], lambda e: convert_cmd())
        root.bind(SHORTCUTS['dry_run'], lambda e: dry_run_cmd())
        root.bind(SHORTCUTS['exit'], lambda e: exit_cmd())
        root.bind(SHORTCUTS['about'], lambda e: about_cmd())
        
        return menubar 