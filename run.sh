#!/bin/bash
# Script de lancement pour EPUB2PDF

# Aller dans le répertoire du projet
cd "$(dirname "$0")"

# Activer l'environnement virtuel
source venv/bin/activate

# Vérifier les dépendances
echo "🔍 Vérification des dépendances..."
python check_dependencies.py

# Lancer l'application
echo "🚀 Lancement de l'application..."
python main.py
