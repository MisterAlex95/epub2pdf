# Module Convertisseur Modulaire

Ce module a été refactorisé pour une meilleure organisation et maintenabilité du code.

## Structure

```
src/core/converter/
├── __init__.py              # Exports publics du module
├── base_converter.py        # Classe de base avec fonctionnalités communes
├── extractor.py             # Extraction CBR/CBZ
├── image_processor.py       # Traitement d'images et conversion PDF
├── pdf_merger.py           # Fusion de PDFs
├── native_converter.py     # Convertisseur principal (orchestrateur)
└── README.md              # Cette documentation
```

## Composants

### BaseConverter (`base_converter.py`)
- Classe de base pour tous les convertisseurs
- Gestion des dépendances (Pillow, Wand, PyPDF2, unar)
- Utilitaires communs (tri naturel, vérification fichiers)
- Configuration du répertoire temporaire

### Extractor (`extractor.py`)
- Extraction des fichiers CBR avec `rarfile` et `unar`
- Extraction des fichiers CBZ avec `zipfile`
- Gestion des fichiers temporaires
- Déduplication des images extraites

### ImageProcessor (`image_processor.py`)
- Conversion d'images en PDF avec Pillow
- Traitement des options (grayscale, resize)
- Division en groupes pour optimiser la mémoire
- Gestion des erreurs de conversion

### PDFMerger (`pdf_merger.py`)
- Fusion de PDFs temporaires avec PyPDF2
- Fallback vers copie simple si PyPDF2 échoue
- Nettoyage des fichiers temporaires
- Validation des PDFs créés

### NativeConverter (`native_converter.py`)
- Orchestrateur principal
- Interface unifiée pour CBR/CBZ/EPUB
- Gestion des chemins de sortie
- Nettoyage automatique des fichiers temporaires

## Avantages de la Refactorisation

1. **Séparation des responsabilités** : Chaque module a une fonction claire
2. **Maintenabilité** : Code plus facile à modifier et déboguer
3. **Testabilité** : Chaque composant peut être testé indépendamment
4. **Réutilisabilité** : Les composants peuvent être utilisés séparément
5. **Lisibilité** : Code plus organisé et documenté

## Utilisation

```python
from src.core.converter import NativeConverter

# Créer le convertisseur
converter = NativeConverter(max_workers=5)

# Convertir un CBR
success, message = converter.convert_cbr_to_pdf(
    "input.cbr", 
    "output.pdf", 
    options={"grayscale": True}
)

# Convertir un CBZ
success, message = converter.convert_cbz_to_pdf(
    "input.cbz", 
    "output.pdf", 
    options={"resize": "A4"}
)
```

## Compatibilité

Le fichier `src/core/converter.py` maintient la compatibilité avec l'ancien import :
```python
from .converter import NativeConverter  # Fonctionne toujours
```

## Dépendances

- **Pillow** : Traitement d'images
- **PyPDF2** : Manipulation de PDFs
- **rarfile** : Extraction de fichiers RAR
- **Wand** : Alternative pour le traitement d'images (optionnel)
- **unar** : Extraction rapide de RAR (optionnel)
