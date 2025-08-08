"""
Gestionnaire de configuration pour sauvegarder les options de l'interface
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any


class ConfigManager:
    """Gestionnaire de configuration pour sauvegarder les options"""
    
    def __init__(self, config_file="app_config.json"):
        self.config_file = Path(config_file)
        self.logger = logging.getLogger('epub2pdf')
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Charge la configuration depuis le fichier"""
        default_config = {
            # Options de fusion
            'merge_volumes': False,
            'fetch_metadata': True,
            'merge_order': 'Naturel',
            'custom_order': False,
            
            # Options de performance
            'max_workers': 5,
            'speed_mode': 'Normal',
            
            # Options de sortie
            'auto_rename': True,
            'output_folder': '',
            
            # Options de destination
            'destination_mode': 'Dossier personnalisé',
            'create_subfolders': False,
            'overwrite_existing': False,
            
            # Options d'interface
            'window_width': 1200,
            'window_height': 800,
            'options_panel_width': 300,
            'file_list_height': 10,
            'progress_panel_height': 8,
            
            # Options de filtres
            'last_search_term': '',
            'last_series_filter': '',
            'last_volume_filter': '',
            'last_chapter_filter': '',
            'last_sort_by': 'name',
            'last_sort_reverse': False
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    # Fusionner avec les valeurs par défaut
                    default_config.update(loaded_config)
                    self.logger.debug(f"Configuration chargée: {self.config_file}")
            except (json.JSONDecodeError, IOError) as e:
                self.logger.warning(f"Erreur chargement configuration: {e}")
        
        return default_config
    
    def _save_config(self):
        """Sauvegarde la configuration dans le fichier"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            self.logger.debug(f"Configuration sauvegardée: {self.config_file}")
        except IOError as e:
            self.logger.error(f"Erreur sauvegarde configuration: {e}")
    
    def get(self, key: str, default=None):
        """Récupère une valeur de configuration"""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any):
        """Définit une valeur de configuration et sauvegarde"""
        self.config[key] = value
        self._save_config()
    
    def update(self, config_dict: Dict[str, Any]):
        """Met à jour plusieurs valeurs de configuration et sauvegarde"""
        self.config.update(config_dict)
        self._save_config()
    
    def get_all(self) -> Dict[str, Any]:
        """Récupère toute la configuration"""
        return self.config.copy()
    
    def reset_to_defaults(self):
        """Remet la configuration aux valeurs par défaut"""
        self.config = self._load_config()
        self._save_config()
