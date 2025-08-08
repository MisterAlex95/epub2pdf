"""
Gestionnaire de métadonnées utilisant l'API MyAnimeList et MangaDex
"""

import requests
import re
import logging
from pathlib import Path
from typing import Optional, Dict, Any
import subprocess
import json

class MetadataManager:
    """Gestionnaire de métadonnées pour enrichir les PDF avec les données MyAnimeList et MangaDex"""
    
    def __init__(self):
        # MyAnimeList API
        self.mal_base_url = "https://api.myanimelist.net/v2"
        self.mal_client_id = None
        
        # MangaDex API (publique, pas besoin de clé)
        self.mangadex_base_url = "https://api.mangadex.org"
        
        self.logger = logging.getLogger('epub2pdf')
        
    def set_mal_client_id(self, client_id: str):
        """Configure l'ID client MyAnimeList"""
        self.mal_client_id = client_id
        self.logger.info(f"Client ID MyAnimeList configuré: {client_id[:8]}...")
    
    def extract_manga_info_from_filename(self, filename: str) -> Dict[str, str]:
        """Extrait les informations manga du nom de fichier"""
        try:
            # Patterns courants pour les noms de manga
            patterns = [
                # Pattern: "Kingdom T01 - C001 à 008 [216p] (Yasuhisa HARA) [Scantrads].cbr"
                r'^(.+?)\s+T(\d+)\s*-\s*C(\d+)\s*à\s*(\d+)\s*\[(\d+)p\]\s*\(([^)]+)\)\s*\[([^\]]+)\]',
                # Pattern: "One Piece T01 Ch001-010.cbr"
                r'^(.+?)\s+T(\d+)\s*Ch(\d+)-(\d+)',
                # Pattern: "Naruto Vol.01 Ch.001-010.cbr"
                r'^(.+?)\s+Vol\.(\d+)\s*Ch\.(\d+)-(\d+)',
                # Pattern simple: "Kingdom T01.cbr"
                r'^(.+?)\s+T(\d+)',
                # Pattern: "Kingdom Vol.01.cbr"
                r'^(.+?)\s+Vol\.(\d+)',
            ]
            
            clean_filename = Path(filename).stem  # Sans extension
            
            for pattern in patterns:
                match = re.match(pattern, clean_filename)
                if match:
                    groups = match.groups()
                    if len(groups) >= 2:
                        return {
                            'title': groups[0].strip(),
                            'volume': groups[1],
                            'chapters': f"{groups[2]}-{groups[3]}" if len(groups) > 3 else None,
                            'pages': groups[4] if len(groups) > 4 else None,
                            'author': groups[5] if len(groups) > 5 else None,
                            'scan_group': groups[6] if len(groups) > 6 else None
                        }
            
            # Fallback: extraire juste le titre
            return {'title': clean_filename}
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'extraction des infos: {e}")
            return {'title': Path(filename).stem}
    
    def search_manga_on_mal(self, title: str) -> Optional[Dict[str, Any]]:
        """Recherche un manga sur MyAnimeList"""
        try:
            if not self.mal_client_id:
                self.logger.warning("Client ID MyAnimeList non configuré")
                return None
            
            headers = {
                'X-MAL-CLIENT-ID': self.mal_client_id
            }
            
            params = {
                'q': title,
                'limit': 5,
                'fields': 'id,title,main_picture,alternative_titles,synopsis,mean,rank,popularity,media_type,status,genres,authors{first_name,last_name},serialization{name}'
            }
            
            response = requests.get(
                f"{self.mal_base_url}/manga",
                headers=headers,
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('data') and len(data['data']) > 0:
                    # Retourner le premier résultat (le plus pertinent)
                    manga_info = data['data'][0]
                    self.logger.info(f"Manga trouvé sur MAL: {manga_info.get('title', 'Unknown')}")
                    return manga_info
                else:
                    self.logger.warning(f"Aucun manga trouvé pour: {title}")
                    return None
            else:
                self.logger.error(f"Erreur API MAL: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            self.logger.error(f"Erreur lors de la recherche MAL: {e}")
            return None
    
    def search_manga_on_mangadex(self, title: str) -> Optional[Dict[str, Any]]:
        """Recherche un manga sur MangaDex"""
        try:
            # Recherche par titre
            params = {
                'title': title,
                'limit': 5,
                'includes[]': ['author', 'artist', 'cover_art'],
                'contentRating[]': ['safe', 'suggestive', 'erotica', 'pornographic']
            }
            
            response = requests.get(
                f"{self.mangadex_base_url}/manga",
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('data') and len(data['data']) > 0:
                    # Retourner le premier résultat (le plus pertinent)
                    manga_info = data['data'][0]
                    self.logger.info(f"Manga trouvé sur MangaDex: {manga_info.get('attributes', {}).get('title', {}).get('en', 'Unknown')}")
                    return manga_info
                else:
                    self.logger.warning(f"Aucun manga trouvé sur MangaDex pour: {title}")
                    return None
            else:
                self.logger.error(f"Erreur API MangaDex: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            self.logger.error(f"Erreur lors de la recherche MangaDex: {e}")
            return None
    
    def get_manga_details_mangadex(self, manga_id: str) -> Optional[Dict[str, Any]]:
        """Récupère les détails complets d'un manga depuis MangaDex"""
        try:
            params = {
                'includes[]': ['author', 'artist', 'cover_art', 'manga'],
                'contentRating[]': ['safe', 'suggestive', 'erotica', 'pornographic']
            }
            
            response = requests.get(
                f"{self.mangadex_base_url}/manga/{manga_id}",
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                self.logger.error(f"Erreur lors de la récupération des détails MangaDex: {response.status_code}")
                return None
                
        except Exception as e:
            self.logger.error(f"Erreur lors de la récupération des détails MangaDex: {e}")
            return None
    
    def merge_manga_info(self, mal_info: Optional[Dict], mangadex_info: Optional[Dict]) -> Dict[str, Any]:
        """Fusionne les informations de MyAnimeList et MangaDex"""
        merged_info = {}
        
        try:
            # Informations de base
            if mal_info:
                merged_info['title'] = mal_info.get('title', '')
                merged_info['synopsis'] = mal_info.get('synopsis', '')
                merged_info['mean'] = mal_info.get('mean')
                merged_info['popularity'] = mal_info.get('popularity')
                merged_info['genres'] = mal_info.get('genres', [])
                merged_info['authors'] = mal_info.get('authors', [])
                merged_info['source'] = 'MyAnimeList'
            
            # Enrichir avec MangaDex si disponible
            if mangadex_info:
                attributes = mangadex_info.get('attributes', {})
                
                # Titre alternatif si pas de titre MAL
                if not merged_info.get('title') and attributes.get('title', {}).get('en'):
                    merged_info['title'] = attributes['title']['en']
                
                # Synopsis plus détaillé
                if attributes.get('description', {}).get('en') and not merged_info.get('synopsis'):
                    merged_info['synopsis'] = attributes['description']['en']
                
                # Informations supplémentaires
                merged_info['status'] = attributes.get('status')
                merged_info['year'] = attributes.get('year')
                merged_info['content_rating'] = attributes.get('contentRating')
                
                # Auteurs/Artistes
                if not merged_info.get('authors'):
                    authors = []
                    for rel in mangadex_info.get('relationships', []):
                        if rel.get('type') == 'author':
                            authors.append(rel.get('attributes', {}).get('name', ''))
                    if authors:
                        merged_info['authors'] = [{'first_name': author, 'last_name': ''} for author in authors]
                
                merged_info['source'] = 'MangaDex + MyAnimeList' if merged_info.get('source') else 'MangaDex'
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la fusion des informations: {e}")
        
        return merged_info
    
    def apply_pdf_metadata(self, pdf_path: str, manga_info: Dict[str, Any], file_info: Dict[str, str]) -> bool:
        """Applique les métadonnées au PDF"""
        try:
            if not Path(pdf_path).exists():
                self.logger.error(f"Fichier PDF non trouvé: {pdf_path}")
                return False
            
            # Vérifier si exiftool est disponible
            if not self._check_exiftool():
                self.logger.warning("exiftool non disponible, métadonnées non appliquées")
                return False
            
            # Préparer les métadonnées
            metadata = self._prepare_metadata(manga_info, file_info)
            
            # Construire la commande exiftool
            cmd = ['exiftool', '-overwrite_original']
            
            for key, value in metadata.items():
                if value:
                    cmd.extend([f'-{key}={value}'])
            
            cmd.append(pdf_path)
            
            # Exécuter exiftool
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                self.logger.info(f"Métadonnées appliquées avec succès: {pdf_path}")
                return True
            else:
                self.logger.error(f"Erreur exiftool: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"Erreur lors de l'application des métadonnées: {e}")
            return False
    
    def _prepare_metadata(self, manga_info: Dict[str, Any], file_info: Dict[str, str]) -> Dict[str, str]:
        """Prépare les métadonnées pour exiftool"""
        metadata = {}
        
        try:
            # Titre
            title = manga_info.get('title', file_info.get('title', ''))
            if title:
                metadata['Title'] = title
            
            # Auteur
            authors = manga_info.get('authors', [])
            if authors:
                author_names = []
                for author in authors:
                    if isinstance(author, dict):
                        first_name = author.get('first_name', '')
                        last_name = author.get('last_name', '')
                        if first_name or last_name:
                            author_names.append(f"{first_name} {last_name}".strip())
                    else:
                        author_names.append(str(author))
                
                if author_names:
                    metadata['Author'] = '; '.join(author_names)
            
            # Synopsis
            synopsis = manga_info.get('synopsis', '')
            if synopsis:
                # Limiter la longueur du synopsis
                if len(synopsis) > 500:
                    synopsis = synopsis[:497] + "..."
                metadata['Subject'] = synopsis
            
            # Genre
            genres = manga_info.get('genres', [])
            if genres:
                genre_names = []
                for genre in genres:
                    if isinstance(genre, dict):
                        genre_names.append(genre.get('name', ''))
                    else:
                        genre_names.append(str(genre))
                
                if genre_names:
                    metadata['Keywords'] = ', '.join(genre_names)
            
            # Informations du fichier
            if file_info.get('volume'):
                metadata['Keywords'] = (metadata.get('Keywords', '') + f", Volume {file_info['volume']}").strip(', ')
            
            if file_info.get('chapters'):
                metadata['Keywords'] = (metadata.get('Keywords', '') + f", Chapters {file_info['chapters']}").strip(', ')
            
            # Note moyenne
            mean = manga_info.get('mean')
            if mean:
                metadata['Keywords'] = (metadata.get('Keywords', '') + f", Rating {mean:.1f}/10").strip(', ')
            
            # Statut et année
            if manga_info.get('status'):
                metadata['Keywords'] = (metadata.get('Keywords', '') + f", Status: {manga_info['status']}").strip(', ')
            
            if manga_info.get('year'):
                metadata['Keywords'] = (metadata.get('Keywords', '') + f", Year: {manga_info['year']}").strip(', ')
            
            # Créateur
            metadata['Creator'] = 'epub2pdf with MyAnimeList + MangaDex APIs'
            
            # Source
            if file_info.get('scan_group'):
                metadata['Source'] = f"Scanned by {file_info['scan_group']}"
            
            # Date de création
            from datetime import datetime
            metadata['CreateDate'] = datetime.now().strftime('%Y:%m:%d %H:%M:%S')
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la préparation des métadonnées: {e}")
        
        return metadata
    
    def _check_exiftool(self) -> bool:
        """Vérifie si exiftool est disponible"""
        try:
            result = subprocess.run(['exiftool', '-ver'], capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except Exception:
            return False
    
    def enrich_pdf_metadata(self, pdf_path: str, original_filename: str) -> bool:
        """Enrichit les métadonnées d'un PDF avec les données MyAnimeList et MangaDex"""
        try:
            # Extraire les informations du nom de fichier
            file_info = self.extract_manga_info_from_filename(original_filename)
            title = file_info.get('title', '')
            
            # Rechercher sur les deux APIs
            mal_info = self.search_manga_on_mal(title)
            mangadex_info = self.search_manga_on_mangadex(title)
            
            # Fusionner les informations
            merged_info = self.merge_manga_info(mal_info, mangadex_info)
            
            if merged_info:
                # Appliquer les métadonnées
                return self.apply_pdf_metadata(pdf_path, merged_info, file_info)
            else:
                self.logger.warning(f"Aucune information trouvée pour: {original_filename}")
                return False
                
        except Exception as e:
            self.logger.error(f"Erreur lors de l'enrichissement des métadonnées: {e}")
            return False 