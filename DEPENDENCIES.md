# 📦 Dépendances EPUB2PDF

Ce document détaille toutes les dépendances du projet EPUB2PDF.

## 🎯 Vue d'ensemble

Le projet utilise trois fichiers de dépendances différents selon les besoins :

- **`requirements.txt`** : Dépendances complètes (recommandé)
- **`requirements-minimal.txt`** : Dépendances minimales uniquement
- **`requirements-dev.txt`** : Dépendances de développement

## 📋 Dépendances principales (requises)

### Interface utilisateur
- **PySide6** `>=6.5.0` : Interface graphique moderne
  - Alternative à tkinter
  - Interface native et performante
  - Support multiplateforme

### Traitement d'images
- **Pillow** `>=10.0.0` : Traitement d'images Python
  - Redimensionnement, conversion, optimisation
  - Support de nombreux formats (JPEG, PNG, etc.)
  - Manipulation de métadonnées

### Manipulation PDF
- **PyPDF2** `>=3.0.0` : Bibliothèque PDF Python
  - Création, fusion, manipulation de PDFs
  - Extraction de métadonnées
  - Compression et optimisation

### Extraction d'archives
- **rarfile** `>=4.0` : Extraction d'archives RAR
  - Support des formats RAR, CBR
  - Extraction automatique des images
  - Gestion des erreurs

### Requêtes HTTP
- **requests** `>=2.28.0` : Bibliothèque HTTP
  - Récupération de métadonnées manga
  - API MyAnimeList et MangaDex
  - Gestion des timeouts et erreurs

## 🔧 Dépendances optionnelles

### Traitement d'images avancé
- **wand** `>=0.6.0` : Interface Python pour ImageMagick
  - Qualité d'image supérieure
  - Formats d'image supplémentaires
  - Optimisations avancées

### Optimisation des performances
- **numba** `>=0.58.0` : Compilation JIT pour Python
  - Accélération des calculs
  - Optimisation des boucles
  - Support GPU (optionnel)

- **psutil** `>=5.9.0` : Monitoring système
  - Surveillance des ressources
  - Optimisation mémoire
  - Gestion des processus

## 🧪 Dépendances de développement

### Tests
- **pytest** `>=7.0.0` : Framework de tests
- **pytest-cov** `>=4.0.0` : Couverture de code
- **pytest-mock** `>=3.10.0` : Mocking pour tests
- **pytest-qt** `>=4.2.0` : Tests d'interface Qt
- **pytest-xdist** `>=3.0.0` : Tests parallèles

### Qualité de code
- **black** `>=22.0.0` : Formateur de code
- **flake8** `>=5.0.0` : Linter Python
- **isort** `>=5.10.0` : Tri des imports
- **mypy** `>=1.0.0` : Vérification de types

### Documentation
- **sphinx** `>=5.0.0` : Génération de documentation
- **sphinx-rtd-theme** `>=1.0.0` : Thème ReadTheDocs

### Outils de développement
- **pre-commit** `>=2.20.0` : Hooks Git
- **tox** `>=4.0.0` : Tests multi-environnements

### Profilage et debugging
- **memory-profiler** `>=0.60.0` : Profilage mémoire
- **line-profiler** `>=3.5.0` : Profilage ligne par ligne
- **ipdb** `>=0.13.0` : Debugger interactif

## 🖥️ Dépendances système

### Extraction d'archives
- **unar** : Extraction d'archives universelle
  - Support RAR, ZIP, 7Z, etc.
  - Installation : `brew install unar` (macOS) ou `apt-get install unar` (Ubuntu)

### Traitement d'images
- **ImageMagick** : Suite de traitement d'images
  - Conversion et optimisation d'images
  - Installation : `brew install imagemagick` (macOS) ou `apt-get install imagemagick` (Ubuntu)

## 📊 Matrice de compatibilité

| Dépendance | Python 3.8 | Python 3.9 | Python 3.10 | Python 3.11 | Python 3.12 |
|------------|------------|------------|-------------|-------------|-------------|
| PySide6    | ✅         | ✅         | ✅          | ✅          | ✅          |
| Pillow     | ✅         | ✅         | ✅          | ✅          | ✅          |
| PyPDF2     | ✅         | ✅         | ✅          | ✅          | ✅          |
| rarfile    | ✅         | ✅         | ✅          | ✅          | ✅          |
| requests   | ✅         | ✅         | ✅          | ✅          | ✅          |
| wand       | ✅         | ✅         | ✅          | ✅          | ✅          |
| numba      | ✅         | ✅         | ✅          | ✅          | ✅          |
| psutil     | ✅         | ✅         | ✅          | ✅          | ✅          |

## 🚀 Installation

### Installation complète
```bash
pip install -r requirements.txt
```

### Installation minimale
```bash
pip install -r requirements-minimal.txt
```

### Installation développement
```bash
pip install -r requirements-dev.txt
```

## 🔍 Vérification

Utilisez le script de vérification pour contrôler l'installation :

```bash
python check_dependencies.py
```

## 🐛 Dépannage

### Problèmes courants

1. **PySide6 non trouvé** :
   ```bash
   pip install PySide6
   ```

2. **Pillow non trouvé** :
   ```bash
   pip install Pillow
   ```

3. **unar non trouvé** :
   ```bash
   # macOS
   brew install unar
   
   # Ubuntu
   sudo apt-get install unar
   ```

4. **ImageMagick non trouvé** :
   ```bash
   # macOS
   brew install imagemagick
   
   # Ubuntu
   sudo apt-get install imagemagick
   ```

### Mise à jour des dépendances

```bash
# Mise à jour de toutes les dépendances
pip install --upgrade -r requirements.txt

# Mise à jour d'une dépendance spécifique
pip install --upgrade PySide6
```

## 📈 Performance

### Recommandations

- **SSD** : Utilisez un SSD pour de meilleures performances
- **RAM** : Minimum 4GB, recommandé 8GB+
- **CPU** : Multi-cœurs recommandé pour le traitement parallèle
- **Antivirus** : Désactivez temporairement pendant la conversion

### Optimisations

- **Workers** : Ajustez le nombre de workers selon votre CPU
- **Cache** : Le cache intelligent améliore les performances
- **Mémoire** : Gestion automatique de la mémoire
- **Compression** : Réduction automatique de la taille des fichiers
