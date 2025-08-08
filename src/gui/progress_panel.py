"""
Panneau de progression et logs
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import time
import logging


class ProgressPanel:
    """Panneau de progression et logs"""
    
    def __init__(self, main_window):
        self.main_window = main_window
        self.root = main_window.root
        
        # Variables de progression
        self.global_progress_var = tk.DoubleVar()
        self.current_file_var = tk.StringVar(value="Aucun fichier en cours")
        self.status_var = tk.StringVar(value="Prêt")
        
        # Composants UI
        self.global_progress_bar = None
        self.log_text = None
        
        # État de conversion
        self.converting = False
        
        # Configuration du handler de logging
        self._setup_logging_handler()
        
    def _setup_logging_handler(self):
        """Configure un handler de logging pour capturer tous les logs"""
        class TkinterLogHandler(logging.Handler):
            def __init__(self, progress_panel):
                super().__init__()
                self.progress_panel = progress_panel
                
            def emit(self, record):
                try:
                    # Formater le message
                    msg = self.format(record)
                    # Ajouter au panneau de progression
                    self.progress_panel.add_log(msg)
                except Exception:
                    pass
        
        # Créer le handler personnalisé
        self.log_handler = TkinterLogHandler(self)
        self.log_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        
        # Ajouter le handler au logger principal
        logger = logging.getLogger('epub2pdf')
        logger.addHandler(self.log_handler)
        
    def setup_ui(self, parent):
        """Configure l'interface du panneau de progression"""
        # Frame pour la progression
        progress_frame = ttk.LabelFrame(parent, text="Progression et logs", padding=5)
        progress_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(5, 0))
        
        # Configuration des colonnes pour la réactivité
        progress_frame.columnconfigure(0, weight=1)
        progress_frame.rowconfigure(1, weight=1)
        
        # Barre de progression globale
        self._create_global_progress(progress_frame)
        
        # Zone de logs
        self._create_log_area(progress_frame)
        
    def _create_global_progress(self, parent):
        """Crée la barre de progression globale"""
        progress_container = ttk.Frame(parent)
        progress_container.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        # Configuration des colonnes pour la réactivité
        progress_container.columnconfigure(1, weight=1)
        
        # Label du fichier en cours
        ttk.Label(progress_container, text="Fichier en cours:").grid(row=0, column=0, sticky="w", padx=(0, 10))
        ttk.Label(progress_container, textvariable=self.current_file_var).grid(row=0, column=1, sticky="w")
        
        # Barre de progression
        self.global_progress_bar = ttk.Progressbar(
            progress_container,
            variable=self.global_progress_var,
            maximum=100,
            length=400
        )
        self.global_progress_bar.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(5, 0))
        
        # Label de statut
        ttk.Label(progress_container, textvariable=self.status_var).grid(row=2, column=0, columnspan=2, sticky="w", pady=(5, 0))
        
    def _create_log_area(self, parent):
        """Crée la zone de logs"""
        log_frame = ttk.LabelFrame(parent, text="Logs", padding=5)
        log_frame.grid(row=1, column=0, sticky="nsew")
        
        # Configuration des colonnes et lignes pour la réactivité
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        # Zone de texte pour les logs
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            height=8,
            wrap=tk.WORD,
            state=tk.DISABLED,
            font=("Consolas", 9)
        )
        self.log_text.grid(row=0, column=0, sticky="nsew")
        
        # Configuration du thème sombre pour les logs
        self.log_text.configure(
            bg="#1e1e1e",
            fg="#ffffff",
            insertbackground="#ffffff",
            selectbackground="#4a9eff"
        )
        
    def start_conversion(self):
        """Démarre l'affichage de la conversion"""
        self.converting = True
        self.global_progress_var.set(0)
        self.current_file_var.set("Initialisation...")
        self.status_var.set("Conversion en cours...")
        self.add_log("Démarrage de la conversion...")
        
    def stop_conversion(self):
        """Arrête l'affichage de la conversion"""
        self.converting = False
        self.global_progress_var.set(100)
        self.current_file_var.set("Aucun fichier en cours")
        self.status_var.set("Conversion terminée")
        self.add_log("Conversion terminée.")
        
    def update_progress(self, progress):
        """Met à jour la progression globale"""
        if 0 <= progress <= 100:
            self.global_progress_var.set(progress)
            
    def update_current_file(self, filename):
        """Met à jour le fichier en cours"""
        self.current_file_var.set(filename)
        
    def update_status(self, status):
        """Met à jour le statut"""
        self.status_var.set(status)
        
    def add_log(self, message):
        """Ajoute un message au log"""
        # Éviter les doublons de timestamp si le message en contient déjà un
        if not message.startswith('[') and not message.startswith('20'):
            timestamp = time.strftime("%H:%M:%S")
            log_message = f"[{timestamp}] {message}\n"
        else:
            log_message = f"{message}\n"
        
        # Ajouter le message de manière thread-safe
        self.root.after(0, self._add_log_safe, log_message)
        
    def _add_log_safe(self, message):
        """Ajoute un message au log de manière thread-safe"""
        self.log_text.configure(state=tk.NORMAL)
        self.log_text.insert(tk.END, message)
        
        # Limiter le nombre de lignes pour éviter la surcharge mémoire
        lines = self.log_text.get(1.0, tk.END).split('\n')
        if len(lines) > 1000:  # Garder seulement les 1000 dernières lignes
            # Supprimer les premières lignes
            self.log_text.delete(1.0, f"{len(lines) - 1000}.0")
        
        self.log_text.see(tk.END)
        self.log_text.configure(state=tk.DISABLED)
        
    def clear_logs(self):
        """Efface tous les logs"""
        self.log_text.configure(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.configure(state=tk.DISABLED)
        
    def get_logs(self):
        """Récupère tous les logs"""
        return self.log_text.get(1.0, tk.END)
        
    def save_logs(self, filename):
        """Sauvegarde les logs dans un fichier"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(self.get_logs())
            self.add_log(f"Logs sauvegardés dans {filename}")
        except Exception as e:
            self.add_log(f"Erreur lors de la sauvegarde des logs: {e}")
            
    def update_file_progress(self, filename, progress, message=""):
        """Met à jour la progression d'un fichier spécifique"""
        if self.converting:
            self.update_current_file(filename)
            self.update_progress(progress)
            
            # Mettre à jour le statut
            if progress == 0:
                self.update_status("Démarrage...")
            elif progress < 50:
                self.update_status("Extraction...")
            elif progress < 80:
                self.update_status("Conversion...")
            elif progress < 100:
                self.update_status("Finalisation...")
            else:
                self.update_status("Terminé")
                
    def show_error(self, error_message):
        """Affiche une erreur dans les logs"""
        self.add_log(f"ERREUR: {error_message}")
        self.update_status("Erreur")
        
    def show_warning(self, warning_message):
        """Affiche un avertissement dans les logs"""
        self.add_log(f"ATTENTION: {warning_message}")
        
    def show_success(self, success_message):
        """Affiche un message de succès dans les logs"""
        self.add_log(f"SUCCÈS: {success_message}")
        
    def start_periodic_update(self):
        """Démarre les mises à jour périodiques"""
        if self.converting:
            # Mettre à jour la progression toutes les 100ms
            self.root.after(100, self.start_periodic_update)
            
    def stop_periodic_update(self):
        """Arrête les mises à jour périodiques"""
        self.converting = False 