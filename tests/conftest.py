"""
Configuration pytest pour epub2pdf
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch
import sys
import os

# Ajouter le répertoire src au path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from PySide6.QtWidgets import QApplication


@pytest.fixture(scope="session")
def qt_app():
    """Fixture pour l'application Qt"""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app
    app.quit()


@pytest.fixture
def temp_dir():
    """Fixture pour un répertoire temporaire"""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


@pytest.fixture
def sample_files(temp_dir):
    """Fixture pour créer des fichiers de test"""
    # Créer des fichiers CBZ de test
    files = []
    
    for i in range(3):
        cbz_file = temp_dir / f"test_manga_{i+1}.cbz"
        # Créer un fichier ZIP simple pour simuler un CBZ
        import zipfile
        with zipfile.ZipFile(cbz_file, 'w') as zf:
            for j in range(5):  # 5 pages par manga
                zf.writestr(f"page_{j+1:03d}.jpg", f"fake_image_data_{j+1}" * 100)
        files.append(str(cbz_file))
    
    # Créer des fichiers CBR de test
    for i in range(2):
        cbr_file = temp_dir / f"test_comic_{i+1}.cbr"
        # Créer un fichier ZIP pour simuler un CBR
        import zipfile
        with zipfile.ZipFile(cbr_file, 'w') as zf:
            for j in range(8):  # 8 pages par comic
                zf.writestr(f"page_{j+1:03d}.jpg", f"fake_comic_data_{j+1}" * 100)
        files.append(str(cbr_file))
    
    return files


@pytest.fixture
def mock_file_manager():
    """Fixture pour un mock du file manager"""
    with patch('src.core.file_manager.FileManager') as mock:
        mock_instance = Mock()
        mock.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_performance_optimizer():
    """Fixture pour un mock du performance optimizer"""
    with patch('src.utils.performance_optimizer.performance_optimizer') as mock:
        yield mock


@pytest.fixture
def sample_file_info():
    """Fixture pour des informations de fichier de test"""
    return {
        'name': 'test_manga_1.cbz',
        'path': '/test/path/test_manga_1.cbz',
        'size_mb': 1.5,
        'pages': 10,
        'status': 'pending',
        'selected': False,
        'converted': False
    }


@pytest.fixture
def mock_conversion_worker():
    """Fixture pour un mock du conversion worker"""
    with patch('src.gui.modern_interface.ConversionWorker') as mock:
        mock_instance = Mock()
        mock.return_value = mock_instance
        yield mock_instance
