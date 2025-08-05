#!/bin/bash

# epub2pdf.sh - Convert EPUB files to PDF
# EPUB files are essentially ZIP archives containing HTML/CSS content
# This script extracts EPUB files and converts the content to PDF

set -euo pipefail

# Version
VERSION="2.0.0"

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
EDIT_METADATA=false
AUTO_RENAME=false
PARALLEL=false
MAX_WORKERS=4

# Metadata variables
PDF_TITLE=""
PDF_AUTHOR=""
PDF_SUBJECT=""
PDF_KEYWORDS=""

# Required commands
REQUIRED_CMDS=("unzip" "convert" "zip" "ebook-convert")

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

debug_log "Script epub2pdf.sh démarré (v${VERSION})"
debug_log "Répertoire de travail: $(pwd)"
debug_log "Arguments reçus: $*"

# Help function
show_help() {
    cat << EOF
📖 epub2pdf.sh v${VERSION} - Convert EPUB files to PDF

Usage: $0 [OPTIONS] [EPUB_FILES...]

Options:
    -i, --input-dir DIR        Input directory containing EPUB files
    -o, --output-dir DIR       Output directory for PDF files (default: ./pdfs)
    -r, --recursive            Search for EPUB files in subdirectories
    -f, --force                Overwrite existing PDF files
    -g, --grayscale            Convert images to grayscale (saves ink)
    --resize SIZE              Resize images (ex: A4, 1240x1754, 800x600)
    --zip-output               Create ZIP archive of all PDFs
    --clean-tmp                Clean temporary files (default: true)
    --open-output-dir          Open output directory when done
    -v, --verbose              Verbose output
    --dry-run                  Show what would be done without doing it
    --single-file FILE         Process a single EPUB file
    --edit-metadata            Edit PDF metadata after conversion
    --auto-rename              Auto-rename files based on content
    --parallel                 Enable parallel processing
    --max-workers N            Maximum number of parallel workers (default: 4)
    -h, --help                 Show this help message
    --version                  Show version

Resize options:
    A4, A3, A5                Standard paper sizes
    HD, FHD                    Standard resolutions
    widthxheight               Custom size (ex: 800x600)

Examples:
    $0 --input-dir ./books --output-dir ./pdfs --recursive
    $0 --input-dir ./ebooks --grayscale --resize A4
    $0 --input-dir ./library --verbose --dry-run
    $0 --single-file "book.epub" --output-dir ./pdfs --edit-metadata

EOF
}

# Simple argument parsing
debug_log "Début du parsing des arguments..."
while [[ $# -gt 0 ]]; do
  case "$1" in
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
      debug_log "Redimensionnement défini: $RESIZE"
      shift 2
      ;;
    --zip-output)
      ZIP_OUTPUT=true
      debug_log "Mode ZIP activé"
      shift
      ;;
    --clean-tmp)
      CLEAN_TMP=true
      debug_log "Nettoyage temporaire activé"
      shift
      ;;
    --open-output-dir)
      OPEN_OUTPUT_DIR=true
      debug_log "Ouverture du répertoire de sortie activée"
      shift
      ;;
    --single-file)
      SINGLE_FILE="$2"
      debug_log "Fichier EPUB unique défini: $SINGLE_FILE"
      shift 2
      ;;
    --edit-metadata)
      EDIT_METADATA=true
      debug_log "Édition des métadonnées PDF activée"
      shift
      ;;
    --auto-rename)
      AUTO_RENAME=true
      debug_log "Auto-renommage des fichiers activé"
      shift
      ;;
    --parallel)
      PARALLEL=true
      debug_log "Traitement parallèle activé"
      shift
      ;;
    --max-workers)
      MAX_WORKERS="$2"
      debug_log "Nombre de workers parallèles défini: $MAX_WORKERS"
      shift 2
      ;;
    --pdf-title)
      PDF_TITLE="$2"
      debug_log "Titre PDF défini: $PDF_TITLE"
      shift 2
      ;;
    --pdf-author)
      PDF_AUTHOR="$2"
      debug_log "Auteur PDF défini: $PDF_AUTHOR"
      shift 2
      ;;
    --pdf-subject)
      PDF_SUBJECT="$2"
      debug_log "Sujet PDF défini: $PDF_SUBJECT"
      shift 2
      ;;
    --pdf-keywords)
      PDF_KEYWORDS="$2"
      debug_log "Mots-clés PDF définis: $PDF_KEYWORDS"
      shift 2
      ;;
    --dry-run)
      DRY_RUN=true
      debug_log "Mode dry-run activé"
      shift
      ;;
    -v|--verbose)
      VERBOSE=true
      debug_log "Mode verbose activé"
      shift
      ;;
    --version)
      echo "epub2pdf.sh v${VERSION}"
      exit 0
      ;;
    -h|--help)
      show_help
      exit 0
      ;;
    *)
      # Check if it's a file path
      if [[ -f "$1" && "$1" == *.epub ]]; then
        EPUBS+=("$1")
        debug_log "Fichier EPUB trouvé: $1"
        shift
      else
        echo "❌ Unknown option: $1"
        echo "Use --help to see available options"
        exit 1
      fi
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
debug_log "  EDIT_METADATA=$EDIT_METADATA"
debug_log "  AUTO_RENAME=$AUTO_RENAME"
debug_log "  PARALLEL=$PARALLEL"
debug_log "  MAX_WORKERS=$MAX_WORKERS"

# Check dependencies
debug_log "Vérification des dépendances..."
for cmd in "${REQUIRED_CMDS[@]}"; do
  debug_log "Vérification de la commande: $cmd"
  if ! command -v "$cmd" &>/dev/null; then
    echo "❌ Missing dependency: $cmd"
    echo "💡 Install dependencies with: ./install-epub2pdf.sh"
    exit 1
  else
    debug_log "✅ Commande $cmd trouvée: $(which $cmd)"
  fi
done
debug_log "✅ Toutes les dépendances sont satisfaites"

# Path validation
if [[ -n "$INPUT_DIR" && ! -d "$INPUT_DIR" ]]; then
  echo "❌ Input directory does not exist: $INPUT_DIR"
  exit 1
fi

# Find EPUB files
if [[ -n "$SINGLE_FILE" ]]; then
    # Single file mode
    if [[ -f "$SINGLE_FILE" ]]; then
        EPUBS=("$SINGLE_FILE")
        debug_log "Fichier unique spécifié: $SINGLE_FILE"
    else
        error "Single file not found: $SINGLE_FILE"
    fi
elif [[ -n "$INPUT_DIR" ]]; then
    # Directory mode
    if [[ ! -d "$INPUT_DIR" ]]; then
        error "Input directory does not exist: $INPUT_DIR"
    fi
    
    if $RECURSIVE; then
        IFS=$'\n' EPUBS=($(find "$INPUT_DIR" -type f -name "*.epub"))
    else
        IFS=$'\n' EPUBS=($(find "$INPUT_DIR" -maxdepth 1 -type f -name "*.epub"))
    fi
else
    # Check if files were passed as arguments
    if [[ $# -gt 0 ]]; then
        debug_log "Arguments passés: $*"
        # Process each argument
        for arg in "$@"; do
            if [[ -f "$arg" && "$arg" == *.epub ]]; then
                EPUBS+=("$arg")
                debug_log "Fichier EPUB trouvé: $arg"
            fi
        done
    fi
fi

TOTAL=${#EPUBS[@]}
if [ "$TOTAL" -eq 0 ]; then
  echo "⚠️ No .epub files found in $INPUT_DIR"
  exit 0
fi

mkdir -p "$OUTPUT_DIR"

# Progress bar
progress_bar() {
  current=$1
  total=$2
  width=40
  filled=$(( current * width / total ))
  empty=$(( width - filled ))
  percent=$(( current * 100 / total ))
  printf "\r["
  for ((j=0; j<filled; j++)); do printf "█"; done
  for ((j=0; j<empty; j++)); do printf " "; done
  printf "] %3d%% (%d/%d)" $percent $current $total
}

# Function to clean filenames
clean_filename() {
  echo "$1" | sed 's/[^a-zA-Z0-9._-]/_/g'
}

# Function to get resize dimensions
get_resize_dimensions() {
  local size="$1"
  case "$size" in
    "A4"|"a4")
      echo "1240x1754"
      ;;
    "A3"|"a3")
      echo "1754x2480"
      ;;
    "A5"|"a5")
      echo "874x1240"
      ;;
    "HD"|"hd")
      echo "1280x720"
      ;;
    "FHD"|"fhd")
      echo "1920x1080"
      ;;
    *)
      echo "$size"
      ;;
  esac
}

# Function to edit PDF metadata
edit_pdf_metadata() {
    local pdf_file="$1"
    local original_name="$2"
    
    if [[ "$EDIT_METADATA" == false ]]; then
        return 0
    fi
    
    debug_log "Édition des métadonnées pour: $pdf_file"
    
    # Check if exiftool is available
    if ! command -v exiftool &> /dev/null; then
        debug_log "⚠️ exiftool non disponible, métadonnées non modifiées"
        warning "exiftool not found, metadata not modified"
        return 0
    fi
    
    # Extract title from filename
    local title=$(basename "$original_name" .epub | sed 's/_/ /g' | sed 's/-/ /g')
    
    # Set metadata
    if exiftool -overwrite_original \
        -Title="$title" \
        -Author="Converted with epub2pdf.sh" \
        -Subject="E-Book" \
        -Keywords="epub,ebook,PDF" \
        -Creator="epub2pdf.sh v$VERSION" \
        "$pdf_file" > /dev/null 2>&1; then
        debug_log "✅ Métadonnées mises à jour pour: $pdf_file"
        info "Metadata updated for: $pdf_file"
    else
        debug_log "❌ Échec de la mise à jour des métadonnées"
        warning "Failed to update metadata for: $pdf_file"
    fi
}

# Function to auto-rename PDF based on content
auto_rename_pdf() {
    local pdf_file="$1"
    local original_name="$2"
    
    if [[ "$AUTO_RENAME" == false ]]; then
        return 0
    fi
    
    debug_log "Renommage automatique pour: $pdf_file"
    
    # Extract series and volume information from filename
    local basename=$(basename "$original_name" .epub)
    
    # Common patterns for ebook naming
    local new_name=""
    
    # Pattern: Series T.X
    if [[ $basename =~ ^(.+)\s+T\.([0-9]+) ]]; then
        local series="${BASH_REMATCH[1]}"
        local volume="${BASH_REMATCH[2]}"
        new_name="${series} T${volume}.pdf"
    # Pattern: Series Vol.X
    elif [[ $basename =~ ^(.+)\s+Vol\.([0-9]+) ]]; then
        local series="${BASH_REMATCH[1]}"
        local volume="${BASH_REMATCH[2]}"
        new_name="${series} Vol${volume}.pdf"
    else
        # Default: clean up the name
        new_name=$(echo "$basename" | sed 's/_/ /g' | sed 's/-/ /g').pdf
    fi
    
    if [[ -n "$new_name" && "$new_name" != "$(basename "$pdf_file")" ]]; then
        local new_path="$OUTPUT_DIR/$new_name"
        if mv "$pdf_file" "$new_path" 2>/dev/null; then
            debug_log "✅ Renommé: $pdf_file -> $new_path"
            info "Renamed: $pdf_file -> $new_path"
        else
            debug_log "❌ Échec du renommage: $pdf_file"
            warning "Failed to rename: $pdf_file"
        fi
    fi
}

# Info function
info() {
    echo -e "${GREEN}✅ $1${NC}"
}

# Warning function
warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Success function
success() {
    echo -e "${GREEN}✅ $1${NC}"
}

# Function to apply PDF metadata
apply_pdf_metadata() {
  local pdf_file="$1"
  
  # Check if exiftool is available
  if ! command -v exiftool &>/dev/null; then
    echo "⚠️ exiftool not found, skipping metadata"
    return
  fi
  
  # Build exiftool command
  local exif_cmd="exiftool -overwrite_original"
  
  if [[ -n "$PDF_TITLE" ]]; then
    exif_cmd="$exif_cmd -Title='$PDF_TITLE'"
  fi
  
  if [[ -n "$PDF_AUTHOR" ]]; then
    exif_cmd="$exif_cmd -Author='$PDF_AUTHOR'"
  fi
  
  if [[ -n "$PDF_SUBJECT" ]]; then
    exif_cmd="$exif_cmd -Subject='$PDF_SUBJECT'"
  fi
  
  if [[ -n "$PDF_KEYWORDS" ]]; then
    exif_cmd="$exif_cmd -Keywords='$PDF_KEYWORDS'"
  fi
  
  # Apply metadata if any is set
  if [[ "$exif_cmd" != "exiftool -overwrite_original" ]]; then
    if [[ "$VERBOSE" == true ]]; then
      echo "Applying metadata to: $pdf_file"
    fi
    
    if ! eval "$exif_cmd" "$pdf_file" >/dev/null 2>&1; then
      echo "⚠️ Failed to apply metadata to: $pdf_file"
    fi
  fi
}

# Processing
count=0
for epub in "${EPUBS[@]}"; do
  count=$((count+1))
  name=$(basename "$epub" .epub)
  clean_name=$(clean_filename "$name")
  out="$OUTPUT_DIR/$clean_name.pdf"

  $DRY_RUN && echo "🧪 $epub → $out" && continue
  [ "$VERBOSE" = true ] && echo "📘 Processing: $epub"

  if [ -f "$out" ] && [ "$FORCE" = false ]; then
    [ "$VERBOSE" = true ] && echo "⏭️ Already converted: $clean_name"
    progress_bar "$count" "$TOTAL"
    continue
  fi

  # Create temporary directory
  TMP_DIR=$(mktemp -d)
  
  debug_log "Répertoire temporaire: $TMP_DIR"

  # Convert EPUB directly to PDF using Calibre
  debug_log "Conversion EPUB vers PDF avec Calibre..."
  
  # Prepare ebook-convert arguments
  EBOOK_ARGS=()
  
  if [[ -n "$RESIZE" ]]; then
    RESIZE_DIMS=$(get_resize_dimensions "$RESIZE")
    EBOOK_ARGS+=("--output-profile" "tablet")
    EBOOK_ARGS+=("--margin-top" "0" "--margin-bottom" "0" "--margin-left" "0" "--margin-right" "0")
  fi
  
  if [[ "$GRAYSCALE" == true ]]; then
    EBOOK_ARGS+=("--grayscale")
  fi

  # Convert EPUB directly to PDF
  debug_log "Conversion de: $epub vers $out"
  if [[ ${#EBOOK_ARGS[@]} -eq 0 ]]; then
    if ! ebook-convert "$epub" "$out" >/dev/null 2>&1; then
      warning "Failed to convert EPUB file: $epub"
      [ "$CLEAN_TMP" = true ] && rm -rf "$TMP_DIR"
      progress_bar "$count" "$TOTAL"
      continue
    fi
  else
    if ! ebook-convert "$epub" "$out" "${EBOOK_ARGS[@]}" >/dev/null 2>&1; then
      warning "Failed to convert EPUB file: $epub"
      [ "$CLEAN_TMP" = true ] && rm -rf "$TMP_DIR"
      progress_bar "$count" "$TOTAL"
      continue
    fi
  fi

  if [[ -f "$out" ]]; then
    success "Created: $out"
    
    # Edit metadata if requested
    edit_pdf_metadata "$out" "$epub"
    
    # Auto-rename if requested
    auto_rename_pdf "$out" "$epub"
  else
    warning "Failed to create PDF: $out"
  fi

  # Clean up temporary files
  if [[ "$CLEAN_TMP" == true ]]; then
    debug_log "Nettoyage des fichiers temporaires..."
    rm -rf "$TMP_DIR"
  fi

  progress_bar "$count" "$TOTAL"
done

echo -e "\n✅ Conversion completed."

# ZIP
if $ZIP_OUTPUT; then
  ZIP_NAME="${OUTPUT_DIR%/}.zip"
  echo "📦 Creating archive: $ZIP_NAME"
  if [ -f "$ZIP_NAME" ]; then
    rm "$ZIP_NAME"
  fi
  if ls "$OUTPUT_DIR"/*.pdf >/dev/null 2>&1; then
    zip -j -q "$ZIP_NAME" "$OUTPUT_DIR"/*.pdf
    echo "✅ Archive created: $ZIP_NAME"
  else
    echo "⚠️ No PDFs to archive"
  fi
fi

$OPEN_OUTPUT_DIR && open "$OUTPUT_DIR"

success "Conversion completed!"

exit 0
