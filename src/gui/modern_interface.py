"""
Interface moderne avec PySide6 pour epub2pdf
"""

import sys
import os
import logging
from pathlib import Path
from typing import List, Dict, Optional

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QTextEdit, QProgressBar,
    QFileDialog, QMessageBox, QTabWidget, QGroupBox, QCheckBox,
    QComboBox, QSpinBox, QTreeWidget, QTreeWidgetItem, QSplitter,
    QFrame, QScrollArea, QGridLayout, QFormLayout, QInputDialog,
    QHeaderView, QDialog, QListWidget, QListWidgetItem
)
from PySide6.QtCore import Qt, QThread, Signal, QSize
from PySide6.QtGui import QFont, QPalette, QColor

from src.core.file_manager import FileManager
from src.utils.config_manager import ConfigManager


class CustomTreeWidget(QTreeWidget):
    """TreeWidget personnalisé pour gérer les clics sur les cases à cocher"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setMouseTracking(True)
    
    def mousePressEvent(self, event):
        """Gère l'événement de clic sur l'arbre"""
        if event.button() == Qt.LeftButton:
            item = self.itemAt(event.pos())
            if item:
                # Vérifier si le clic est dans la zone de la checkbox (colonne 0)
                column = self.columnAt(event.pos().x())
                if column == 0:
                    # Inverser l'état de la checkbox
                    current_state = item.checkState(0)
                    new_state = Qt.Unchecked if current_state == Qt.Checked else Qt.Checked
                    item.setCheckState(0, new_state)
                    
                    # Mettre à jour les données du fichier
                    file_info = item.data(0, Qt.UserRole)
                    if file_info:
                        file_info['selected'] = (new_state == Qt.Checked)
                    
                    # Émettre le signal de changement
                    self.itemChanged.emit(item, 0)
                    return
        
        # Appeler le comportement par défaut pour les autres cas
        super().mousePressEvent(event)


class ConversionWorker(QThread):
    """Worker thread pour la conversion en arrière-plan"""
    progress_updated = Signal(int, int, str)  # current, total, message
    file_converted = Signal(dict)  # file_info
    conversion_finished = Signal(bool, str)  # success, message
    
    def __init__(self, file_manager: FileManager, files_to_convert: List[Dict], output_directory: str = None):
        super().__init__()
        self.file_manager = file_manager
        self.files_to_convert = files_to_convert
        self.output_directory = output_directory
        self.is_running = True
        
    def run(self):
        """Exécute la conversion en arrière-plan"""
        try:
            total_files = len(self.files_to_convert)
            converted_count = 0
            failed_count = 0
            
            self.progress_updated.emit(0, total_files, "Démarrage de la conversion...")
            
            for i, file_info in enumerate(self.files_to_convert):
                if not self.is_running:
                    break
                
                # Émettre le progrès
                self.progress_updated.emit(i + 1, total_files, f"Conversion de {file_info['name']}")
                
                try:
                    # Conversion réelle
                    success = self._convert_single_file(file_info)
                    
                    if success:
                        file_info['converted'] = True
                        file_info['status'] = 'completed'
                        converted_count += 1
                        self.file_manager.logger.info(f"✅ Conversion réussie: {file_info['name']}")
                    else:
                        file_info['status'] = 'failed'
                        failed_count += 1
                        self.file_manager.logger.error(f"❌ Conversion échouée: {file_info['name']}")
                    
                    # Émettre le signal de fichier converti
                    self.file_converted.emit(file_info)
                    
                except Exception as e:
                    file_info['status'] = 'failed'
                    file_info['error'] = str(e)
                    failed_count += 1
                    self.file_manager.logger.error(f"❌ Erreur conversion {file_info['name']}: {e}")
                    self.file_converted.emit(file_info)
            
            # Message final
            if self.is_running:
                message = f"Conversion terminée: {converted_count} réussies, {failed_count} échouées"
                self.conversion_finished.emit(True, message)
            else:
                self.conversion_finished.emit(False, "Conversion arrêtée par l'utilisateur")
            
        except Exception as e:
            self.conversion_finished.emit(False, f"Erreur: {str(e)}")
    
    def _convert_single_file(self, file_info: Dict) -> bool:
        """Convertit un seul fichier"""
        try:
            file_path = file_info['path']
            file_ext = file_info['extension']
            
            # Déterminer le chemin de sortie
            if self.output_directory:
                output_dir = self.output_directory
            else:
                output_dir = str(Path(file_path).parent)
            
            # Créer le nom de fichier de sortie
            base_name = Path(file_info['name']).stem
            output_filename = f"{base_name}.pdf"
            output_path = os.path.join(output_dir, output_filename)
            
            # Options de conversion
            conversion_options = {
                'resize': 'A4',
                'grayscale': False,
                'optimize': True
            }
            
            # Conversion selon le type de fichier
            if file_ext == '.cbr':
                success, message = self.file_manager.native_converter.convert_cbr_to_pdf(
                    file_path, output_path, conversion_options
                )
            elif file_ext == '.cbz':
                success, message = self.file_manager.native_converter.convert_cbz_to_pdf(
                    file_path, output_path, conversion_options
                )
            elif file_ext == '.epub':
                success, message = self.file_manager.native_converter.convert_epub_to_pdf(
                    file_path, output_path, conversion_options
                )
            else:
                self.file_manager.logger.warning(f"⚠️ Format non supporté: {file_ext}")
                return False
            
            return success
            
        except Exception as e:
            self.file_manager.logger.error(f"❌ Erreur conversion {file_info['name']}: {e}")
            return False
    
    def stop(self):
        """Arrête la conversion"""
        self.is_running = False


class MergeWorker(QThread):
    """Worker thread pour la fusion en arrière-plan"""
    progress_updated = Signal(int, int, str)  # current, total, message
    merge_finished = Signal(bool, str)  # success, message
    
    def __init__(self, file_manager: FileManager, files_to_merge: List[Dict], output_path: str):
        super().__init__()
        self.file_manager = file_manager
        self.files_to_merge = files_to_merge
        self.output_path = output_path
        self.is_running = True
        
    def run(self):
        """Exécute la fusion en arrière-plan"""
        try:
            total_files = len(self.files_to_merge)
            converted_count = 0
            failed_count = 0
            temp_pdfs = []
            
            # Debug: afficher l'ordre reçu
            order_names = [f['name'] for f in self.files_to_merge]
            self.file_manager.logger.info(f"DEBUG - Ordre reçu pour fusion: {order_names}")
            
            self.progress_updated.emit(0, total_files, "Démarrage de la fusion...")
            
            # Étape 1: Convertir tous les fichiers en PDFs temporaires
            for i, file_info in enumerate(self.files_to_merge):
                if not self.is_running:
                    break
                
                # Émettre le progrès
                self.progress_updated.emit(i + 1, total_files, f"Conversion de {file_info['name']}")
                
                try:
                    # Conversion en PDF temporaire
                    temp_pdf = self._convert_to_temp_pdf(file_info)
                    
                    if temp_pdf and os.path.exists(temp_pdf):
                        temp_pdfs.append(temp_pdf)
                        converted_count += 1
                        self.file_manager.logger.info(f"✅ Conversion réussie: {file_info['name']}")
                    else:
                        failed_count += 1
                        self.file_manager.logger.error(f"❌ Conversion échouée: {file_info['name']}")
                    
                except Exception as e:
                    failed_count += 1
                    self.file_manager.logger.error(f"❌ Erreur conversion {file_info['name']}: {e}")
            
            # Debug: afficher l'ordre des PDFs temporaires
            temp_names = [Path(p).name for p in temp_pdfs]
            self.file_manager.logger.info(f"DEBUG - Ordre des PDFs temporaires: {temp_names}")
            
            # Étape 2: Fusionner tous les PDFs temporaires
            if temp_pdfs and self.is_running:
                self.progress_updated.emit(total_files, total_files, "Fusion des PDFs...")
                
                try:
                    success = self._merge_pdfs(temp_pdfs, self.output_path)
                    
                    if success:
                        self.file_manager.logger.info(f"✅ Fusion réussie: {len(temp_pdfs)} fichiers → {self.output_path}")
                        message = f"Fusion terminée: {converted_count} fichiers fusionnés en {Path(self.output_path).name}"
                        self.merge_finished.emit(True, message)
                    else:
                        message = f"Fusion échouée: {failed_count} erreurs"
                        self.merge_finished.emit(False, message)
                        
                except Exception as e:
                    self.file_manager.logger.error(f"❌ Erreur fusion: {e}")
                    self.merge_finished.emit(False, f"Erreur fusion: {str(e)}")
            else:
                if not self.is_running:
                    self.merge_finished.emit(False, "Fusion arrêtée par l'utilisateur")
                else:
                    self.merge_finished.emit(False, "Aucun fichier à fusionner")
            
            # Nettoyer les fichiers temporaires
            self._cleanup_temp_files(temp_pdfs)
            
        except Exception as e:
            self.merge_finished.emit(False, f"Erreur: {str(e)}")
    
    def _convert_to_temp_pdf(self, file_info: Dict) -> Optional[str]:
        """Convertit un fichier en PDF temporaire"""
        try:
            file_path = file_info['path']
            file_ext = file_info['extension']
            
            # Créer un nom de fichier temporaire unique
            import uuid
            temp_name = f"temp_{uuid.uuid4().hex[:8]}.pdf"
            
            # Utiliser le dossier temp du projet
            temp_dir = Path(__file__).parent.parent.parent / "temp"
            temp_dir.mkdir(exist_ok=True)
            temp_path = temp_dir / temp_name
            
            # Options de conversion
            conversion_options = {
                'resize': 'A4',
                'grayscale': False,
                'optimize': True
            }
            
            # Conversion selon le type de fichier
            if file_ext == '.cbr':
                success, message = self.file_manager.native_converter.convert_cbr_to_pdf(
                    file_path, str(temp_path), conversion_options
                )
            elif file_ext == '.cbz':
                success, message = self.file_manager.native_converter.convert_cbz_to_pdf(
                    file_path, str(temp_path), conversion_options
                )
            elif file_ext == '.epub':
                success, message = self.file_manager.native_converter.convert_epub_to_pdf(
                    file_path, str(temp_path), conversion_options
                )
            else:
                self.file_manager.logger.warning(f"⚠️ Format non supporté: {file_ext}")
                return None
            
            return str(temp_path) if success else None
            
        except Exception as e:
            self.file_manager.logger.error(f"❌ Erreur conversion {file_info['name']}: {e}")
            return None
    
    def _merge_pdfs(self, pdf_paths: List[str], output_path: str) -> bool:
        """Fusionne plusieurs PDFs en un seul"""
        try:
            if not pdf_paths:
                return False
            
            # Utiliser PyPDF2 pour fusionner les PDFs
            from PyPDF2 import PdfMerger
            
            merger = PdfMerger()
            
            # Ajouter chaque PDF au merger
            for pdf_path in pdf_paths:
                if os.path.exists(pdf_path):
                    with open(pdf_path, 'rb') as pdf_file:
                        merger.append(pdf_file)
                        self.file_manager.logger.debug(f"✅ PDF ajouté: {Path(pdf_path).name}")
                else:
                    self.file_manager.logger.warning(f"⚠️ PDF manquant: {pdf_path}")
            
            # Écrire le PDF fusionné
            with open(output_path, 'wb') as output_file:
                merger.write(output_file)
            
            merger.close()
            
            # Vérifier que le fichier a été créé
            if os.path.exists(output_path):
                file_size = os.path.getsize(output_path)
                self.file_manager.logger.info(f"✅ PDF fusionné créé: {output_path} ({file_size / (1024*1024):.1f} MB)")
                return True
            else:
                self.file_manager.logger.error(f"❌ PDF fusionné non créé: {output_path}")
                return False
                
        except Exception as e:
            self.file_manager.logger.error(f"❌ Erreur fusion PDFs: {e}")
            return False
    
    def _cleanup_temp_files(self, temp_files: List[str]):
        """Nettoie les fichiers temporaires"""
        for temp_file in temp_files:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
                    self.file_manager.logger.debug(f"🧹 Fichier temporaire supprimé: {Path(temp_file).name}")
            except Exception as e:
                self.file_manager.logger.warning(f"⚠️ Erreur suppression {temp_file}: {e}")
    
    def stop(self):
        """Arrête la fusion"""
        self.is_running = False


class CustomListWidget(QListWidget):
    """ListWidget personnalisé qui gère correctement le drag & drop"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDragDropMode(QListWidget.InternalMove)
        self.setAlternatingRowColors(True)
    
    def dropEvent(self, event):
        """Surcharge de dropEvent pour mettre à jour l'ordre"""
        super().dropEvent(event)
        # Émettre un signal personnalisé pour notifier le changement d'ordre
        if hasattr(self.parent(), 'on_order_changed'):
            self.parent().on_order_changed()


class MergeOrderDialog(QDialog):
    """Dialogue pour choisir l'ordre de fusion des fichiers"""
    
    def __init__(self, files, parent=None):
        super().__init__(parent)
        self.files = files
        self.ordered_files = files.copy()
        self.setup_ui()
    
    def setup_ui(self):
        self.setWindowTitle("Ordre de fusion")
        self.setModal(True)
        self.resize(600, 500)
        
        layout = QVBoxLayout(self)
        
        # Titre
        title_label = QLabel("Choisissez l'ordre de fusion des fichiers:")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px; margin-bottom: 10px;")
        layout.addWidget(title_label)
        
        # Options de tri rapide
        quick_sort_layout = QHBoxLayout()
        quick_sort_layout.addWidget(QLabel("Tri rapide:"))
        
        self.quick_sort_combo = QComboBox()
        self.quick_sort_combo.addItems([
            "Ordre de sélection",
            "Ordre alphabétique (A-Z)",
            "Ordre alphabétique inversé (Z-A)",
            "Ordre numérique (1, 2, 3...)",
            "Ordre numérique inversé (3, 2, 1...)",
            "Par taille (croissant)",
            "Par taille (décroissant)",
            "Par date (plus récent d'abord)",
            "Par date (plus ancien d'abord)"
        ])
        self.quick_sort_combo.currentTextChanged.connect(self.apply_quick_sort)
        quick_sort_layout.addWidget(self.quick_sort_combo)
        
        quick_sort_layout.addStretch()
        
        # Bouton pour réinitialiser l'ordre
        self.reset_btn = QPushButton("🔄 Réinitialiser")
        self.reset_btn.clicked.connect(self.reset_order)
        quick_sort_layout.addWidget(self.reset_btn)
        
        layout.addLayout(quick_sort_layout)
        
        # Liste des fichiers
        self.files_list = CustomListWidget(self)
        self.update_files_list()
        layout.addWidget(self.files_list)
        
        # Instructions
        instructions_label = QLabel("💡 Glissez-déposez les fichiers pour les réorganiser, ou utilisez les boutons Monter/Descendre")
        instructions_label.setStyleSheet("color: #666; font-style: italic; margin: 5px;")
        layout.addWidget(instructions_label)
        
        # Boutons
        buttons_layout = QHBoxLayout()
        
        self.move_up_btn = QPushButton("⬆️ Monter")
        self.move_up_btn.clicked.connect(self.move_up)
        buttons_layout.addWidget(self.move_up_btn)
        
        self.move_down_btn = QPushButton("⬇️ Descendre")
        self.move_down_btn.clicked.connect(self.move_down)
        buttons_layout.addWidget(self.move_down_btn)
        
        buttons_layout.addStretch()
        
        self.ok_btn = QPushButton("✅ Confirmer")
        self.ok_btn.clicked.connect(self.accept)
        self.ok_btn.setDefault(True)
        buttons_layout.addWidget(self.ok_btn)
        
        self.cancel_btn = QPushButton("❌ Annuler")
        self.cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(buttons_layout)
    
    def on_order_changed(self):
        """Appelé quand l'ordre change par drag & drop"""
        self.update_order_from_list()
    
    def update_files_list(self):
        self.files_list.clear()
        for i, file_info in enumerate(self.ordered_files, 1):
            size_mb = file_info.get('size', 0) / (1024 * 1024) if file_info.get('size', 0) > 0 else 0
            item = QListWidgetItem(f"{i:2d}. {file_info['name']} ({size_mb:.1f} MB)")
            item.setData(Qt.UserRole, file_info)
            self.files_list.addItem(item)
    
    def update_order_from_list(self):
        """Met à jour l'ordre des fichiers selon la liste actuelle"""
        new_order = []
        for i in range(self.files_list.count()):
            item = self.files_list.item(i)
            if item:
                file_info = item.data(Qt.UserRole)
                if file_info:
                    new_order.append(file_info)
        
        if new_order and new_order != self.ordered_files:
            self.ordered_files = new_order
            # Mettre à jour les numéros sans recréer la liste
            self.update_numbers_only()
    
    def update_numbers_only(self):
        """Met à jour seulement les numéros sans recréer la liste"""
        for i in range(self.files_list.count()):
            item = self.files_list.item(i)
            if item:
                file_info = item.data(Qt.UserRole)
                if file_info:
                    size_mb = file_info.get('size', 0) / (1024 * 1024) if file_info.get('size', 0) > 0 else 0
                    item.setText(f"{i+1:2d}. {file_info['name']} ({size_mb:.1f} MB)")
    
    def apply_quick_sort(self, sort_type):
        if sort_type == "Ordre de sélection":
            # Garder l'ordre de sélection original
            pass
        elif sort_type == "Ordre alphabétique (A-Z)":
            self.ordered_files.sort(key=lambda x: x['name'].lower())
        elif sort_type == "Ordre alphabétique inversé (Z-A)":
            self.ordered_files.sort(key=lambda x: x['name'].lower(), reverse=True)
        elif sort_type == "Ordre numérique (1, 2, 3...)":
            self.ordered_files.sort(key=self._extract_number)
        elif sort_type == "Ordre numérique inversé (3, 2, 1...)":
            self.ordered_files.sort(key=self._extract_number, reverse=True)
        elif sort_type == "Par taille (croissant)":
            self.ordered_files.sort(key=lambda x: x.get('size', 0))
        elif sort_type == "Par taille (décroissant)":
            self.ordered_files.sort(key=lambda x: x.get('size', 0), reverse=True)
        elif sort_type == "Par date (plus récent d'abord)":
            self.ordered_files.sort(key=lambda x: x.get('modified', 0), reverse=True)
        elif sort_type == "Par date (plus ancien d'abord)":
            self.ordered_files.sort(key=lambda x: x.get('modified', 0))
        
        self.update_files_list()
    
    def reset_order(self):
        """Réinitialise l'ordre à l'ordre de sélection original"""
        self.ordered_files = self.files.copy()
        self.update_files_list()
        self.quick_sort_combo.setCurrentText("Ordre de sélection")
    
    def _extract_number(self, file_info):
        """Extrait le premier nombre du nom de fichier pour le tri numérique"""
        import re
        name = file_info['name']
        numbers = re.findall(r'\d+', name)
        return int(numbers[0]) if numbers else 0
    
    def move_up(self):
        current_row = self.files_list.currentRow()
        if current_row > 0:
            self.ordered_files.insert(current_row - 1, self.ordered_files.pop(current_row))
            self.update_files_list()
            self.files_list.setCurrentRow(current_row - 1)
    
    def move_down(self):
        current_row = self.files_list.currentRow()
        if current_row < len(self.ordered_files) - 1:
            self.ordered_files.insert(current_row + 1, self.ordered_files.pop(current_row))
            self.update_files_list()
            self.files_list.setCurrentRow(current_row + 1)
    
    def get_ordered_files(self):
        """Récupère l'ordre actuel des fichiers depuis la liste"""
        # Mettre à jour l'ordre depuis la liste actuelle
        current_order = []
        for i in range(self.files_list.count()):
            item = self.files_list.item(i)
            if item:
                file_info = item.data(Qt.UserRole)
                if file_info:
                    current_order.append(file_info)
        
        # Si l'ordre a changé, le mettre à jour
        if current_order and current_order != self.ordered_files:
            self.ordered_files = current_order
        
        return self.ordered_files


class ModernInterface(QMainWindow):
    """Interface moderne avec PySide6"""
    
    def __init__(self):
        super().__init__()
        self.file_manager = FileManager()
        self.conversion_worker = None
        self.files = []
        self.config_manager = ConfigManager()
        
        # Configuration de l'interface
        self.setWindowTitle("epub2pdf - Convertisseur Moderne")
        self.setMinimumSize(1200, 800)
        
        # Configuration du thème sombre
        self.setup_dark_theme()
        
        # Configuration de l'interface
        self.setup_ui()
        
        # Connecter les signaux
        self.setup_connections()
        
        # Charger la configuration sauvegardée
        self.load_saved_config()
    
    def setup_dark_theme(self):
        """Configure le thème sombre moderne"""
        # Palette de couleurs sombre
        palette = QPalette()
        
        # Couleurs de base
        palette.setColor(QPalette.Window, QColor(53, 53, 53))
        palette.setColor(QPalette.WindowText, QColor(255, 255, 255))
        palette.setColor(QPalette.Base, QColor(25, 25, 25))
        palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        palette.setColor(QPalette.ToolTipBase, QColor(255, 255, 255))
        palette.setColor(QPalette.ToolTipText, QColor(255, 255, 255))
        palette.setColor(QPalette.Text, QColor(255, 255, 255))
        palette.setColor(QPalette.Button, QColor(53, 53, 53))
        palette.setColor(QPalette.ButtonText, QColor(255, 255, 255))
        palette.setColor(QPalette.BrightText, QColor(255, 0, 0))
        palette.setColor(QPalette.Link, QColor(42, 130, 218))
        palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
        
        self.setPalette(palette)
        
        # Style moderne
        self.setStyleSheet("""
            QMainWindow {
                background-color: #353535;
            }
            QTabWidget::pane {
                border: 1px solid #555555;
                background-color: #252525;
            }
            QTabBar::tab {
                background-color: #404040;
                color: white;
                padding: 8px 16px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #2a82da;
            }
            QPushButton {
                background-color: #2a82da;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1e6bb8;
            }
            QPushButton:pressed {
                background-color: #155a9e;
            }
            QPushButton:disabled {
                background-color: #555555;
                color: #888888;
            }
            QLineEdit, QTextEdit {
                background-color: #404040;
                color: white;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 4px;
            }
            QTreeWidget {
                background-color: #404040;
                color: white;
                border: 1px solid #555555;
                border-radius: 4px;
            }
            QProgressBar {
                border: 1px solid #555555;
                border-radius: 4px;
                text-align: center;
                background-color: #404040;
            }
            QProgressBar::chunk {
                background-color: #2a82da;
                border-radius: 3px;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #555555;
                border-radius: 4px;
                margin-top: 8px;
                padding-top: 8px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 8px;
                padding: 0 4px 0 4px;
            }
        """)
    
    def setup_ui(self):
        """Configure l'interface utilisateur"""
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QVBoxLayout(central_widget)
        
        # Titre
        title_label = QLabel("epub2pdf - Convertisseur Moderne")
        title_label.setAlignment(Qt.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #2a82da; margin: 10px;")
        main_layout.addWidget(title_label)
        
        # Widget à onglets
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # Onglet Conversion
        self.setup_conversion_tab()
        
        # Onglet Options
        self.setup_options_tab()
        
        # Barre de statut
        self.status_label = QLabel("Prêt")
        self.status_label.setStyleSheet("color: #888888; padding: 5px;")
        main_layout.addWidget(self.status_label)
        
        # Barre de progression
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)
    
    def setup_conversion_tab(self):
        """Configure l'onglet de conversion"""
        conversion_widget = QWidget()
        layout = QVBoxLayout(conversion_widget)
        
        # Créer un splitter principal pour diviser l'interface
        main_splitter = QSplitter(Qt.Vertical)
        
        # =============================================================================
        # SECTION SUPÉRIEURE : Configuration et contrôles
        # =============================================================================
        top_widget = QWidget()
        top_layout = QVBoxLayout(top_widget)
        
        # Section des chemins (plus compacte)
        paths_group = QGroupBox("Chemins")
        paths_layout = QFormLayout(paths_group)
        paths_layout.setSpacing(5)
        
        # Répertoire d'entrée
        self.input_path_edit = QLineEdit()
        self.input_path_edit.setPlaceholderText("Sélectionnez le répertoire d'entrée...")
        self.browse_input_btn = QPushButton("Parcourir")
        self.browse_input_btn.setMaximumWidth(80)
        input_layout = QHBoxLayout()
        input_layout.addWidget(self.input_path_edit)
        input_layout.addWidget(self.browse_input_btn)
        paths_layout.addRow("Répertoire d'entrée:", input_layout)
        
        # Répertoire de sortie
        self.output_path_edit = QLineEdit()
        self.output_path_edit.setPlaceholderText("Sélectionnez le répertoire de sortie...")
        self.browse_output_btn = QPushButton("Parcourir")
        self.browse_output_btn.setMaximumWidth(80)
        output_layout = QHBoxLayout()
        output_layout.addWidget(self.output_path_edit)
        output_layout.addWidget(self.browse_output_btn)
        paths_layout.addRow("Répertoire de sortie:", output_layout)
        
        top_layout.addWidget(paths_group)
        
        # Section des filtres et options (plus compacte)
        filters_group = QGroupBox("Filtres et Options")
        filters_layout = QGridLayout(filters_group)
        filters_layout.setSpacing(5)
        
        # Ligne 1 : Recherche et Mode récursif
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Rechercher dans les fichiers...")
        filters_layout.addWidget(QLabel("Recherche:"), 0, 0)
        filters_layout.addWidget(self.search_edit, 0, 1)
        
        self.recursive_checkbox = QCheckBox("Mode récursif")
        filters_layout.addWidget(self.recursive_checkbox, 0, 2)
        
        # Ligne 2 : Tri
        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["Nom", "Taille", "Date"])
        filters_layout.addWidget(QLabel("Tri par:"), 1, 0)
        filters_layout.addWidget(self.sort_combo, 1, 1)
        
        top_layout.addWidget(filters_group)
        
        # Boutons d'action (plus compacts)
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(5)
        
        self.scan_btn = QPushButton("🔍 Scanner")
        self.scan_btn.setMaximumWidth(100)
        buttons_layout.addWidget(self.scan_btn)
        
        self.select_all_btn = QPushButton("☑️ Tout sélectionner")
        self.select_all_btn.setMaximumWidth(120)
        buttons_layout.addWidget(self.select_all_btn)
        
        self.deselect_all_btn = QPushButton("☐ Tout désélectionner")
        self.deselect_all_btn.setMaximumWidth(130)
        buttons_layout.addWidget(self.deselect_all_btn)
        
        buttons_layout.addStretch()
        
        top_layout.addLayout(buttons_layout)
        
        # =============================================================================
        # SECTION CENTRALE : Liste des fichiers (PLUS GRANDE)
        # =============================================================================
        self.files_group = QGroupBox("Fichiers")
        files_layout = QVBoxLayout(self.files_group)
        
        # Créer un TreeWidget personnalisé pour gérer les clics
        self.files_tree = CustomTreeWidget()
        self.files_tree.setHeaderLabels(["Nom", "Taille", "Pages", "Statut"])
        self.files_tree.setAlternatingRowColors(True)
        
        # Configuration pour une meilleure sélection et visibilité
        self.files_tree.setSelectionMode(QTreeWidget.SingleSelection)
        self.files_tree.setRootIsDecorated(False)
        self.files_tree.setUniformRowHeights(True)
        
        # Ajuster la taille des colonnes
        self.files_tree.setColumnWidth(0, 300)  # Nom - plus large
        self.files_tree.setColumnWidth(1, 80)   # Taille
        self.files_tree.setColumnWidth(2, 60)   # Pages
        self.files_tree.setColumnWidth(3, 100)  # Statut
        
        # Permettre le redimensionnement des colonnes
        self.files_tree.header().setStretchLastSection(False)
        self.files_tree.header().setSectionResizeMode(0, QHeaderView.Stretch)  # Nom s'étend
        
        files_layout.addWidget(self.files_tree)
        
        # =============================================================================
        # SECTION INFÉRIEURE : Actions et logs
        # =============================================================================
        bottom_widget = QWidget()
        bottom_layout = QVBoxLayout(bottom_widget)
        
        # Boutons de conversion (plus compacts)
        conversion_buttons_layout = QHBoxLayout()
        conversion_buttons_layout.setSpacing(5)
        
        self.convert_selected_btn = QPushButton("🔄 Convertir la sélection")
        self.convert_selected_btn.setEnabled(False)
        conversion_buttons_layout.addWidget(self.convert_selected_btn)
        
        self.convert_all_btn = QPushButton("🚀 Convertir tout")
        self.convert_all_btn.setEnabled(False)
        conversion_buttons_layout.addWidget(self.convert_all_btn)
        
        self.merge_selected_btn = QPushButton("📄 Fusionner la sélection")
        self.merge_selected_btn.setEnabled(False)
        self.merge_selected_btn.clicked.connect(self.merge_selected_files)
        conversion_buttons_layout.addWidget(self.merge_selected_btn)
        
        self.stop_btn = QPushButton("⏹️ Arrêter")
        self.stop_btn.setEnabled(False)
        conversion_buttons_layout.addWidget(self.stop_btn)
        
        conversion_buttons_layout.addStretch()
        
        bottom_layout.addLayout(conversion_buttons_layout)
        
        # Zone de logs/output (plus petite mais toujours accessible)
        logs_group = QGroupBox("Logs et Output")
        logs_layout = QVBoxLayout(logs_group)
        
        # Zone de texte pour les logs
        self.logs_text = QTextEdit()
        self.logs_text.setReadOnly(True)
        self.logs_text.setMaximumHeight(150)  # Plus petite
        self.logs_text.setFont(QFont("Courier", 9))
        
        # Boutons pour les logs
        logs_buttons_layout = QHBoxLayout()
        
        self.clear_logs_btn = QPushButton("🗑️ Effacer")
        self.clear_logs_btn.setMaximumWidth(80)
        self.clear_logs_btn.clicked.connect(self.clear_logs)
        logs_buttons_layout.addWidget(self.clear_logs_btn)
        
        self.save_logs_btn = QPushButton("💾 Sauvegarder")
        self.save_logs_btn.setMaximumWidth(100)
        self.save_logs_btn.clicked.connect(self.save_logs)
        logs_buttons_layout.addWidget(self.save_logs_btn)
        
        logs_buttons_layout.addStretch()
        
        logs_layout.addWidget(self.logs_text)
        logs_layout.addLayout(logs_buttons_layout)
        
        bottom_layout.addWidget(logs_group)
        
        # =============================================================================
        # ASSEMBLAGE FINAL AVEC SPLITTER
        # =============================================================================
        
        # Ajouter les widgets au splitter
        main_splitter.addWidget(top_widget)
        main_splitter.addWidget(self.files_group)
        main_splitter.addWidget(bottom_widget)
        
        # Définir les proportions initiales (donner plus d'espace aux fichiers)
        main_splitter.setSizes([150, 400, 200])  # Top, Files, Bottom
        
        layout.addWidget(main_splitter)
        
        # Ajouter l'onglet
        self.tab_widget.addTab(conversion_widget, "Conversion")
        
        # Initialiser l'état des boutons
        self.update_conversion_buttons_state()
    
    def setup_options_tab(self):
        """Configure l'onglet des options"""
        options_widget = QWidget()
        layout = QVBoxLayout(options_widget)
        
        # Section des performances
        performance_group = QGroupBox("Optimisations de Performance")
        performance_layout = QFormLayout(performance_group)
        
        # Nombre de workers
        self.workers_spin = QSpinBox()
        self.workers_spin.setRange(1, 16)
        self.workers_spin.setValue(5)  # Valeur par défaut
        performance_layout.addRow("Workers:", self.workers_spin)
        
        # Optimisations
        self.use_cache_checkbox = QCheckBox("Utiliser le cache")
        self.use_cache_checkbox.setChecked(True)
        performance_layout.addRow("", self.use_cache_checkbox)
        
        self.use_parallel_checkbox = QCheckBox("Traitement parallèle")
        self.use_parallel_checkbox.setChecked(True)
        performance_layout.addRow("", self.use_parallel_checkbox)
        
        layout.addWidget(performance_group)
        
        # Section des options de conversion
        conversion_options_group = QGroupBox("Options de Conversion")
        conversion_options_layout = QFormLayout(conversion_options_group)
        
        # Format de sortie
        self.output_format_combo = QComboBox()
        self.output_format_combo.addItems(["PDF", "PDF optimisé"])
        conversion_options_layout.addRow("Format de sortie:", self.output_format_combo)
        
        # Redimensionnement
        self.resize_combo = QComboBox()
        self.resize_combo.addItems(["Aucun", "A4", "Letter", "HD", "FHD"])
        conversion_options_layout.addRow("Redimensionnement:", self.resize_combo)
        
        # Options avancées
        self.grayscale_checkbox = QCheckBox("Niveau de gris")
        conversion_options_layout.addRow("", self.grayscale_checkbox)
        
        self.optimize_checkbox = QCheckBox("Optimiser les PDFs")
        self.optimize_checkbox.setChecked(True)
        conversion_options_layout.addRow("", self.optimize_checkbox)
        
        layout.addWidget(conversion_options_group)
        
        # Section des métadonnées
        metadata_group = QGroupBox("Métadonnées")
        metadata_layout = QFormLayout(metadata_group)
        
        self.add_metadata_checkbox = QCheckBox("Ajouter les métadonnées")
        metadata_layout.addRow("", self.add_metadata_checkbox)
        
        layout.addWidget(metadata_group)
        
        # Section des options de fusion
        merge_group = QGroupBox("Options de Fusion")
        merge_layout = QFormLayout(merge_group)
        
        # Fusion des volumes
        self.merge_volumes_check = QCheckBox("Fusionner les volumes")
        merge_layout.addRow("", self.merge_volumes_check)
        
        # Récupération des métadonnées
        self.fetch_metadata_check = QCheckBox("Récupérer les métadonnées")
        self.fetch_metadata_check.setChecked(True)
        merge_layout.addRow("", self.fetch_metadata_check)
        
        # Ordre de fusion
        self.merge_order_combo = QComboBox()
        self.merge_order_combo.addItems(["Naturel", "Alphabétique", "Inversé", "Personnalisé"])
        merge_layout.addRow("Ordre de fusion:", self.merge_order_combo)
        
        layout.addWidget(merge_group)
        
        # Ajouter l'onglet
        self.tab_widget.addTab(options_widget, "Options")
    
    def setup_connections(self):
        """Configure les connexions entre les widgets"""
        # Connexions pour les chemins
        self.browse_input_btn.clicked.connect(self.browse_input_directory)
        self.browse_output_btn.clicked.connect(self.browse_output_directory)
        
        # Connexions pour les actions
        self.scan_btn.clicked.connect(self.scan_files)
        self.select_all_btn.clicked.connect(self.select_all_files)
        self.deselect_all_btn.clicked.connect(self.deselect_all_files)
        
        # Connexions pour la conversion
        self.convert_selected_btn.clicked.connect(self.convert_selected_files)
        self.convert_all_btn.clicked.connect(self.convert_all_files)
        self.stop_btn.clicked.connect(self.stop_conversion)
        
        # Connexions pour la recherche et le tri (temps réel)
        self.search_edit.textChanged.connect(self.filter_files)
        self.sort_combo.currentTextChanged.connect(self.filter_files)
        
        # Connexions pour les fichiers
        self.files_tree.itemChanged.connect(self.on_file_selection_changed)
        
        # Connexions pour la configuration
        self.input_path_edit.textChanged.connect(self.on_config_changed)
        self.output_path_edit.textChanged.connect(self.on_config_changed)
        self.search_edit.textChanged.connect(self.on_config_changed)
        self.recursive_checkbox.toggled.connect(self.on_config_changed)
        self.sort_combo.currentTextChanged.connect(self.on_config_changed)
        
        # Charger la configuration sauvegardée
        self.load_saved_config()
    
    def on_file_selection_changed(self, item, column):
        """Appelé quand la sélection d'un fichier change"""
        if column == 0:  # Seulement pour la colonne du nom
            file_info = item.data(0, Qt.UserRole)
            if file_info:
                is_checked = item.checkState(0) == Qt.Checked
                file_info['selected'] = is_checked
                
                # Mettre à jour la liste principale des fichiers
                for i, f in enumerate(self.files):
                    if f['path'] == file_info['path']:
                        self.files[i]['selected'] = is_checked
                        break
                
                # Mettre à jour le statut
                self.update_conversion_buttons_state()
    
    def update_conversion_buttons_state(self):
        """Met à jour l'état des boutons de conversion"""
        selected_files = [f for f in self.files if f.get('selected', False)]
        has_files = len(self.files) > 0
        
        # Activer le bouton de sélection seulement s'il y a des fichiers sélectionnés
        self.convert_selected_btn.setEnabled(len(selected_files) > 0)
        self.convert_all_btn.setEnabled(has_files)
        self.merge_selected_btn.setEnabled(len(selected_files) > 1)  # Au moins 2 fichiers pour fusionner
        
    def merge_selected_files(self):
        """Fusionne les fichiers sélectionnés"""
        selected_files = [f for f in self.files if f.get('selected', False)]
        
        if len(selected_files) < 2:
            self.add_log_message("Veuillez sélectionner au moins 2 fichiers pour la fusion", "WARNING")
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner au moins 2 fichiers pour la fusion")
            return
        
        self.add_log_message(f"Tentative de fusion de {len(selected_files)} fichiers sélectionnés", "INFO")
        
        # Demander l'ordre de fusion
        merge_order = self._select_merge_order(selected_files)
        if not merge_order:
            self.add_log_message("Fusion annulée par l'utilisateur", "INFO")
            return
        
        # Générer un nom de fichier par défaut
        default_name = self._generate_merge_filename(selected_files)
        
        # Demander le nom du fichier fusionné
        filename, ok = QInputDialog.getText(
            self,
            "Nom du fichier fusionné",
            "Entrez le nom du fichier PDF fusionné:",
            QLineEdit.Normal,
            default_name
        )
        
        if not ok or not filename.strip():
            self.add_log_message("Fusion annulée par l'utilisateur", "INFO")
            return
        
        # Ajouter l'extension .pdf si nécessaire
        if not filename.lower().endswith('.pdf'):
            filename += '.pdf'
        
        # Déterminer le répertoire de sortie
        output_directory = self.output_path_edit.text().strip()
        if not output_directory:
            output_directory = str(Path.home() / "Documents")
        
        # Créer le chemin complet
        output_path = os.path.join(output_directory, filename)
        
        # Vérifier si le fichier existe déjà
        if os.path.exists(output_path):
            reply = QMessageBox.question(
                self,
                "Fichier existant",
                f"Le fichier {filename} existe déjà. Voulez-vous le remplacer ?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.No:
                self.add_log_message("Fusion annulée - fichier existant", "INFO")
                return
        
        # Démarrer la fusion avec l'ordre choisi
        self.start_merge(merge_order, output_path)
    
    def _select_merge_order(self, selected_files):
        """Permet à l'utilisateur de choisir l'ordre de fusion"""
        # Créer et afficher le dialogue
        dialog = MergeOrderDialog(selected_files, self)
        if dialog.exec() == QDialog.Accepted:
            ordered_files = dialog.get_ordered_files()
            self.add_log_message(f"Ordre de fusion choisi: {len(ordered_files)} fichiers", "INFO")
            return ordered_files
        else:
            return None
    
    def _generate_merge_filename(self, selected_files):
        """Génère un nom de fichier par défaut pour la fusion"""
        if not selected_files:
            return "merged.pdf"
        
        # Essayer d'extraire le nom de la série du premier fichier
        first_file = selected_files[0]['name']
        
        # Patterns pour extraire le nom de la série
        import re
        
        # Pattern: Series - Volume XX - Chapter XXX
        pattern1 = r'^(.+?)\s*[-_]\s*[Vv]olume\s*\d+'
        match = re.search(pattern1, first_file)
        if match:
            series_name = match.group(1).strip()
            return f"{series_name}_merged.pdf"
        
        # Pattern: Series Vol.XX Ch.XXX
        pattern2 = r'^(.+?)\s+[Vv]ol\.?\s*\d+'
        match = re.search(pattern2, first_file)
        if match:
            series_name = match.group(1).strip()
            return f"{series_name}_merged.pdf"
        
        # Fallback: utiliser le nom du premier fichier sans extension
        base_name = Path(first_file).stem
        return f"{base_name}_merged.pdf"
    
    def start_merge(self, files_to_merge: List[Dict], output_path: str):
        """Démarre le processus de fusion"""
        try:
            # Désactiver les boutons pendant la fusion
            self.merge_selected_btn.setEnabled(False)
            self.convert_selected_btn.setEnabled(False)
            self.convert_all_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
            
            # Créer et démarrer le worker de fusion
            self.merge_worker = MergeWorker(self.file_manager, files_to_merge, output_path)
            self.merge_worker.progress_updated.connect(self.update_progress)
            self.merge_worker.merge_finished.connect(self.on_merge_finished)
            
            self.add_log_message(f"🚀 Démarrage de la fusion vers: {output_path}", "INFO")
            self.merge_worker.start()
            
        except Exception as e:
            error_msg = f"Erreur lors du démarrage de la fusion: {e}"
            self.add_log_message(error_msg, "ERROR")
            QMessageBox.critical(self, "Erreur", error_msg)
            
            # Réactiver les boutons
            self.merge_selected_btn.setEnabled(True)
            self.convert_selected_btn.setEnabled(True)
            self.convert_all_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)
    
    def on_merge_finished(self, success: bool, message: str):
        """Appelé quand la fusion est terminée"""
        self.progress_bar.setVisible(False)
        self.convert_selected_btn.setEnabled(True)
        self.convert_all_btn.setEnabled(True)
        self.merge_selected_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        
        if success:
            self.status_label.setText(message)
            QMessageBox.information(self, "Succès", message)
        else:
            self.status_label.setText(f"Erreur: {message}")
            QMessageBox.critical(self, "Erreur", message)
    
    def browse_input_directory(self):
        """Ouvre le dialogue de sélection du répertoire d'entrée"""
        directory = QFileDialog.getExistingDirectory(
            self, "Sélectionner le répertoire d'entrée"
        )
        if directory:
            self.input_path_edit.setText(directory)
    
    def browse_output_directory(self):
        """Ouvre le dialogue de sélection du répertoire de sortie"""
        directory = QFileDialog.getExistingDirectory(
            self, "Sélectionner le répertoire de sortie"
        )
        if directory:
            self.output_path_edit.setText(directory)
            # Sauvegarder automatiquement le dossier de sortie
            self.config_manager.set('output_folder', directory)
            self.add_log_message(f"✅ Dossier de sortie sauvegardé: {directory}", "INFO")
    
    def scan_files(self):
        """Scanne les fichiers dans le répertoire d'entrée"""
        input_path = self.input_path_edit.text().strip()
        if not input_path:
            self.add_log_message("Veuillez sélectionner un répertoire d'entrée", "WARNING")
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner un répertoire d'entrée")
            return
        
        if not os.path.exists(input_path):
            self.add_log_message(f"Le répertoire n'existe pas: {input_path}", "ERROR")
            QMessageBox.critical(self, "Erreur", f"Le répertoire n'existe pas:\n{input_path}")
            return
        
        try:
            self.add_log_message(f"🔍 Scan du répertoire: {input_path}", "INFO")
            
            # Scanner les fichiers
            recursive = self.recursive_checkbox.isChecked()
            self.files = self.file_manager.scan_directory(input_path, recursive=recursive)
            
            # Mettre à jour l'arbre des fichiers
            self.update_files_tree()
            
            # Mettre à jour l'état des boutons
            self.update_conversion_buttons_state()
            
            self.add_log_message(f"✅ Scan terminé: {len(self.files)} fichiers trouvés", "INFO")
            
        except Exception as e:
            error_msg = f"Erreur lors du scan: {e}"
            self.add_log_message(error_msg, "ERROR")
            QMessageBox.critical(self, "Erreur", error_msg)
    
    def update_files_tree(self):
        """Met à jour l'arbre des fichiers"""
        if not hasattr(self, 'files_tree'):
            return
        
        # Bloquer les signaux pendant la mise à jour
        self.files_tree.blockSignals(True)
        self.files_tree.clear()
        
        if not self.files:
            return
        
        # Trier les fichiers selon le critère sélectionné
        sort_by = self.sort_combo.currentText().lower()
        reverse = False
        
        if sort_by == "nom":
            self.files.sort(key=lambda x: x['name'].lower())
        elif sort_by == "taille":
            self.files.sort(key=lambda x: x.get('size', 0), reverse=True)
        elif sort_by == "date":
            self.files.sort(key=lambda x: x.get('modified', 0), reverse=True)
        
        # Appliquer le filtre de recherche
        search_term = self.search_edit.text().lower()
        filtered_files = self.files
        
        if search_term:
            filtered_files = [f for f in self.files if search_term in f['name'].lower()]
        
        # Ajouter les fichiers à l'arbre
        for file_info in filtered_files:
            item = QTreeWidgetItem()
            
            # Nom du fichier (plus lisible)
            name = file_info['name']
            if len(name) > 50:
                name = name[:47] + "..."
            item.setText(0, name)
            item.setToolTip(0, file_info['name'])  # Tooltip avec le nom complet
            
            # Taille formatée
            size = file_info.get('size', 0)
            if size > 0:
                if size < 1024:
                    size_str = f"{size} B"
                elif size < 1024 * 1024:
                    size_str = f"{size / 1024:.1f} KB"
                else:
                    size_str = f"{size / (1024 * 1024):.1f} MB"
            else:
                size_str = "N/A"
            item.setText(1, size_str)
            
            # Nombre de pages
            pages = file_info.get('pages', 0)
            item.setText(2, str(pages) if pages > 0 else "N/A")
            
            # Statut
            status = file_info.get('status', 'pending')
            status_text = {
                'pending': '⏳ En attente',
                'converting': '🔄 Conversion...',
                'completed': '✅ Terminé',
                'failed': '❌ Échoué',
                'merged': '📄 Fusionné'
            }.get(status, '⏳ En attente')
            item.setText(3, status_text)
            
            # Couleur selon le statut
            if status == 'completed':
                item.setForeground(3, QColor('#00AA00'))  # Vert
            elif status == 'failed':
                item.setForeground(3, QColor('#FF0000'))  # Rouge
            elif status == 'converting':
                item.setForeground(3, QColor('#FFAA00'))  # Orange
            elif status == 'merged':
                item.setForeground(3, QColor('#0088FF'))  # Bleu
            
            # Case à cocher pour la sélection
            item.setCheckState(0, Qt.Checked if file_info.get('selected', False) else Qt.Unchecked)
            
            # Stocker les données du fichier
            item.setData(0, Qt.UserRole, file_info)
            
            # Ajouter l'item à l'arbre
            self.files_tree.addTopLevelItem(item)
        
        # Mettre à jour le nombre de fichiers
        total_files = len(self.files)
        selected_files = len([f for f in self.files if f.get('selected', False)])
        
        # Mettre à jour le titre du groupe
        files_group_title = f"Fichiers ({selected_files}/{total_files} sélectionnés)"
        if hasattr(self, 'files_group'):
            self.files_group.setTitle(files_group_title)
        
        # Débloquer les signaux
        self.files_tree.blockSignals(False)
        
        # Mettre à jour l'état des boutons
        self.update_conversion_buttons_state()
    
    def select_all_files(self):
        """Sélectionne tous les fichiers"""
        # Désactiver temporairement les signaux
        self.files_tree.blockSignals(True)
        
        for i in range(self.files_tree.topLevelItemCount()):
            item = self.files_tree.topLevelItem(i)
            item.setCheckState(0, Qt.Checked)
        
        # Mettre à jour la liste principale
        for file_info in self.files:
            file_info['selected'] = True
        
        # Réactiver les signaux
        self.files_tree.blockSignals(False)
        
        # Mettre à jour les boutons
        self.update_conversion_buttons_state()
    
    def deselect_all_files(self):
        """Désélectionne tous les fichiers"""
        # Désactiver temporairement les signaux
        self.files_tree.blockSignals(True)
        
        for i in range(self.files_tree.topLevelItemCount()):
            item = self.files_tree.topLevelItem(i)
            item.setCheckState(0, Qt.Unchecked)
        
        # Mettre à jour la liste principale
        for file_info in self.files:
            file_info['selected'] = False
        
        # Réactiver les signaux
        self.files_tree.blockSignals(False)
        
        # Mettre à jour les boutons
        self.update_conversion_buttons_state()
    
    def filter_files(self):
        """Filtre et trie les fichiers selon les critères sélectionnés"""
        if not hasattr(self, 'files') or not self.files:
            return
        
        # Mettre à jour l'arbre des fichiers avec les nouveaux filtres
        self.update_files_tree()
        
        # Ajouter un message de log si des filtres sont appliqués
        search_term = self.search_edit.text().strip()
        if search_term:
            filtered_count = len([f for f in self.files if search_term.lower() in f['name'].lower()])
            self.add_log_message(f"🔍 Recherche '{search_term}': {filtered_count} fichiers trouvés", "INFO")
    
    def convert_selected_files(self):
        """Convertit les fichiers sélectionnés"""
        selected_files = [f for f in self.files if f.get('selected', False)]
        
        if not selected_files:
            self.add_log_message("Aucun fichier sélectionné", "WARNING")
            QMessageBox.warning(self, "Erreur", "Aucun fichier sélectionné")
            return
        
        self.add_log_message(f"Démarrage de la conversion de {len(selected_files)} fichiers sélectionnés", "INFO")
        self.start_conversion(selected_files)
    
    def convert_all_files(self):
        """Convertit tous les fichiers"""
        if not self.files:
            self.add_log_message("Aucun fichier à convertir", "WARNING")
            QMessageBox.warning(self, "Erreur", "Aucun fichier à convertir")
            return
        
        self.add_log_message(f"Démarrage de la conversion de tous les {len(self.files)} fichiers", "INFO")
        self.start_conversion(self.files)
    
    def start_conversion(self, files_to_convert: List[Dict]):
        """Démarre le processus de conversion"""
        try:
            # Désactiver les boutons pendant la conversion
            self.convert_selected_btn.setEnabled(False)
            self.convert_all_btn.setEnabled(False)
            self.merge_selected_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
            
            # Déterminer le répertoire de sortie
            output_directory = self.output_path_edit.text().strip()
            if not output_directory:
                output_directory = str(Path.home() / "Documents")
            
            # Créer et démarrer le worker de conversion
            self.conversion_worker = ConversionWorker(self.file_manager, files_to_convert, output_directory)
            self.conversion_worker.progress_updated.connect(self.update_progress)
            self.conversion_worker.file_converted.connect(self.on_file_converted)
            self.conversion_worker.conversion_finished.connect(self.on_conversion_finished)
            
            self.add_log_message(f"🚀 Démarrage de la conversion vers: {output_directory}", "INFO")
            self.conversion_worker.start()
            
        except Exception as e:
            error_msg = f"Erreur lors du démarrage de la conversion: {e}"
            self.add_log_message(error_msg, "ERROR")
            QMessageBox.critical(self, "Erreur", error_msg)
            
            # Réactiver les boutons
            self.convert_selected_btn.setEnabled(True)
            self.convert_all_btn.setEnabled(True)
            self.merge_selected_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)
    
    def add_log_message(self, message: str, level: str = "INFO"):
        """Ajoute un message aux logs"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Couleurs selon le niveau
        color_map = {
            "INFO": "#00AA00",    # Vert
            "WARNING": "#FFAA00",  # Orange
            "ERROR": "#FF0000",    # Rouge
            "DEBUG": "#888888"     # Gris
        }
        
        color = color_map.get(level, "#000000")
        formatted_message = f'<span style="color: {color}">[{timestamp}] {level}: {message}</span>'
        
        # Ajouter le message à la zone de texte
        self.logs_text.append(formatted_message)
        
        # Auto-scroll vers le bas
        scrollbar = self.logs_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
        
        # Limiter le nombre de lignes (garder les 1000 dernières)
        lines = self.logs_text.toPlainText().split('\n')
        if len(lines) > 1000:
            # Garder seulement les 1000 dernières lignes
            content = '\n'.join(lines[-1000:])
            self.logs_text.setPlainText(content)
    
    def clear_logs(self):
        """Efface tous les logs"""
        self.logs_text.clear()
        self.add_log_message("Logs effacés", "INFO")
    
    def save_logs(self):
        """Sauvegarde les logs dans un fichier"""
        try:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"epub2pdf_logs_{timestamp}.txt"
            
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Sauvegarder les logs",
                filename,
                "Fichiers texte (*.txt);;Tous les fichiers (*)"
            )
            
            if file_path:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.logs_text.toPlainText())
                
                self.add_log_message(f"Logs sauvegardés dans: {file_path}", "INFO")
                QMessageBox.information(self, "Succès", f"Logs sauvegardés dans:\n{file_path}")
        except Exception as e:
            self.add_log_message(f"Erreur lors de la sauvegarde des logs: {e}", "ERROR")
            QMessageBox.warning(self, "Erreur", f"Erreur lors de la sauvegarde:\n{e}")
    
    def update_progress(self, current: int, total: int, message: str):
        """Met à jour la barre de progression et ajoute un message aux logs"""
        if hasattr(self, 'progress_bar'):
            self.progress_bar.setMaximum(total)
            self.progress_bar.setValue(current)
        
        # Ajouter le message aux logs
        self.add_log_message(message, "INFO")
        
        # Mettre à jour le label de statut
        if hasattr(self, 'status_label'):
            self.status_label.setText(message)
    
    def on_file_converted(self, file_info: Dict):
        """Appelé quand un fichier est converti"""
        status = "✅ Réussi" if file_info.get('converted', False) else "❌ Échoué"
        message = f"{status}: {file_info['name']}"
        self.add_log_message(message, "INFO" if file_info.get('converted', False) else "ERROR")
        
        # Mettre à jour l'arbre des fichiers
        self.update_files_tree()
    
    def on_conversion_finished(self, success: bool, message: str):
        """Appelé quand la conversion est terminée"""
        level = "INFO" if success else "ERROR"
        self.add_log_message(message, level)
        
        # Réinitialiser l'interface
        if hasattr(self, 'progress_bar'):
            self.progress_bar.setValue(0)
        
        if hasattr(self, 'status_label'):
            self.status_label.setText("Prêt")
        
        # Réactiver les boutons
        self.convert_selected_btn.setEnabled(True)
        self.convert_all_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        
        # Afficher un message de fin
        if success:
            QMessageBox.information(self, "Conversion terminée", message)
        else:
            QMessageBox.warning(self, "Erreur de conversion", message)
    
    def on_merge_finished(self, success: bool, message: str):
        """Appelé quand la fusion est terminée"""
        level = "INFO" if success else "ERROR"
        self.add_log_message(message, level)
        
        # Réinitialiser l'interface
        if hasattr(self, 'progress_bar'):
            self.progress_bar.setValue(0)
        
        if hasattr(self, 'status_label'):
            self.status_label.setText("Prêt")
        
        # Réactiver les boutons
        self.merge_selected_btn.setEnabled(True)
        self.convert_selected_btn.setEnabled(True)
        self.convert_all_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        
        # Afficher un message de fin
        if success:
            QMessageBox.information(self, "Fusion terminée", message)
        else:
            QMessageBox.warning(self, "Erreur de fusion", message)
    
    def stop_conversion(self):
        """Arrête la conversion ou fusion en cours"""
        if hasattr(self, 'conversion_worker') and self.conversion_worker and self.conversion_worker.isRunning():
            self.conversion_worker.stop()
            self.conversion_worker.wait()
        
        if hasattr(self, 'merge_worker') and self.merge_worker and self.merge_worker.isRunning():
            self.merge_worker.stop()
            self.merge_worker.wait()
        
        self.progress_bar.setVisible(False)
        self.convert_selected_btn.setEnabled(True)
        self.convert_all_btn.setEnabled(True)
        self.merge_selected_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.status_label.setText("Opération arrêtée")
    
    def closeEvent(self, event):
        """Gère la fermeture de l'application"""
        if self.conversion_worker and self.conversion_worker.isRunning():
            reply = QMessageBox.question(
                self, "Confirmation",
                "Une conversion est en cours. Voulez-vous vraiment quitter ?",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.stop_conversion()
                event.accept()
            else:
                event.ignore()
        else:
            # Sauvegarder la configuration avant de fermer
            self.save_current_config()
            event.accept()
    
    def load_saved_config(self):
        """Charge la configuration sauvegardée"""
        try:
            # Charger les options de l'interface
            window_width = self.config_manager.get('window_width', 1200)
            window_height = self.config_manager.get('window_height', 800)
            self.resize(window_width, window_height)
            
            # Charger les chemins
            input_folder = self.config_manager.get('input_folder', '')
            if hasattr(self, 'input_path_edit') and input_folder:
                self.input_path_edit.setText(input_folder)
            
            output_folder = self.config_manager.get('output_folder', '')
            if hasattr(self, 'output_path_edit') and output_folder:
                self.output_path_edit.setText(output_folder)
            
            # Charger les options de conversion
            max_workers = self.config_manager.get('max_workers', 5)
            if hasattr(self, 'workers_spin'):
                self.workers_spin.setValue(max_workers)
            
            # Charger les options de fusion
            merge_volumes = self.config_manager.get('merge_volumes', False)
            if hasattr(self, 'merge_volumes_check'):
                self.merge_volumes_check.setChecked(merge_volumes)
            
            fetch_metadata = self.config_manager.get('fetch_metadata', True)
            if hasattr(self, 'fetch_metadata_check'):
                self.fetch_metadata_check.setChecked(fetch_metadata)
            
            merge_order = self.config_manager.get('merge_order', 'Naturel')
            if hasattr(self, 'merge_order_combo'):
                index = self.merge_order_combo.findText(merge_order)
                if index >= 0:
                    self.merge_order_combo.setCurrentIndex(index)
            
            # Charger les options de conversion
            output_format = self.config_manager.get('output_format', 'PDF')
            if hasattr(self, 'output_format_combo'):
                index = self.output_format_combo.findText(output_format)
                if index >= 0:
                    self.output_format_combo.setCurrentIndex(index)
            
            resize_option = self.config_manager.get('resize_option', 'Aucun')
            if hasattr(self, 'resize_combo'):
                index = self.resize_combo.findText(resize_option)
                if index >= 0:
                    self.resize_combo.setCurrentIndex(index)
            
            grayscale = self.config_manager.get('grayscale', False)
            if hasattr(self, 'grayscale_checkbox'):
                self.grayscale_checkbox.setChecked(grayscale)
            
            optimize = self.config_manager.get('optimize', True)
            if hasattr(self, 'optimize_checkbox'):
                self.optimize_checkbox.setChecked(optimize)
            
            add_metadata = self.config_manager.get('add_metadata', False)
            if hasattr(self, 'add_metadata_checkbox'):
                self.add_metadata_checkbox.setChecked(add_metadata)
            
            # Charger les filtres
            last_search = self.config_manager.get('last_search_term', '')
            if hasattr(self, 'search_edit'):
                self.search_edit.setText(last_search)
            
        except Exception as e:
            self.add_log_message(f"⚠️ Erreur lors du chargement de la configuration: {e}", "ERROR")
    
    def save_current_config(self):
        """Sauvegarde la configuration actuelle"""
        try:
            # Sauvegarder la taille de la fenêtre
            self.config_manager.set('window_width', self.width())
            self.config_manager.set('window_height', self.height())
            
            # Sauvegarder les chemins
            if hasattr(self, 'input_path_edit'):
                input_folder = self.input_path_edit.text()
                self.config_manager.set('input_folder', input_folder)
            
            if hasattr(self, 'output_path_edit'):
                output_folder = self.output_path_edit.text()
                self.config_manager.set('output_folder', output_folder)
            
            # Sauvegarder les options de conversion
            if hasattr(self, 'workers_spin'):
                self.config_manager.set('max_workers', self.workers_spin.value())
            
            # Sauvegarder les options de fusion
            if hasattr(self, 'merge_volumes_check'):
                self.config_manager.set('merge_volumes', self.merge_volumes_check.isChecked())
            
            if hasattr(self, 'fetch_metadata_check'):
                self.config_manager.set('fetch_metadata', self.fetch_metadata_check.isChecked())
            
            if hasattr(self, 'merge_order_combo'):
                merge_order = self.merge_order_combo.currentText()
                self.config_manager.set('merge_order', merge_order)
            
            # Sauvegarder les options de conversion
            if hasattr(self, 'output_format_combo'):
                output_format = self.output_format_combo.currentText()
                self.config_manager.set('output_format', output_format)
            
            if hasattr(self, 'resize_combo'):
                resize_option = self.resize_combo.currentText()
                self.config_manager.set('resize_option', resize_option)
            
            if hasattr(self, 'grayscale_checkbox'):
                self.config_manager.set('grayscale', self.grayscale_checkbox.isChecked())
            
            if hasattr(self, 'optimize_checkbox'):
                self.config_manager.set('optimize', self.optimize_checkbox.isChecked())
            
            if hasattr(self, 'add_metadata_checkbox'):
                self.config_manager.set('add_metadata', self.add_metadata_checkbox.isChecked())
            
            # Sauvegarder les filtres
            if hasattr(self, 'search_edit'):
                search_term = self.search_edit.text()
                self.config_manager.set('last_search_term', search_term)
            
        except Exception as e:
            self.add_log_message(f"⚠️ Erreur lors de la sauvegarde de la configuration: {e}", "ERROR")
    
    def on_config_changed(self):
        """Appelé quand la configuration change"""
        self.save_current_config()
