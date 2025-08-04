#!/usr/bin/env python3
"""
Module pour gérer les métadonnées PDF et le renommage automatique
"""

import re
import os
import subprocess
from pathlib import Path
from core.config import RENAME_PATTERNS, METADATA_TEMPLATES


class MetadataManager:
    """Gestionnaire des métadonnées PDF et du renommage automatique"""
    
    @staticmethod
    def extract_title_info(filename, format_type):
        """
        Extrait les informations de titre à partir du nom de fichier
        
        Args:
            filename: Nom du fichier
            format_type: Type de format ('manga', 'comic', 'epub')
            
        Returns:
            dict: Informations extraites (title, volume, chapter, etc.)
        """
        # Supprimer l'extension
        name_without_ext = Path(filename).stem
        
        # Essayer les patterns de renommage
        patterns = RENAME_PATTERNS.get(format_type, [])
        
        for pattern in patterns:
            match = re.match(pattern, name_without_ext)
            if match:
                groups = match.groups()
                if len(groups) >= 2:
                    title = groups[0].strip()
                    if len(groups) >= 3:
                        # Format avec volume et chapitre
                        return {
                            'title': title,
                            'volume': groups[1],
                            'chapter': groups[2],
                            'original_name': name_without_ext
                        }
                    else:
                        # Format simple avec numéro
                        return {
                            'title': title,
                            'volume': groups[1],
                            'original_name': name_without_ext
                        }
        
        # Si aucun pattern ne correspond, retourner le nom original
        return {
            'title': name_without_ext,
            'original_name': name_without_ext
        }
    
    @staticmethod
    def generate_clean_filename(info, format_type):
        """
        Génère un nom de fichier propre basé sur les informations extraites
        
        Args:
            info: Informations extraites du nom de fichier
            format_type: Type de format
            
        Returns:
            str: Nom de fichier propre
        """
        title = info.get('title', '').replace('_', ' ').strip()
        volume = info.get('volume', '')
        chapter = info.get('chapter', '')
        
        # Nettoyer le titre
        title = re.sub(r'[^\w\s-]', '', title).strip()
        
        if volume and chapter:
            return f"{title} - Vol.{volume} Ch.{chapter}"
        elif volume:
            return f"{title} - Vol.{volume}"
        else:
            return title
    
    @staticmethod
    def edit_pdf_metadata(pdf_path, info, format_type, options=None, index=None):
        """
        Édite les métadonnées d'un fichier PDF
        Args:
            pdf_path: Chemin du fichier PDF
            info: Informations extraites
            format_type: Type de format
            options: Dictionnaire d'options (pour custom_title, etc.)
            index: Numéro d'incrémentation (pour le titre)
        Returns:
            bool: True si succès, False sinon
        """
        try:
            template = METADATA_TEMPLATES.get(format_type, {})
            # Prendre le titre custom si fourni
            title = info.get('title', '').replace('_', ' ').strip()
            if options:
                if options.get('custom_title'):
                    base_title = options['custom_title']
                    if index is not None:
                        title = f"{base_title} {index+1}"
                    else:
                        title = base_title
                if options.get('custom_author'):
                    template['creator'] = options['custom_author']
                if options.get('custom_subject'):
                    template['subject'] = options['custom_subject']
                if options.get('custom_keywords'):
                    template['keywords'] = options['custom_keywords']
            # Préparer les métadonnées
            metadata = {
                'Title': title,
                'Author': template.get('creator', 'epub2pdf'),
                'Subject': template.get('subject', 'Document'),
                'Keywords': template.get('keywords', 'pdf'),
                'Producer': template.get('producer', 'epub2pdf')
            }
            # Utiliser exiftool pour éditer les métadonnées
            cmd = ['exiftool', '-overwrite_original']
            for key, value in metadata.items():
                cmd.extend([f'-{key}={value}'])
            cmd.append(str(pdf_path))
            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.returncode == 0
        except Exception as e:
            print(f"❌ Error editing PDF metadata: {e}")
            return False

    @staticmethod
    def rename_file_with_metadata(file_path, format_type, options=None, index=None):
        """
        Renomme un fichier avec un nom propre basé sur les métadonnées
        Args:
            file_path: Chemin du fichier
            format_type: Type de format
            options: Dictionnaire d'options (pour custom_title, etc.)
            index: Numéro d'incrémentation (pour le titre)
        Returns:
            str: Nouveau nom de fichier ou None si échec
        """
        try:
            filename = Path(file_path).name
            info = MetadataManager.extract_title_info(filename, format_type)
            # Prendre le titre custom si fourni
            if options and options.get('custom_title'):
                base_title = options['custom_title']
                if index is not None:
                    clean_name = f"{base_title} {index+1}"
                else:
                    clean_name = base_title
            else:
                clean_name = MetadataManager.generate_clean_filename(info, format_type)
            # Ajouter l'extension .pdf
            new_filename = f"{clean_name}.pdf"
            # Vérifier si le nouveau nom est différent
            if new_filename != filename:
                new_path = Path(file_path).parent / new_filename
                # Éviter les conflits de noms
                counter = 1
                while new_path.exists():
                    new_filename = f"{clean_name}_{counter}.pdf"
                    new_path = Path(file_path).parent / new_filename
                    counter += 1
                # Renommer le fichier
                Path(file_path).rename(new_path)
                return str(new_path)
            return str(file_path)
        except Exception as e:
            print(f"❌ Error renaming file: {e}")
            return None 