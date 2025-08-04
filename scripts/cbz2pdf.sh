#!/bin/bash

# cbz2pdf.sh - Convert CBZ (Comic Book ZIP) files to PDF
# CBZ files are essentially ZIP archives containing images
# This script extracts CBZ files and converts the images to PDF

set -euo pipefail

# Version
VERSION="1.0.0"

# Debug mode (set to true for verbose logging)
DEBUG=true

# Debug logging function
debug_log() {
    if [ "$DEBUG" = true ]; then
        echo -e "${BLUE}🔍 DEBUG: $1${NC}" >&2
    fi
}

# Default values
INPUT_DIR=""
OUTPUT_DIR="./pdfs"
RECURSIVE=false
FORCE=false
GRAYSCALE=false
RESIZE=""
ZIP_OUTPUT=false
CLEAN_TMP=false
OPEN_OUTPUT_DIR=false
VERBOSE=false
DRY_RUN=false
SINGLE_FILE=""

# Required commands
REQUIRED_CMDS=("unzip" "convert" "zip")

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

debug_log "Script cbz2pdf.sh démarré (v${VERSION})"
debug_log "Répertoire de travail: $(pwd)"
debug_log "Arguments reçus: $*"

# Help function
show_help() {
    cat << EOF
📖 cbz2pdf.sh v${VERSION} - Convert CBZ files to PDF

Usage: $0 [OPTIONS] [CBZ_FILES...]

Options:
    -i, --input-dir DIR        Input directory containing CBZ files
    -o, --output-dir DIR       Output directory for PDF files (default: ./pdfs)
    -r, --recursive            Search for CBZ files in subdirectories
    -f, --force                Overwrite existing PDF files
    -g, --grayscale            Convert images to grayscale (saves ink)
    --resize SIZE              Resize images (ex: A4, 1240x1754, 800x600)
    --zip-output               Create ZIP archive of all PDFs
    --clean-tmp                Clean temporary files (default: true)
    --open-output-dir          Open output directory when done
    -v, --verbose              Verbose output
    --dry-run                  Show what would be done without doing it
    --single-file FILE         Process a single CBZ file
    -h, --help                 Show this help message
    --version                  Show version

Resize options:
    A4, A3, A5                Standard paper sizes
    HD, FHD                    Standard resolutions
    widthxheight               Custom size (ex: 800x600)

Examples:
    $0 --input-dir ./comics --output-dir ./pdfs --recursive
    $0 --input-dir ./manga --grayscale --resize A4
    $0 --input-dir ./books --verbose --dry-run

EOF
}

# Version function
show_version() {
    echo "cbz2pdf.sh v${VERSION}"
}

# Error function
error() {
    echo -e "${RED}❌ Error: $1${NC}" >&2
    exit 1
}

# Warning function
warning() {
    echo -e "${YELLOW}⚠️  Warning: $1${NC}" >&2
}

# Info function
info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Success function
success() {
    echo -e "${GREEN}✅ $1${NC}"
}

# Check dependencies
check_dependencies() {
    debug_log "Vérification des dépendances..."
    for cmd in "${REQUIRED_CMDS[@]}"; do
        debug_log "Vérification de la commande: $cmd"
        if ! command -v "$cmd" &>/dev/null; then
            error "$cmd is required but not installed"
        else
            debug_log "✅ Commande $cmd trouvée: $(which $cmd)"
        fi
    done
    debug_log "✅ Toutes les dépendances sont satisfaites"
}

# Clean filename function
clean_filename() {
    local filename="$1"
    debug_log "Nettoyage du nom de fichier: $filename"
    # Remove or replace problematic characters
    local cleaned=$(echo "$filename" | sed 's/[^a-zA-Z0-9._-]/_/g')
    debug_log "Nom nettoyé: $cleaned"
    echo "$cleaned"
}

# Get resize dimensions
get_resize_dimensions() {
    local size="$1"
    debug_log "Calcul des dimensions de redimensionnement pour: $size"
    case "$size" in
        "A4"|"a4")
            local dims="1240x1754"
            debug_log "Format A4 détecté: $dims"
            echo "$dims"
            ;;
        "A3"|"a3")
            local dims="1754x2480"
            debug_log "Format A3 détecté: $dims"
            echo "$dims"
            ;;
        "A5"|"a5")
            local dims="874x1240"
            debug_log "Format A5 détecté: $dims"
            echo "$dims"
            ;;
        "HD"|"hd")
            local dims="1280x720"
            debug_log "Format HD détecté: $dims"
            echo "$dims"
            ;;
        "FHD"|"fhd")
            local dims="1920x1080"
            debug_log "Format FHD détecté: $dims"
            echo "$dims"
            ;;
        *)
            # Check if it's a valid format (widthxheight)
            if [[ "$size" =~ ^[0-9]+x[0-9]+$ ]]; then
                debug_log "Format personnalisé détecté: $size"
                echo "$size"
            else
                error "Invalid size format: $size"
                echo "Supported formats: A4, A3, A5, HD, FHD, or widthxheight (ex: 800x600)"
                exit 1
            fi
            ;;
    esac
}

# Progress bar function
show_progress() {
    local current=$1
    local total=$2
    local width=50
    local percentage=$((current * 100 / total))
    local completed=$((width * current / total))
    local remaining=$((width - completed))
    
    printf "\r["
    printf "%${completed}s" | tr ' ' '#'
    printf "%${remaining}s" | tr ' ' '-'
    printf "] %d%% (%d/%d)" "$percentage" "$current" "$total"
}

# Parse command line arguments
debug_log "Début du parsing des arguments..."
while [[ $# -gt 0 ]]; do
    case $1 in
        -i|--input-dir)
            INPUT_DIR="$2"
            debug_log "Répertoire d'entrée défini: $INPUT_DIR"
            shift 2
            ;;
        -o|--output-dir)
            OUTPUT_DIR="$2"
            debug_log "Répertoire de sortie défini: $OUTPUT_DIR"
            shift 2
            ;;
        -r|--recursive)
            RECURSIVE=true
            debug_log "Mode récursif activé"
            shift
            ;;
        -f|--force)
            FORCE=true
            debug_log "Mode force activé"
            shift
            ;;
        -g|--grayscale)
            GRAYSCALE=true
            debug_log "Mode grayscale activé"
            shift
            ;;
        --resize)
            RESIZE="$2"
            debug_log "Taille de redimensionnement définie: $RESIZE"
            shift 2
            ;;
        --zip-output)
            ZIP_OUTPUT=true
            debug_log "Mode zip activé"
            shift
            ;;
        --clean-tmp)
            CLEAN_TMP=true
            debug_log "Mode nettoyage temporaire activé"
            shift
            ;;
        --open-output-dir)
            OPEN_OUTPUT_DIR=true
            debug_log "Mode ouverture répertoire activé"
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            debug_log "Mode verbose activé"
            shift
            ;;
        --dry-run)
            DRY_RUN=true
            debug_log "Mode dry-run activé"
            shift
            ;;
        --single-file)
            SINGLE_FILE="$2"
            debug_log "Fichier unique défini: $SINGLE_FILE"
            shift 2
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        --version)
            show_version
            exit 0
            ;;
        -*)
            error "Unknown option: $1"
            ;;
        *)
            break
            ;;
    esac
done

debug_log "Parsing des arguments terminé"
debug_log "Options finales:"
debug_log "  INPUT_DIR=$INPUT_DIR"
debug_log "  OUTPUT_DIR=$OUTPUT_DIR"
debug_log "  RECURSIVE=$RECURSIVE"
debug_log "  FORCE=$FORCE"
debug_log "  GRAYSCALE=$GRAYSCALE"
debug_log "  RESIZE=$RESIZE"
debug_log "  ZIP_OUTPUT=$ZIP_OUTPUT"
debug_log "  CLEAN_TMP=$CLEAN_TMP"
debug_log "  OPEN_OUTPUT_DIR=$OPEN_OUTPUT_DIR"
debug_log "  VERBOSE=$VERBOSE"
debug_log "  DRY_RUN=$DRY_RUN"
debug_log "  SINGLE_FILE=$SINGLE_FILE"

# Check dependencies
check_dependencies

# Validate input directory
if [[ -n "$INPUT_DIR" ]]; then
    debug_log "Validation du répertoire d'entrée: $INPUT_DIR"
    if [[ ! -d "$INPUT_DIR" ]]; then
        error "Input directory does not exist: $INPUT_DIR"
    else
        debug_log "✅ Répertoire d'entrée valide: $INPUT_DIR"
    fi
fi

# Create output directory
debug_log "Vérification du répertoire de sortie: $OUTPUT_DIR"
if [[ ! -d "$OUTPUT_DIR" ]]; then
    if [[ "$DRY_RUN" == false ]]; then
        debug_log "Création du répertoire de sortie: $OUTPUT_DIR"
        mkdir -p "$OUTPUT_DIR"
        success "Created output directory: $OUTPUT_DIR"
    else
        info "Would create output directory: $OUTPUT_DIR"
    fi
else
    debug_log "✅ Répertoire de sortie existe déjà: $OUTPUT_DIR"
fi

# Find CBZ files
debug_log "Recherche des fichiers CBZ..."
CBZS=()

# Check if files were passed as arguments
if [[ $# -gt 0 ]]; then
    debug_log "Arguments restants après parsing: $*"
    # Process each argument
    for arg in "$@"; do
        if [[ -f "$arg" ]]; then
            # It's a file - convert just this file
            debug_log "Fichier détecté: $arg"
            CBZS+=("$arg")
            debug_log "Fichier CBZ ajouté: $arg"
        elif [[ -d "$arg" ]]; then
            # It's a directory - find all CBZ files in it
            debug_log "Répertoire détecté: $arg"
            if [[ "$RECURSIVE" == true ]]; then
                debug_log "Mode récursif: recherche dans tous les sous-répertoires"
                while IFS= read -r -d '' file; do
                    CBZS+=("$file")
                    debug_log "Fichier CBZ trouvé: $file"
                done < <(find "$arg" -name "*.cbz" -print0 2>/dev/null)
            else
                debug_log "Mode non-récursif: recherche uniquement dans le répertoire principal"
                while IFS= read -r -d '' file; do
                    CBZS+=("$file")
                    debug_log "Fichier CBZ trouvé: $file"
                done < <(find "$arg" -maxdepth 1 -name "*.cbz" -print0 2>/dev/null)
            fi
        else
            debug_log "❌ Argument invalide: $arg (ni fichier ni répertoire)"
            warning "Invalid argument: $arg (not a file or directory)"
        fi
    done
else
    # No arguments, search in input directory
    if [[ -n "$INPUT_DIR" ]]; then
        debug_log "Recherche dans le répertoire: $INPUT_DIR"
        if [[ "$RECURSIVE" == true ]]; then
            debug_log "Mode récursif: recherche dans tous les sous-répertoires"
            while IFS= read -r -d '' file; do
                CBZS+=("$file")
                debug_log "Fichier CBZ trouvé: $file"
            done < <(find "$INPUT_DIR" -name "*.cbz" -print0 2>/dev/null)
        else
            debug_log "Mode non-récursif: recherche uniquement dans le répertoire principal"
            while IFS= read -r -d '' file; do
                CBZS+=("$file")
                debug_log "Fichier CBZ trouvé: $file"
            done < <(find "$INPUT_DIR" -maxdepth 1 -name "*.cbz" -print0 2>/dev/null)
        fi
    fi
fi

# Filter out empty entries
CBZS=("${CBZS[@]:+${CBZS[@]}}")

debug_log "Total des fichiers CBZ trouvés: ${#CBZS[@]}"

if [[ ${#CBZS[@]} -eq 0 ]]; then
    error "No CBZ files found"
fi

# Show what we found
if [[ "$VERBOSE" == true ]]; then
    info "Found ${#CBZS[@]} CBZ file(s):"
    for cbz in "${CBZS[@]}"; do
        echo "  - $cbz"
    done
    echo
fi

# Process each CBZ file
debug_log "Début du traitement des fichiers CBZ..."
for cbz in "${CBZS[@]}"; do
    debug_log "Traitement du fichier: $cbz"
    
    if [[ ! -f "$cbz" ]]; then
        debug_log "❌ Fichier non trouvé: $cbz"
        warning "File not found: $cbz"
        continue
    fi
    
    debug_log "✅ Fichier trouvé: $cbz"
    
    # Get base filename
    BASENAME=$(basename "$cbz" .cbz)
    CLEAN_BASENAME=$(clean_filename "$BASENAME")
    OUTPUT_PDF="$OUTPUT_DIR/${CLEAN_BASENAME}.pdf"
    
    debug_log "Nom de base: $BASENAME"
    debug_log "Nom nettoyé: $CLEAN_BASENAME"
    debug_log "Fichier de sortie: $OUTPUT_PDF"
    
    # Check if output already exists
    if [[ -f "$OUTPUT_PDF" && "$FORCE" == false ]]; then
        debug_log "⚠️ Fichier de sortie existe déjà: $OUTPUT_PDF"
        warning "Output file already exists, skipping: $OUTPUT_PDF"
        continue
    fi
    
    if [[ "$DRY_RUN" == true ]]; then
        debug_log "Mode dry-run: simulation de la conversion"
        info "Would convert: $cbz -> $OUTPUT_PDF"
        continue
    fi
    
    debug_log "🚀 Début de la conversion: $cbz"
    info "Converting: $cbz"
    
    # Create temporary directory
    debug_log "Création du répertoire temporaire..."
    TMP_DIR=$(mktemp -d)
    TMP_EXTRACT_DIR="$TMP_DIR/extract"
    TMP_IMG_DIR="$TMP_DIR/images"
    
    debug_log "Répertoire temporaire: $TMP_DIR"
    debug_log "Répertoire d'extraction: $TMP_EXTRACT_DIR"
    debug_log "Répertoire d'images: $TMP_IMG_DIR"
    
    mkdir -p "$TMP_EXTRACT_DIR" "$TMP_IMG_DIR"
    
    # Extract CBZ file (CBZ is just a ZIP file)
    debug_log "Extraction du fichier CBZ..."
    if [[ "$VERBOSE" == true ]]; then
        info "Extracting CBZ file..."
    fi
    
    if ! unzip -q "$cbz" -d "$TMP_EXTRACT_DIR"; then
        debug_log "❌ Échec de l'extraction: $cbz"
        error "Failed to extract CBZ file: $cbz"
        continue
    fi
    
    debug_log "✅ Extraction réussie"
    
    # Find all image files
    debug_log "Recherche des fichiers d'images..."
    IMG_FILES=()
    while IFS= read -r -d '' img; do
        IMG_FILES+=("$img")
        debug_log "Image trouvée: $img"
    done < <(find "$TMP_EXTRACT_DIR" -type f \( -iname "*.jpg" -o -iname "*.jpeg" -o -iname "*.png" -o -iname "*.gif" -o -iname "*.bmp" -o -iname "*.tiff" -o -iname "*.webp" \) -print0 | sort -z)
    
    debug_log "Total des images trouvées: ${#IMG_FILES[@]}"
    
    if [[ ${#IMG_FILES[@]} -eq 0 ]]; then
        debug_log "❌ Aucune image trouvée dans le CBZ"
        warning "No image files found in CBZ: $cbz"
        continue
    fi
    
    if [[ "$VERBOSE" == true ]]; then
        info "Found ${#IMG_FILES[@]} image files"
    fi
    
    # Limit number of images to prevent memory issues
    MAX_IMAGES=1000
    if [[ ${#IMG_FILES[@]} -gt $MAX_IMAGES ]]; then
        warning "Too many images (${#IMG_FILES[@]}), limiting to $MAX_IMAGES"
        IMG_FILES=("${IMG_FILES[@]:0:$MAX_IMAGES}")
    fi
    
    # Prepare conversion arguments
    CONVERT_ARGS=()
    if [[ -n "$RESIZE" ]]; then
        RESIZE_DIMS=$(get_resize_dimensions "$RESIZE")
        CONVERT_ARGS+=("-resize" "${RESIZE_DIMS}^" "-gravity" "center" "-extent" "$RESIZE_DIMS")
    fi
    if [[ "$GRAYSCALE" == true ]]; then
        CONVERT_ARGS+=("-colorspace" "Gray")
    fi
    CONVERT_ARGS+=("-quality" "100")
    
    # Convert images to PDF
    if [[ "$VERBOSE" == true ]]; then
        info "Converting images to PDF..."
    fi
    
    # Process images in batches to avoid memory issues
    BATCH_SIZE=20
    TOTAL_IMAGES=${#IMG_FILES[@]}
    BATCHES=$(( (TOTAL_IMAGES + BATCH_SIZE - 1) / BATCH_SIZE ))
    
    for ((BATCH=0; BATCH<BATCHES; BATCH++)); do
        START=$((BATCH * BATCH_SIZE))
        END=$((START + BATCH_SIZE))
        if [[ $END -gt $TOTAL_IMAGES ]]; then
            END=$TOTAL_IMAGES
        fi
        
        BATCH_FILES=("${IMG_FILES[@]:START:END-START}")
        
        if [[ "$VERBOSE" == true ]]; then
            show_progress $((BATCH + 1)) $BATCHES
        fi
        
        # Create temporary file list for this batch
        GROUP_FILE="$TMP_DIR/group_${BATCH}.txt"
        for img in "${BATCH_FILES[@]}"; do
            echo "$img" >> "$GROUP_FILE"
        done
        
        # Convert this batch
        if ! convert @"$GROUP_FILE" "${CONVERT_ARGS[@]}" "$TMP_IMG_DIR/batch_${BATCH}.pdf" >/dev/null 2>&1; then
            warning "Failed to convert batch $((BATCH + 1))"
            continue
        fi
    done
    
    if [[ "$VERBOSE" == true ]]; then
        echo  # New line after progress bar
    fi
    
    # Combine all batch PDFs into final PDF
    if [[ "$VERBOSE" == true ]]; then
        info "Combining PDFs..."
    fi
    
    BATCH_PDFS=()
    for ((BATCH=0; BATCH<BATCHES; BATCH++)); do
        if [[ -f "$TMP_IMG_DIR/batch_${BATCH}.pdf" ]]; then
            BATCH_PDFS+=("$TMP_IMG_DIR/batch_${BATCH}.pdf")
        fi
    done
    
    if [[ ${#BATCH_PDFS[@]} -eq 0 ]]; then
        error "No PDFs created"
        continue
    fi
    
    # Create final PDF
    if ! convert "${BATCH_PDFS[@]}" "$OUTPUT_PDF" >/dev/null 2>&1; then
        error "Failed to create final PDF: $OUTPUT_PDF"
        continue
    fi
    
    success "Created: $OUTPUT_PDF"
    
    # Clean up temporary files
    if [[ "$CLEAN_TMP" == true ]]; then
        rm -rf "$TMP_DIR"
    fi
done

# Create ZIP archive if requested
if [[ "$ZIP_OUTPUT" == true && "$DRY_RUN" == false ]]; then
    if [[ "$VERBOSE" == true ]]; then
        info "Creating ZIP archive..."
    fi
    
    ZIP_NAME="$OUTPUT_DIR/cbz_pdfs.zip"
    if [[ -f "$ZIP_NAME" ]]; then
        rm "$ZIP_NAME"
    fi
    
    if zip -q -r "$ZIP_NAME" "$OUTPUT_DIR" -i "*.pdf"; then
        success "Created ZIP archive: $ZIP_NAME"
    else
        warning "Failed to create ZIP archive"
    fi
fi

# Open output directory if requested
if [[ "$OPEN_OUTPUT_DIR" == true && "$DRY_RUN" == false ]]; then
    if command -v open &>/dev/null; then
        open "$OUTPUT_DIR"
    elif command -v xdg-open &>/dev/null; then
        xdg-open "$OUTPUT_DIR"
    fi
fi

success "Conversion completed!"

exit 0 