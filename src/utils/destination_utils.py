"""
Utilitaires pour la gestion de la destination des fichiers
"""

from pathlib import Path
import logging


def get_output_directory(source_file: str, options: dict) -> Path:
    """Détermine le dossier de destination selon les options"""
    try:
        mode = options.get('destination_mode', 'Dossier personnalisé')
        source_path = Path(source_file)
        
        if mode == "Même dossier que source":
            # Même dossier que le fichier source
            return source_path.parent
            
        elif mode == "Bureau":
            # Dossier Bureau
            return Path.home() / "Desktop"
            
        elif mode == "Documents":
            # Dossier Documents
            return Path.home() / "Documents"
            
        else:  # "Dossier personnalisé"
            # Dossier personnalisé spécifié
            custom_path = options.get('output_folder', '')
            if custom_path and custom_path != "(Dossier source)":
                return Path(custom_path)
            else:
                # Essayer de charger depuis path_config.json
                try:
                    import json
                    config_file = Path("path_config.json")
                    if config_file.exists():
                        with open(config_file, 'r', encoding='utf-8') as f:
                            path_config = json.load(f)
                            last_output_path = path_config.get('last_output_path', '')
                            if last_output_path and Path(last_output_path).exists():
                                return Path(last_output_path)
                except Exception as e:
                    logging.warning(f"Erreur chargement path_config.json: {e}")
                
                # Fallback vers le dossier source
                return source_path.parent
                
    except Exception as e:
        logging.error(f"Erreur détermination dossier de destination: {e}")
        # Fallback vers le dossier source
        return Path(source_file).parent


def get_output_filename(source_file: str, options: dict) -> str:
    """Détermine le nom du fichier de sortie"""
    try:
        source_path = Path(source_file)
        auto_rename = options.get('auto_rename', True)
        
        if auto_rename:
            # Générer un nom basé sur le nom original
            base_name = source_path.stem
            return f"{base_name}.pdf"
        else:
            # Garder le nom original
            return source_path.name.replace(source_path.suffix, '.pdf')
            
    except Exception as e:
        logging.error(f"Erreur détermination nom fichier: {e}")
        return f"{Path(source_file).stem}.pdf"


def create_subfolder_if_needed(output_dir: Path, source_file: str, options: dict) -> Path:
    """Crée un sous-dossier si nécessaire"""
    try:
        create_subfolders = options.get('create_subfolders', False)
        
        if not create_subfolders:
            return output_dir
            
        # Extraire le nom de la série du nom de fichier
        source_name = Path(source_file).stem
        
        # Chercher des patterns de série dans le nom
        import re
        
        # Patterns pour détecter les séries
        patterns = [
            r'^([^_]+)',  # Tout avant le premier underscore
            r'^([^-]+)',  # Tout avant le premier tiret
            r'([A-Za-z]+)',  # Premier groupe de lettres
        ]
        
        series_name = None
        for pattern in patterns:
            match = re.search(pattern, source_name)
            if match:
                series_name = match.group(1).strip()
                break
                
        if series_name:
            # Créer le sous-dossier
            subfolder = output_dir / series_name
            subfolder.mkdir(exist_ok=True)
            return subfolder
        else:
            return output_dir
            
    except Exception as e:
        logging.error(f"Erreur création sous-dossier: {e}")
        return output_dir


def get_final_output_path(source_file: str, options: dict) -> Path:
    """Détermine le chemin final de sortie complet"""
    try:
        # Obtenir le dossier de destination
        output_dir = get_output_directory(source_file, options)
        
        # Créer un sous-dossier si nécessaire
        final_dir = create_subfolder_if_needed(output_dir, source_file, options)
        
        # Obtenir le nom du fichier
        filename = get_output_filename(source_file, options)
        
        # Créer le dossier de destination s'il n'existe pas
        final_dir.mkdir(parents=True, exist_ok=True)
        
        # Chemin final
        final_path = final_dir / filename
        
        # Gérer l'écrasement
        overwrite = options.get('overwrite_existing', False)
        if not overwrite and final_path.exists():
            # Ajouter un suffixe numérique
            counter = 1
            while final_path.exists():
                stem = final_path.stem
                suffix = final_path.suffix
                final_path = final_dir / f"{stem}_{counter}{suffix}"
                counter += 1
                
        return final_path
        
    except Exception as e:
        logging.error(f"Erreur détermination chemin final: {e}")
        # Fallback
        source_path = Path(source_file)
        return source_path.parent / f"{source_path.stem}.pdf"
