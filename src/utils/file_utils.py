"""
Utilitaires pour la gestion de fichiers
"""

from pathlib import Path


def format_file_size(size_bytes):
    """Formate la taille en bytes en format lisible"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


def get_file_info(file_path):
    """Récupère les informations d'un fichier"""
    path = Path(file_path)
    return {
        'path': str(path),
        'name': path.name,
        'type': path.suffix.lower(),
        'size': format_file_size(path.stat().st_size),
        'pages': "?",  # Sera mis à jour par le file_manager
        'status': 'En attente',
        'progress': 0
    }


def open_file_with_default_app(file_path):
    """Ouvre un fichier avec l'application par défaut"""
    import subprocess
    import platform
    
    try:
        if platform.system() == "Darwin":  # macOS
            subprocess.call(('open', file_path))
        elif platform.system() == "Windows":
            subprocess.call(('start', file_path), shell=True)
        else:  # Linux
            subprocess.call(('xdg-open', file_path))
        return True
    except Exception as e:
        return False
