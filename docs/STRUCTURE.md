# 🏗️ Structure Modulaire du Projet

## 📁 Organisation des Fichiers

### 🔧 Modules de Configuration
- **`config.py`** - Configuration centralisée
  - Constantes de version et métadonnées
  - Schéma de couleurs
  - Configuration des formats de fichiers
  - Options de redimensionnement
  - Paramètres par défaut
  - Raccourcis clavier
  - Messages de statut

### 🎨 Composants d'Interface
- **`ui_components.py`** - Composants UI réutilisables
  - Configuration de fenêtre et thème
  - Création d'en-tête
  - Frame des répertoires
  - Frame des options
  - Frame des boutons
  - Frame de progression
  - Frame de logs
  - Barre de statut
  - Menu de l'application

### 📋 Gestion des Onglets
- **`tab_converter.py`** - Gestionnaire d'onglets
  - Classe `TabConverter` pour chaque format
  - Scan de fichiers par format
  - Compteur de fichiers en temps réel
  - Interface d'onglet compacte

### ⚙️ Gestion des Conversions
- **`conversion_manager.py`** - Gestionnaire de conversions
  - Construction de commandes
  - Conversion de fichiers individuels
  - Conversion séquentielle
  - Conversion parallèle
  - Gestion des erreurs

### 💾 Gestion des Paramètres
- **`settings_manager.py`** - Gestionnaire de paramètres
  - Chargement/sauvegarde des paramètres
  - Fusion avec les valeurs par défaut
  - Gestion des erreurs de fichier
  - Réinitialisation des paramètres

### 🖥️ Interface Principale
- **`unified_gui.py`** - Interface unifiée
  - Point d'entrée principal
  - Orchestration des modules
  - Gestion des événements
  - Threading pour les conversions
  - Interface utilisateur complète

## 🔄 Flux de Données

```
config.py → ui_components.py → unified_gui.py
     ↓              ↓              ↓
settings_manager.py ← conversion_manager.py
     ↓              ↓
tab_converter.py ← unified_gui.py
```

## 🎯 Avantages de la Nouvelle Structure

### ✅ **Modularité**
- Chaque module a une responsabilité unique
- Code facilement testable et maintenable
- Réutilisation des composants

### ✅ **Maintenabilité**
- Code organisé et documenté
- Séparation claire des préoccupations
- Facile d'ajouter de nouvelles fonctionnalités

### ✅ **Extensibilité**
- Ajout facile de nouveaux formats
- Configuration centralisée
- Composants réutilisables

### ✅ **Lisibilité**
- Code bien structuré
- Documentation intégrée
- Noms de variables et fonctions explicites

## 🚀 Utilisation

### Import des Modules
```python
from config import VERSION, COLORS, FILE_FORMATS
from ui_components import UIComponents
from tab_converter import TabConverter
from conversion_manager import ConversionManager
from settings_manager import SettingsManager
```

### Configuration
```python
# Charger les paramètres
settings_manager = SettingsManager()
settings = settings_manager.load_settings()

# Utiliser la configuration
colors = COLORS
formats = FILE_FORMATS
```

### Composants UI
```python
# Créer un composant
header = UIComponents.create_header_frame(parent)
buttons = UIComponents.create_buttons_frame(parent, commands)
```

### Conversions
```python
# Convertir des fichiers
options = {'output_dir': './pdfs', 'grayscale': True}
ConversionManager.convert_single_file(file_path, 'epub', options)
```

## 📊 Comparaison Avant/Après

| Aspect | Avant | Après |
|--------|-------|-------|
| **Fichiers** | 1 fichier monolithique | 6 modules spécialisés |
| **Lignes de code** | 858 lignes | 440 lignes (interface principale) |
| **Responsabilités** | Tout mélangé | Séparées par module |
| **Maintenance** | Difficile | Facile |
| **Tests** | Impossible | Facile |
| **Extensibilité** | Limitée | Illimitée |

## 🔧 Ajout de Nouveaux Formats

Pour ajouter un nouveau format (ex: PDF vers TXT) :

1. **Ajouter dans `config.py`** :
```python
FILE_FORMATS = {
    # ... formats existants ...
    'pdf': {
        'name': 'PDF',
        'icon': '📄',
        'script': 'pdf2txt.sh',
        'description': 'PDF to text conversion'
    }
}
```

2. **Créer le script de conversion** : `pdf2txt.sh`

3. **L'interface se met à jour automatiquement** !

## 🎉 Résultat

Le projet est maintenant **parfaitement organisé**, **facilement maintenable** et **extensible** avec une architecture modulaire professionnelle ! 🏆 