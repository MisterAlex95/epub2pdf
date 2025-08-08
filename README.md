# EPUB2PDF - Convertisseur de Manga/Comics

Application moderne de conversion de fichiers EPUB, CBR et CBZ vers PDF avec interface graphique PySide6.

## 🚀 Fonctionnalités

- **Conversion multi-format** : EPUB, CBR, CBZ → PDF
- **Interface moderne** : Interface graphique intuitive avec PySide6
- **Fusion de fichiers** : Combinez plusieurs chapitres en un seul PDF
- **Traitement par lots** : Conversion de plusieurs fichiers simultanément
- **Métadonnées** : Récupération automatique des informations manga
- **Optimisation** : Redimensionnement, grayscale, compression
- **Sauvegarde de configuration** : Mémorisation des préférences utilisateur

## 📋 Prérequis

### Dépendances système

**macOS :**
```bash
# Installation via Homebrew
brew install unar imagemagick
```

**Ubuntu/Debian :**
```bash
# Installation via apt
sudo apt-get update
sudo apt-get install unar imagemagick
```

**Windows :**
- Téléchargez et installez [UnRAR](https://www.win-rar.com/download.html)
- Téléchargez et installez [ImageMagick](https://imagemagick.org/script/download.php#windows)

### Python

- Python 3.8 ou supérieur
- pip (gestionnaire de paquets Python)

## 🛠️ Installation

### Installation complète (recommandée)

```bash
# Cloner le repository
git clone https://github.com/votre-username/epub2pdf.git
cd epub2pdf

# Créer un environnement virtuel
python -m venv venv

# Activer l'environnement virtuel
# macOS/Linux :
source venv/bin/activate
# Windows :
venv\Scripts\activate

# Installer toutes les dépendances
pip install -r requirements.txt
```

### Installation minimale

```bash
# Installation des dépendances minimales uniquement
pip install -r requirements-minimal.txt
```

### Installation pour le développement

```bash
# Installation avec outils de développement
pip install -r requirements-dev.txt
```

## 🎯 Utilisation

### Lancement de l'application

```bash
python main.py
```

### Interface utilisateur

1. **Onglet Conversion** :
   - Sélectionnez un dossier d'entrée
   - Choisissez un dossier de sortie
   - Sélectionnez les fichiers à convertir
   - Cliquez sur "Convertir la sélection" ou "Convertir tout"

2. **Fusion de fichiers** :
   - Sélectionnez plusieurs fichiers
   - Cliquez sur "Fusionner la sélection"
   - Entrez le nom du fichier fusionné
   - Le PDF fusionné sera créé dans le dossier de sortie

3. **Options** :
   - Format de sortie (PDF)
   - Redimensionnement (A4, A3, etc.)
   - Conversion en niveaux de gris
   - Optimisation et compression
   - Ajout de métadonnées

## 📁 Structure du projet

```
epub2pdf/
├── main.py                 # Point d'entrée principal
├── requirements.txt        # Dépendances complètes
├── requirements-minimal.txt # Dépendances minimales
├── requirements-dev.txt    # Dépendances de développement
├── src/
│   ├── core/              # Logique métier
│   │   ├── converter/     # Convertisseurs
│   │   ├── file_manager.py
│   │   └── metadata_manager.py
│   ├── gui/               # Interface utilisateur
│   │   ├── modern_interface.py
│   │   └── ...
│   └── utils/             # Utilitaires
├── tests/                 # Tests unitaires
├── temp/                  # Fichiers temporaires
└── logs/                  # Fichiers de logs
```

## 🔧 Configuration

### Fichiers de configuration

- `app_config.json` : Configuration de l'application
- `path_config.json` : Chemins par défaut

### Variables d'environnement

- `EPUB2PDF_LOG_LEVEL` : Niveau de log (DEBUG, INFO, WARNING, ERROR)
- `EPUB2PDF_TEMP_DIR` : Dossier temporaire personnalisé

## 🧪 Tests

```bash
# Lancer tous les tests
pytest

# Tests avec couverture
pytest --cov=src

# Tests spécifiques
pytest tests/test_core.py
pytest tests/test_gui.py
```

## 📊 Performance

### Optimisations incluses

- **Traitement parallèle** : Conversion simultanée de plusieurs fichiers
- **Cache intelligent** : Mise en cache des informations de fichiers
- **Optimisation mémoire** : Gestion efficace de la mémoire
- **Compression** : Réduction de la taille des fichiers PDF

### Recommandations

- Utilisez un SSD pour de meilleures performances
- Augmentez le nombre de workers selon votre CPU
- Désactivez l'antivirus temporairement pendant la conversion

## 🐛 Dépannage

### Problèmes courants

1. **Erreur "unar not found"** :
   - Installez unar : `brew install unar` (macOS) ou `apt-get install unar` (Ubuntu)

2. **Erreur "ImageMagick not found"** :
   - Installez ImageMagick : `brew install imagemagick` (macOS) ou `apt-get install imagemagick` (Ubuntu)

3. **Erreur "PySide6 not found"** :
   - Installez PySide6 : `pip install PySide6`

4. **Erreur de permission** :
   - Vérifiez les permissions du dossier de sortie
   - Exécutez en tant qu'administrateur si nécessaire

### Logs

Les logs sont sauvegardés dans `src/logs/` avec la date et l'heure.

## 🤝 Contribution

1. Fork le projet
2. Créez une branche feature (`git checkout -b feature/AmazingFeature`)
3. Commit vos changements (`git commit -m 'Add some AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrez une Pull Request

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 🙏 Remerciements

- [PySide6](https://doc.qt.io/qtforpython/) - Interface utilisateur
- [Pillow](https://python-pillow.org/) - Traitement d'images
- [PyPDF2](https://pypdf2.readthedocs.io/) - Manipulation PDF
- [UnRAR](https://www.rarlab.com/) - Extraction d'archives RAR
