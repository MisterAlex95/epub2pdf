#!/usr/bin/env python3
"""
Module pour les filtres et la recherche de fichiers
"""

import re
from pathlib import Path
from datetime import datetime, timedelta


class FileFilter:
    """Gestionnaire de filtres pour les fichiers"""
    
    def __init__(self):
        self.filters = {
            'name': '',
            'size_min': 0,
            'size_max': float('inf'),
            'date_min': None,
            'date_max': None,
            'extension': [],
            'volume': None,
            'chapter': None,
            'series': ''
        }
        
    def set_filter(self, filter_type, value):
        """Définit un filtre"""
        if filter_type in self.filters:
            self.filters[filter_type] = value
            
    def clear_filters(self):
        """Efface tous les filtres"""
        self.filters = {
            'name': '',
            'size_min': 0,
            'size_max': float('inf'),
            'date_min': None,
            'date_max': None,
            'extension': [],
            'volume': None,
            'chapter': None,
            'series': ''
        }
        
    def apply_filters(self, files):
        """
        Applique les filtres à une liste de fichiers
        
        Args:
            files: Liste de chemins de fichiers
            
        Returns:
            list: Fichiers filtrés
        """
        filtered_files = []
        
        for file_path in files:
            if self._matches_filters(file_path):
                filtered_files.append(file_path)
                
        return filtered_files
        
    def _matches_filters(self, file_path):
        """Vérifie si un fichier correspond aux filtres"""
        try:
            path = Path(file_path)
            
            # Filtre par nom
            if self.filters['name']:
                if self.filters['name'].lower() not in path.name.lower():
                    return False
                    
            # Filtre par taille
            try:
                size = path.stat().st_size
                if size < self.filters['size_min'] or size > self.filters['size_max']:
                    return False
            except:
                return False
                
            # Filtre par date
            try:
                mtime = path.stat().st_mtime
                file_date = datetime.fromtimestamp(mtime)
                
                if self.filters['date_min'] and file_date < self.filters['date_min']:
                    return False
                if self.filters['date_max'] and file_date > self.filters['date_max']:
                    return False
            except:
                pass
                
            # Filtre par extension
            if self.filters['extension']:
                if path.suffix.lower() not in [ext.lower() for ext in self.filters['extension']]:
                    return False
                    
            # Filtres spécifiques aux mangas
            if self.filters['volume'] or self.filters['chapter'] or self.filters['series']:
                if not self._matches_manga_filters(path.name):
                    return False
                    
            return True
            
        except Exception as e:
            print(f"Erreur lors du filtrage de {file_path}: {e}")
            return False
            
    def _matches_manga_filters(self, filename):
        """Vérifie les filtres spécifiques aux mangas"""
        filename_lower = filename.lower()
        
        # Filtre par série
        if self.filters['series']:
            if self.filters['series'].lower() not in filename_lower:
                return False
                
        # Filtre par volume
        if self.filters['volume']:
            volume_pattern = rf'vol\.{self.filters["volume"]}\b'
            if not re.search(volume_pattern, filename_lower):
                return False
                
        # Filtre par chapitre
        if self.filters['chapter']:
            chapter_pattern = rf'ch\.{self.filters["chapter"]}\b'
            if not re.search(chapter_pattern, filename_lower):
                return False
                
        return True


class FileSorter:
    """Gestionnaire de tri pour les fichiers"""
    
    @staticmethod
    def sort_files(files, sort_by='name', reverse=False):
        """
        Trie une liste de fichiers
        
        Args:
            files: Liste de chemins de fichiers
            sort_by: Critère de tri ('name', 'size', 'date', 'volume', 'chapter')
            reverse: Ordre décroissant si True
            
        Returns:
            list: Fichiers triés
        """
        if sort_by == 'name':
            return sorted(files, key=lambda x: Path(x).name.lower(), reverse=reverse)
        elif sort_by == 'size':
            return sorted(files, key=lambda x: Path(x).stat().st_size, reverse=reverse)
        elif sort_by == 'date':
            return sorted(files, key=lambda x: Path(x).stat().st_mtime, reverse=reverse)
        elif sort_by == 'volume':
            return FileSorter._sort_by_volume(files, reverse)
        elif sort_by == 'chapter':
            return FileSorter._sort_by_chapter(files, reverse)
        else:
            return files
            
    @staticmethod
    def _sort_by_volume(files, reverse=False):
        """Trie par numéro de volume"""
        def extract_volume(filename):
            match = re.search(r'vol\.(\d+)', filename.lower())
            if match:
                return int(match.group(1))
            return 0
            
        return sorted(files, key=lambda x: extract_volume(Path(x).name), reverse=reverse)
        
    @staticmethod
    def _sort_by_chapter(files, reverse=False):
        """Trie par numéro de chapitre"""
        def extract_chapter(filename):
            match = re.search(r'ch\.(\d+)', filename.lower())
            if match:
                return int(match.group(1))
            return 0
            
        return sorted(files, key=lambda x: extract_chapter(Path(x).name), reverse=reverse)


class SearchEngine:
    """Moteur de recherche pour les fichiers"""
    
    def __init__(self):
        self.search_index = {}
        
    def build_index(self, files):
        """Construit un index de recherche"""
        self.search_index.clear()
        
        for file_path in files:
            path = Path(file_path)
            filename = path.name.lower()
            
            # Indexer par mots-clés
            words = re.findall(r'\w+', filename)
            for word in words:
                if word not in self.search_index:
                    self.search_index[word] = []
                self.search_index[word].append(file_path)
                
    def search(self, query, files=None):
        """
        Recherche dans les fichiers
        
        Args:
            query: Terme de recherche
            files: Liste de fichiers à rechercher (optionnel)
            
        Returns:
            list: Fichiers correspondants
        """
        if not query:
            return files or []
            
        query_lower = query.lower()
        results = set()
        
        # Si on a un index, l'utiliser
        if self.search_index:
            query_words = re.findall(r'\w+', query_lower)
            for word in query_words:
                if word in self.search_index:
                    results.update(self.search_index[word])
        else:
            # Recherche directe
            search_files = files or []
            for file_path in search_files:
                if query_lower in Path(file_path).name.lower():
                    results.add(file_path)
                    
        return list(results)
        
    def search_advanced(self, query, files=None):
        """
        Recherche avancée avec expressions régulières
        
        Args:
            query: Expression de recherche
            files: Liste de fichiers à rechercher
            
        Returns:
            list: Fichiers correspondants
        """
        if not query:
            return files or []
            
        results = []
        search_files = files or []
        
        try:
            pattern = re.compile(query, re.IGNORECASE)
            for file_path in search_files:
                if pattern.search(Path(file_path).name):
                    results.append(file_path)
        except re.error:
            # Si l'expression régulière est invalide, faire une recherche simple
            return self.search(query, files)
            
        return results 