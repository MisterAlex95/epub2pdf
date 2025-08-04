#!/usr/bin/env python3
"""
Module pour gérer les paramètres et la persistance
"""

import json
from pathlib import Path
from core.config import DEFAULT_SETTINGS


class SettingsManager:
    """Gère les paramètres de l'application"""
    
    def __init__(self, settings_file=None):
        """
        Initialise le gestionnaire de paramètres
        
        Args:
            settings_file: Chemin du fichier de paramètres
        """
        if settings_file is None:
            settings_file = Path.home() / ".epub2pdf_settings.json"
        self.settings_file = Path(settings_file)
        
    def load_settings(self):
        """
        Charge les paramètres depuis le fichier
        
        Returns:
            dict: Paramètres chargés
        """
        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r') as f:
                    settings = json.load(f)
                    
                # Fusionner avec les paramètres par défaut
                merged_settings = DEFAULT_SETTINGS.copy()
                merged_settings.update(settings)
                return merged_settings
                
        except Exception as e:
            print(f"Error loading settings: {e}")
            
        return DEFAULT_SETTINGS.copy()
        
    def save_settings(self, settings):
        """
        Sauvegarde les paramètres dans le fichier
        
        Args:
            settings: Dictionnaire des paramètres à sauvegarder
        """
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(settings, f, indent=2)
                
        except Exception as e:
            print(f"Error saving settings: {e}")
            
    def get_setting(self, key, default=None):
        """
        Récupère un paramètre spécifique
        
        Args:
            key: Clé du paramètre
            default: Valeur par défaut si non trouvé
            
        Returns:
            Valeur du paramètre
        """
        settings = self.load_settings()
        return settings.get(key, default)
        
    def set_setting(self, key, value):
        """
        Définit un paramètre spécifique
        
        Args:
            key: Clé du paramètre
            value: Valeur à définir
        """
        settings = self.load_settings()
        settings[key] = value
        self.save_settings(settings)
        
    def reset_settings(self):
        """Réinitialise les paramètres aux valeurs par défaut"""
        self.save_settings(DEFAULT_SETTINGS)
        
    def get_settings_file_path(self):
        """Retourne le chemin du fichier de paramètres"""
        return str(self.settings_file) 