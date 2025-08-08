"""
Interface principale de l'application
Point d'entrée pour l'interface utilisateur
"""

import tkinter as tk
from tkinter import ttk, messagebox
import logging
import threading
from pathlib import Path

from src.gui.main_window import MainWindow
from src.core.file_manager import FileManager


class ConverterInterface:
    """Interface principale de l'application de conversion"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Convertisseur EPUB/CBR/CBZ vers PDF")
        self.root.geometry("1200x800")
        
        # Configuration du logging
        self._setup_logging()
        
        # Initialisation des composants
        self.main_window = MainWindow(root)
        
        # Configuration de l'interface
        self._setup_interface()
        
        # Événements
        self._setup_events()
        
        logging.info("Interface initialisée avec succès")
        
    def _setup_logging(self):
        """Configure le système de logging"""
        # Créer le dossier logs s'il n'existe pas
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # Configuration du logging principal
        logger = logging.getLogger('epub2pdf')
        logger.setLevel(logging.INFO)
        
        # Éviter les handlers dupliqués
        if not logger.handlers:
            # Handler pour fichier
            file_handler = logging.FileHandler(log_dir / "app.log")
            file_handler.setLevel(logging.INFO)
            
            # Handler pour console
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            
            # Format
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)
            
            # Ajouter les handlers
            logger.addHandler(file_handler)
            logger.addHandler(console_handler)
        
    def _setup_interface(self):
        """Configure l'interface principale"""
        # L'interface est déjà configurée dans MainWindow
        pass
        
    def _setup_events(self):
        """Configure les événements de l'application"""
        # Événement de fermeture
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        # Raccourcis clavier globaux
        self.root.bind('<Control-q>', self._on_closing)
        self.root.bind('<F1>', self._show_help)
        
    def _on_closing(self, event=None):
        """Gère la fermeture de l'application"""
        if self.main_window.converting:
            result = messagebox.askyesno(
                "Conversion en cours",
                "Une conversion est en cours. Voulez-vous vraiment quitter ?"
            )
            if not result:
                return
                
        logging.info("Fermeture de l'application")
        
        # Nettoyer les fichiers temporaires
        try:
            self.main_window.cleanup_on_exit()
        except Exception as e:
            logging.error(f"Erreur lors du nettoyage: {e}")
            
        self.root.quit()
        
    def _show_help(self, event=None):
        """Affiche l'aide"""
        help_text = """
Raccourcis clavier:
- Ctrl+O : Ajouter des fichiers
- Ctrl+D : Ajouter un dossier
- Ctrl+R : Scanner les fichiers
- Ctrl+C : Convertir la sélection
- Ctrl+A : Convertir tout
- Ctrl+Q : Quitter
- F1 : Afficher cette aide

Fonctionnalités:
- Conversion EPUB/CBR/CBZ vers PDF
- Fusion en un seul fichier
- Récupération de métadonnées
- Ordre personnalisé
- Conversion parallèle
- Aperçu des fichiers
        """
        
        help_dialog = tk.Toplevel(self.root)
        help_dialog.title("Aide")
        help_dialog.geometry("500x400")
        help_dialog.transient(self.root)
        help_dialog.grab_set()
        
        # Centrer le dialogue
        help_dialog.update_idletasks()
        x = (help_dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (help_dialog.winfo_screenheight() // 2) - (400 // 2)
        help_dialog.geometry(f"500x400+{x}+{y}")
        
        # Contenu de l'aide
        text_widget = tk.Text(help_dialog, wrap=tk.WORD, padx=20, pady=20)
        text_widget.pack(fill=tk.BOTH, expand=True)
        text_widget.insert(tk.END, help_text)
        text_widget.configure(state=tk.DISABLED)
        
        # Bouton fermer
        ttk.Button(help_dialog, text="Fermer", command=help_dialog.destroy).pack(pady=10)
        
    def run(self):
        """Lance l'application"""
        try:
            logging.info("Démarrage de l'application")
            self.root.mainloop()
        except Exception as e:
            logging.error(f"Erreur lors de l'exécution: {e}")
            messagebox.showerror("Erreur", f"Erreur lors de l'exécution: {e}")
        finally:
            logging.info("Application fermée")
            
    def get_file_manager(self):
        """Récupère le gestionnaire de fichiers"""
        return self.main_window.file_manager
        
    def get_file_list(self):
        """Récupère la liste des fichiers"""
        return self.main_window.file_list
        
    def get_options_panel(self):
        """Récupère le panneau d'options"""
        return self.main_window.options_panel
        
    def get_progress_panel(self):
        """Récupère le panneau de progression"""
        return self.main_window.progress_panel


def create_interface(root):
    """Crée et retourne l'interface principale"""
    return ConverterInterface(root)


if __name__ == "__main__":
    # Test de l'interface
    root = tk.Tk()
    interface = create_interface(root)
    interface.run() 