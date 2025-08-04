#!/usr/bin/env python3
"""
Configuration centralisée pour l'interface unifiée
"""

# Version information
VERSION = "1.0.0"
AUTHOR = "epub2pdf Team"
DESCRIPTION = "Unified converter for EPUB, CBR, and CBZ files to PDF"

# Interface settings
WINDOW_SIZE = "1000x700"
MIN_WINDOW_SIZE = (800, 600)
PADDING = 10

# Color scheme
COLORS = {
    'primary': '#2E86AB',      # Blue
    'secondary': '#A23B72',    # Purple
    'success': '#28A745',      # Green
    'warning': '#FFC107',      # Yellow
    'danger': '#DC3545',       # Red
    'light': '#F8F9FA',        # Light gray
    'dark': '#343A40',         # Dark gray
    'white': '#FFFFFF',        # White
    'gray': '#6C757D'          # Gray
}

# File formats configuration
FILE_FORMATS = {
    'epub': {
        'name': 'EPUB',
        'icon': '📖',
        'script': 'scripts/epub2pdf.sh',
        'description': 'E-books and documents'
    },
    'cbr': {
        'name': 'CBR',
        'icon': '📚',
        'script': 'scripts/cbr2pdf.sh',
        'description': 'Comic books (RAR)'
    },
    'cbz': {
        'name': 'CBZ',
        'icon': '📖',
        'script': 'scripts/cbz2pdf.sh',
        'description': 'Comic books (ZIP)'
    }
}

# Resize options
RESIZE_OPTIONS = ["", "A4", "A3", "A5", "HD", "FHD", "Custom"]

# Paramètres par défaut
DEFAULT_SETTINGS = {
    'input_path': '',
    'output_path': '',
    'edit_metadata': False,
    'auto_rename': False,
    'custom_title': '',
    'custom_author': '',
    'custom_subject': '',
    'custom_keywords': '',
    'window_width': 800,
    'window_height': 600
}

# Regex patterns for automatic renaming
RENAME_PATTERNS = {
    'manga': [
        r'(.*?)_Vol\.(\d+)\s+Ch\.(\d+).*',  # Pattern: Title_Vol.X Ch.Y
        r'(.*?)\s+Vol\.(\d+)\s+Ch\.(\d+).*',  # Pattern: Title Vol.X Ch.Y
        r'(.*?)_(\d+)_(\d+).*',  # Pattern: Title_X_Y
        r'(.*?)\s+(\d+)\s+(\d+).*',  # Pattern: Title X Y
        r'(.*?)\s+Vol\.(\d+).*',  # Pattern: Title Vol.X
        r'(.*?)_Vol\.(\d+).*'  # Pattern: Title_Vol.X
    ],
    'comic': [
        r'(.*?)\s+(\d+).*',  # Pattern: Title X
        r'(.*?)_(\d+).*',  # Pattern: Title_X
        r'(.*?)\s+Vol\.(\d+).*',  # Pattern: Title Vol.X
        r'(.*?)_Vol\.(\d+).*'  # Pattern: Title_Vol.X
    ]
}

# Metadata templates
METADATA_TEMPLATES = {
    'manga': {
        'creator': 'Manga Converter',
        'producer': 'epub2pdf',
        'subject': 'Manga',
        'keywords': 'manga, comic, pdf'
    },
    'comic': {
        'creator': 'Comic Converter',
        'producer': 'epub2pdf',
        'subject': 'Comic',
        'keywords': 'comic, pdf'
    },
    'epub': {
        'creator': 'E-book Converter',
        'producer': 'epub2pdf',
        'subject': 'E-book',
        'keywords': 'ebook, epub, pdf'
    }
}

# Keyboard shortcuts
SHORTCUTS = {
    'browse_input': '<Control-o>',
    'browse_output': '<Control-s>',
    'scan_files': '<Control-f>',
    'convert_all': '<Control-r>',
    'dry_run': '<Control-d>',
    'exit': '<Control-q>',
    'about': '<F1>'
}

# Status messages
STATUS_MESSAGES = {
    'ready': 'Ready',
    'scanning': 'Scanning for files...',
    'converting': 'Converting files...',
    'completed': 'Conversion completed',
    'error': 'An error occurred',
    'no_files': 'No files found'
}

# Icons for status
STATUS_ICONS = {
    'ready': '✅',
    'scanning': '🔍',
    'converting': '🔄',
    'completed': '✅',
    'error': '❌',
    'warning': '⚠️'
} 