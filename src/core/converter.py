"""
Fichier de compatibilité pour maintenir l'ancien import
"""

# Importer la nouvelle classe depuis le module modulaire
from .converter.native_converter import NativeConverter

# Exporter la classe pour maintenir la compatibilité
__all__ = ['NativeConverter'] 