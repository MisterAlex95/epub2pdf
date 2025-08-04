#!/usr/bin/env python3
"""
Interface graphique unifiée pour epub2pdf, cbr2pdf et cbz2pdf
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import json
from pathlib import Path
from core.config import VERSION, FILE_FORMATS, COLORS
from core.conversion_manager import ConversionManager
from core.settings_manager import SettingsManager
from gui.ui_components import UIComponents


class UnifiedGUI:
    """Interface unifiée pour la conversion de fichiers"""
    
    def __init__(self, root):
        """Initialise l'interface unifiée"""
        print("🏗️ Initialisation de l'interface unifiée...")
        self.root = root
        print("📐 Configuration de la fenêtre...")
        UIComponents.setup_window(root, f"epub2pdf, cbr2pdf & cbz2pdf - Unified Converter v{VERSION}")
        print("🎨 Configuration du thème...")
        UIComponents.setup_theme()
        
        # Initialisation des gestionnaires
        print("⚙️ Initialisation du gestionnaire de paramètres...")
        self.settings_manager = SettingsManager()
        
        # Initialisation des variables
        print("📝 Initialisation des variables...")
        self._init_variables()
        
        # Création des composants UI
        print("🔧 Création des composants UI...")
        self._init_ui_components()
        
        # Chargement des paramètres
        print("💾 Chargement des paramètres...")
        self._load_settings()
        
        # Configuration des événements
        self._setup_events()
        
        # Configuration des événements de fenêtre
        self._setup_window_events()
        
        # Affichage du message initial
        self._show_initial_message()
        
        print("✅ Interface unifiée initialisée avec succès")
        
        # Variables pour les fichiers
        self.all_files = []
        self.files_by_format = {'epub': [], 'cbr': [], 'cbz': []}
        
    def _init_variables(self):
        """Initialise les variables de l'interface"""
        # Variables de répertoires
        self.input_dir = tk.StringVar()
        self.output_dir = tk.StringVar()
        
        # Variables d'options
        self.recursive = tk.BooleanVar(value=False)
        self.force = tk.BooleanVar(value=False)
        self.grayscale = tk.BooleanVar(value=False)
        self.zip_output = tk.BooleanVar(value=False)
        self.clean_tmp = tk.BooleanVar(value=True)
        self.open_output = tk.BooleanVar(value=False)
        self.parallel = tk.BooleanVar(value=True)
        self.verbose = tk.BooleanVar(value=True)
        self.max_workers = tk.IntVar(value=2)
        
        # Variables de redimensionnement
        self.resize_var = tk.StringVar(value="")
        self.custom_resize_var = tk.StringVar(value="")
        
        # Variables de métadonnées
        self.edit_metadata = tk.BooleanVar(value=True)
        self.auto_rename = tk.BooleanVar(value=True)
        # Champs personnalisés pour les métadonnées
        self.custom_title = tk.StringVar()
        self.custom_author = tk.StringVar()
        self.custom_subject = tk.StringVar()
        self.custom_keywords = tk.StringVar()
        
        # Variables d'état
        self.is_converting = False
        self.should_stop = False
        self.status_var = tk.StringVar()
        self.status_icon = None
        
    def _init_ui_components(self):
        """Initialise les composants de l'interface"""
        # Header
        self.header = UIComponents.create_header_frame(self.root)
        
        # Main content frame
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Directory frame
        self.dir_frame = UIComponents.create_directory_frame(
            self.main_frame,
            self.input_dir,
            self.output_dir,
            self.browse_input,
            self.browse_output,
            self.scan_all_files
        )
        
        # Options frame
        self.options_frame, self.resize_combo, self.custom_resize_entry = UIComponents.create_options_frame(
            self.main_frame,
            {
                'recursive': self.recursive,
                'force': self.force,
                'grayscale': self.grayscale,
                'zip_output': self.zip_output,
                'clean_tmp': self.clean_tmp,
                'open_output': self.open_output,
                'parallel': self.parallel,
                'verbose': self.verbose,
                'max_workers': self.max_workers,
                'resize': self.resize_var,
                'custom_resize': self.custom_resize_var,
                'edit_metadata': self.edit_metadata,
                'auto_rename': self.auto_rename,
                'custom_title': self.custom_title,
                'custom_author': self.custom_author,
                'custom_subject': self.custom_subject,
                'custom_keywords': self.custom_keywords
            }
        )
        
        # Conversion frame (remplace les onglets)
        self._create_conversion_frame()
        
        # Status bar
        self.status_icon, self.status_var, self.status_bar = UIComponents.create_status_bar(self.main_frame)
        
        # Menu
        self.menubar = UIComponents.create_menu(
            self.root,
            self.browse_input,
            self.browse_output,
            self.scan_all_files,
            self.convert_all,
            self.dry_run,
            self.show_about,
            self.root.quit
        )
        
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
        # Lier le changement de resize à la fonction
        self.resize_combo.bind('<<ComboboxSelected>>', self.on_resize_change)
        
        # Configuration de la fermeture propre
        self.root.protocol("WM_DELETE_WINDOW", self.root.quit)
        
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
        self.status_icon.config(text=icon)
        self.status_var.set(message)
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
            'verbose': self.verbose.get(),
            'edit_metadata': self.edit_metadata.get(),
            'auto_rename': self.auto_rename.get(),
            'custom_title': self.custom_title.get(),
            'custom_author': self.custom_author.get(),
            'custom_subject': self.custom_subject.get(),
            'custom_keywords': self.custom_keywords.get()
        }
        
    def scan_all_files(self):
        """Scanne automatiquement tous les formats de fichiers dans le répertoire d'entrée"""
        if not self.input_dir.get():
            messagebox.showerror("Error", "Please select an input directory")
            return
            
        self.update_status("Scanning for files...", "🔍")
        self.update_conversion_status("Scanning for files...", "🔍")
        
        try:
            total_files = 0
            self.files_by_format = {'epub': [], 'cbr': [], 'cbz': []}
            
            input_path = Path(self.input_dir.get())
            
            # Scanner automatiquement pour tous les formats supportés
            supported_formats = ['epub', 'cbr', 'cbz']
            
            for format_key in supported_formats:
                if self.recursive.get():
                    pattern = f"**/*.{format_key}"
                else:
                    pattern = f"*.{format_key}"
                    
                for file_path in input_path.glob(pattern):
                    if file_path.is_file():
                        self.files_by_format[format_key].append(str(file_path))
                        total_files += 1
                        self.log_message(f"📁 Found {format_key.upper()}: {file_path.name}")
            
            # Mettre à jour l'interface
            self.all_files = []
            format_summary = []
            
            for format_key, files in self.files_by_format.items():
                if files:
                    format_summary.append(f"{len(files)} {format_key.upper()}")
                for file_path in files:
                    self.all_files.append((file_path, format_key))
            
            if total_files == 0:
                self.update_status("No files found", "⚠️")
                self.update_conversion_status("No files found", "⚠️")
                messagebox.showinfo("No Files", "No supported files (EPUB, CBR, CBZ) found in the selected directory. Try enabling 'Search subdirectories' or check the file extensions.")
            else:
                summary_text = f"Found {total_files} files: {', '.join(format_summary)}"
                self.update_status(summary_text, "✅")
                self.update_conversion_status(f"Found {total_files} files", "✅")
                self.update_file_count(total_files)
                self.log_message(f"📊 {summary_text}")
                
        except Exception as e:
            self.log_message(f"❌ Error scanning files: {e}")
            self.update_status("Error scanning files", "❌")
            
    def stop_conversion(self):
        """Arrête la conversion en cours"""
        self.should_stop = True
        self.is_converting = False
        self.stop_button.config(state=tk.DISABLED)
        self.convert_button.config(state=tk.NORMAL)
        self.update_conversion_status("Conversion stopped by user", "⏹️")
        self.log_message("⏹️ Conversion stopped by user")
    
    def convert_all(self):
        """Convertit tous les fichiers détectés"""
        if not self.all_files:
            messagebox.showwarning("No Files", "No files to convert. Please scan for files first.")
            return
        
        self.should_stop = False
        self.is_converting = True
        self.convert_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        
        # Lancer la conversion dans un thread séparé
        import threading
        conversion_thread = threading.Thread(target=self._run_conversion)
        conversion_thread.daemon = True
        conversion_thread.start()
    
    def _run_conversion(self):
        """Exécute la conversion dans un thread séparé"""
        try:
            options = self.get_conversion_options()
            total_files = len(self.all_files)
            successful = 0
            failed = 0
            
            self.update_conversion_status("Starting conversion...", "🔄")
            self.reset_progress()
            
            for i, (file_path, format_type) in enumerate(self.all_files):
                if self.should_stop:
                    break
                
                # Mettre à jour la progression
                progress = i + 1
                self.update_progress(progress, total_files, successful, failed)
                
                # Passer l'index i pour l'incrémentation
                if ConversionManager.convert_single_file(file_path, format_type, options, index=i):
                    successful += 1
                    self.log_message(f"✅ Successfully converted: {os.path.basename(file_path)}")
                else:
                    failed += 1
                    self.log_message(f"❌ Failed to convert: {os.path.basename(file_path)}")
                
                # Mettre à jour les statistiques
                stats_text = f"✅ {successful} successful, ❌ {failed} failed"
                self.stats_label.config(text=stats_text)
            
            # Finaliser
            if self.should_stop:
                self.conversion_completed("Conversion stopped", "⏹️")
            else:
                self.conversion_completed(f"Conversion completed: {successful} successful, {failed} failed", "✅")
                
        except Exception as e:
            self.log_message(f"❌ Error during conversion: {e}")
            self.conversion_completed("Conversion error", "❌")
        finally:
            self.is_converting = False
            self.should_stop = False
            
    def conversion_completed(self, message, icon="✅"):
        """Appelé quand la conversion est terminée"""
        self.update_conversion_status(message, icon)
        
        # Réactiver les boutons
        self.convert_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        
        if "Conversion stopped" in message:
            self.log_message("⏹️ Conversion stopped by user")
        elif "Conversion error" in message:
            self.log_message("❌ Conversion error")
        else:
            self.log_message(f"✅ {message}")
        
        # Ouvrir le répertoire de sortie si demandé
        if self.open_output.get() and "successful" in message:
            try:
                import subprocess
                output_dir = self.output_dir.get() or "./pdfs"
                subprocess.run(["open", output_dir])
            except Exception as e:
                self.log_message(f"❌ Error opening output directory: {e}")
                
    def dry_run(self):
        """Simule la conversion sans la faire réellement"""
        if not self.all_files:
            messagebox.showwarning("Warning", "No files to convert")
            return
            
        self.log_message(f"🧪 Simulation de conversion de {len(self.all_files)} fichiers...")
        self.update_status("Simulation en cours...", "🧪")
        self.update_conversion_status("Simulation en cours...", "🧪")
        
        # Simuler la conversion
        for file_path, format_key in self.all_files:
            self.log_message(f"📋 Simuler: {os.path.basename(file_path)} ({format_key.upper()})")
            
        self.log_message("✅ Simulation terminée")
        self.update_status("Simulation terminée", "✅")
        self.update_conversion_status("Simulation terminée", "✅")
        messagebox.showinfo("Dry Run", f"Would convert {len(self.all_files)} files")

    def update_conversion_status(self, message, icon="✅"):
        """Met à jour le statut de conversion"""
        self.conversion_status_label.config(text=f"{icon} {message}")
        
    def update_file_count(self, count):
        """Met à jour le compteur de fichiers avec un résumé des formats"""
        if count == 0:
            self.file_count_label.config(text="📁 No files selected", foreground='gray')
        else:
            # Créer un résumé des formats détectés
            format_summary = []
            for format_key, files in self.files_by_format.items():
                if files:
                    format_summary.append(f"{len(files)} {format_key.upper()}")
            
            summary_text = f"{count} files: {', '.join(format_summary)}"
            self.file_count_label.config(text=summary_text, foreground=COLORS['success'])
            
    def reset_progress(self):
        """Réinitialise la barre de progression"""
        self.progress_bar['value'] = 0
        self.progress_label.config(text="0%")
        self.stats_label.config(text="")
        
    def update_progress(self, current, total, completed=0, failed=0):
        """Met à jour la barre de progression avec des statistiques détaillées"""
        if total > 0:
            percentage = (current / total) * 100
            self.progress_bar['value'] = percentage
            self.progress_label.config(text=f"{percentage:.1f}%")
            
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
                        
            self.stats_label.config(text=stats_text)

    def _create_conversion_frame(self):
        """Crée le frame de conversion unifié"""
        self.conversion_frame = ttk.LabelFrame(self.main_frame, text="🔄 Auto-Detection & Conversion", padding="8")
        self.conversion_frame.pack(fill=tk.X, pady=(0, 8))
        
        # Frame pour les informations de fichiers
        info_frame = ttk.Frame(self.conversion_frame)
        info_frame.pack(fill=tk.X, pady=(0, 8))
        
        # Label pour le nombre de fichiers
        self.file_count_label = ttk.Label(info_frame, text="📁 No files selected", font=("TkDefaultFont", 9))
        self.file_count_label.pack(anchor=tk.W)
        
        # Label pour le statut de conversion
        self.conversion_status_label = ttk.Label(info_frame, text="Ready to convert", font=("TkDefaultFont", 9))
        self.conversion_status_label.pack(anchor=tk.W)
        
        # Frame pour la barre de progression
        progress_frame = ttk.Frame(self.conversion_frame)
        progress_frame.pack(fill=tk.X, pady=(0, 8))
        
        # Barre de progression
        self.progress_bar = ttk.Progressbar(progress_frame, mode='determinate', length=300)
        self.progress_bar.pack(fill=tk.X, pady=(0, 4))
        
        # Label de progression
        self.progress_label = ttk.Label(progress_frame, text="", font=("TkDefaultFont", 8))
        self.progress_label.pack(anchor=tk.W)
        
        # Label de statistiques
        self.stats_label = ttk.Label(progress_frame, text="", font=("TkDefaultFont", 8))
        self.stats_label.pack(anchor=tk.W)
        
        # Frame pour les boutons
        button_frame = ttk.Frame(self.conversion_frame)
        button_frame.pack(fill=tk.X, pady=(8, 0))
        
        # Bouton de conversion
        self.convert_button = ttk.Button(
            button_frame, 
            text="🔄 Convert All Detected Files",
            command=self.convert_all,
            style="Accent.TButton"
        )
        self.convert_button.pack(side=tk.LEFT, padx=(0, 8))
        
        # Bouton Stop
        self.stop_button = ttk.Button(
            button_frame,
            text="⏹️ Stop",
            command=self.stop_conversion,
            state=tk.DISABLED
        )
        self.stop_button.pack(side=tk.LEFT)


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