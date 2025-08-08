"""
Gestionnaire de chemins pour mémoriser les derniers chemins utilisés
"""

import json
import os
from pathlib import Path


class PathManager:
    """Gestionnaire de chemins pour mémoriser les derniers chemins utilisés"""
    
    def __init__(self, config_file="path_config.json"):
        self.config_file = Path(config_file)
        self.paths = self._load_paths()
        
    def _load_paths(self):
        """Charge les chemins sauvegardés"""
        default_paths = {
            'last_file_path': str(Path.home()),
            'last_folder_path': str(Path.home()),
            'last_output_path': str(Path.home())
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_paths = json.load(f)
                    # Fusionner avec les valeurs par défaut
                    default_paths.update(loaded_paths)
            except (json.JSONDecodeError, IOError):
                pass
                
        return default_paths
        
    def _save_paths(self):
        """Sauvegarde les chemins"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.paths, f, indent=2, ensure_ascii=False)
        except IOError:
            pass
            
    def get_last_file_path(self):
        """Récupère le dernier chemin de fichier utilisé"""
        path = Path(self.paths['last_file_path'])
        return str(path) if path.exists() else str(Path.home())
        
    def get_last_folder_path(self):
        """Récupère le dernier chemin de dossier utilisé"""
        path = Path(self.paths['last_folder_path'])
        return str(path) if path.exists() else str(Path.home())
        
    def get_last_output_path(self):
        """Récupère le dernier chemin de sortie utilisé"""
        path = Path(self.paths['last_output_path'])
        return str(path) if path.exists() else str(Path.home())
        
    def set_last_file_path(self, path):
        """Définit le dernier chemin de fichier utilisé"""
        if path and os.path.exists(path):
            self.paths['last_file_path'] = str(Path(path).parent)
            self._save_paths()
            
    def set_last_folder_path(self, path):
        """Définit le dernier chemin de dossier utilisé"""
        if path and os.path.exists(path):
            self.paths['last_folder_path'] = str(Path(path))
            self._save_paths()
            
    def set_last_output_path(self, path):
        """Définit le dernier chemin de sortie utilisé"""
        if path and os.path.exists(path):
            self.paths['last_output_path'] = str(Path(path))
            self._save_paths()
