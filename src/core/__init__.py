"""
Package CORE pour la logique métier
"""

from src.core.file_manager import FileManager
from src.core.converter import NativeConverter
from src.core.metadata_manager import MetadataManager

__all__ = [
    'FileManager',
    'NativeConverter',
    'MetadataManager'
] 