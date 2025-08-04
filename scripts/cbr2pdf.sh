#!/bin/bash

# cbr2pdf.sh - Convert CBR (Comic Book RAR) files to PDF
# CBR files are essentially RAR archives containing images
# This script extracts CBR files and converts the images to PDF

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

# Default options
INPUT_DIR=""
OUTPUT_DIR="./pdfs"
RECURSIVE=false
FORCE=false
GRAYSCALE=false
RESIZE=""
ZIP_OUTPUT=false
CLEAN_TMP=true
OPEN_OUTPUT_DIR=false
VERBOSE=false
DRY_RUN=false

# Required commands
REQUIRED_CMDS=("unar" "convert" "zip")

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

debug_log "Script cbr2pdf.sh démarré (v${VERSION})"
debug_log "Répertoire de travail: $(pwd)"
debug_log "Arguments reçus: $*"

# Check first if help is requested
for arg in "$@"; do
  if [ "$arg" = "--help" ] || [ "$arg" = "-h" ]; then
    cat <<EOF
📘 cbr2pdf v$VERSION

Usage: cbr2pdf [OPTIONS]

Options:
  --input-dir DIR        Input directory containing CBR files (default: .)
  --output-dir DIR       Output directory for PDFs (default: ./pdfs)
  --recursive            Search in subdirectories
  --force                Overwrite existing PDF files
  --grayscale            Convert images to black and white
  --resize SIZE          Resize images (ex: A4, 1240x1754, 800x600)
  --zip-output           Create a .zip archive at the end
  --clean-tmp            Remove temporary files
  --open-output-dir      Open output directory at the end
  --dry-run              Show files to convert without processing
  --verbose              Verbose mode
  --pdf-title TITLE      Set PDF title metadata
  --pdf-author AUTHOR    Set PDF author metadata
  --pdf-subject SUBJECT  Set PDF subject metadata
  --pdf-keywords KEYWORDS Set PDF keywords metadata
  --help                 Show this help

Examples:
  cbr2pdf --input-dir ./comics --output-dir ./pdfs --recursive --grayscale --zip-output
  cbr2pdf --input-dir ./comics --resize A4 --verbose

EOF
    exit 0
  fi
done

# Simple argument parsing
debug_log "Début du parsing des arguments..."
while [[ $# -gt 0 ]]; do
  case "$1" in
    --input-dir)
      INPUT_DIR="$2"
      debug_log "Répertoire d'entrée défini: $INPUT_DIR"
      shift 2
      ;;
    --output-dir)
      OUTPUT_DIR="$2"
      debug_log "Répertoire de sortie défini: $OUTPUT_DIR"
      shift 2
      ;;
    --recursive)
      RECURSIVE=true
      debug_log "Mode récursif activé"
      shift
      ;;
    --force)
      FORCE=true
      debug_log "Mode force activé"
      shift
      ;;
    --grayscale)
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
    --verbose)
      VERBOSE=true
      debug_log "Mode verbose activé"
      shift
      ;;
    *)
      echo "❌ Unknown option: $1"
      echo "Use --help to see available options"
      exit 1
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

# Check dependencies
debug_log "Vérification des dépendances..."
for cmd in "${REQUIRED_CMDS[@]}"; do
  debug_log "Vérification de la commande: $cmd"
  if ! command -v "$cmd" &>/dev/null; then
    echo "❌ Missing dependency: $cmd"
    echo "💡 Install dependencies with: ./install-cbr2pdf.sh"
    exit 1
  else
    debug_log "✅ Commande $cmd trouvée: $(which $cmd)"
  fi
done
debug_log "✅ Toutes les dépendances sont satisfaites"

# Path validation
if [ ! -d "$INPUT_DIR" ]; then
  echo "❌ Input directory does not exist: $INPUT_DIR"
  exit 1
fi

# Find CBR files
if $RECURSIVE; then
  IFS=$'\n' CBRS=($(find "$INPUT_DIR" -type f -name "*.cbr"))
else
  IFS=$'\n' CBRS=($(find "$INPUT_DIR" -maxdepth 1 -type f -name "*.cbr"))
fi

TOTAL=${#CBRS[@]}
if [ "$TOTAL" -eq 0 ]; then
  echo "⚠️ No .cbr files found in $INPUT_DIR"
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
      # Check if it's a valid format (widthxheight)
      if [[ "$size" =~ ^[0-9]+x[0-9]+$ ]]; then
        echo "$size"
      else
        echo "❌ Invalid size format: $size"
        echo "Supported formats: A4, A3, A5, HD, FHD, or widthxheight (ex: 800x600)"
        exit 1
      fi
      ;;
  esac
}

# Apply PDF metadata
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
for cbr in "${CBRS[@]}"; do
  count=$((count+1))
  name=$(basename "$cbr" .cbr)
  clean_name=$(clean_filename "$name")
  out="$OUTPUT_DIR/$clean_name.pdf"

  $DRY_RUN && echo "🧪 $cbr → $out" && continue
  [ "$VERBOSE" = true ] && echo "📘 Processing: $cbr"

  if [ -f "$out" ] && [ "$FORCE" = false ]; then
    [ "$VERBOSE" = true ] && echo "⏭️ Already converted: $clean_name"
    progress_bar "$count" "$TOTAL"
    continue
  fi

  TMP_EXTRACT_DIR="$OUTPUT_DIR/${clean_name}_extract"
  TMP_IMG_DIR="$OUTPUT_DIR/${clean_name}_img"
  
  # Clean existing temporary files
  rm -rf "$TMP_EXTRACT_DIR" "$TMP_IMG_DIR"
  mkdir -p "$TMP_EXTRACT_DIR" "$TMP_IMG_DIR"

  # Extract CBR file
  if ! unar -o "$TMP_EXTRACT_DIR" "$cbr" >/dev/null 2>&1; then
    echo "❌ Error extracting: $cbr"
    continue
  fi

  # Find and copy images from extracted directory
  if ! find "$TMP_EXTRACT_DIR" -type f \( -name "*.jpg" -o -name "*.jpeg" -o -name "*.png" -o -name "*.gif" -o -name "*.bmp" \) -exec cp {} "$TMP_IMG_DIR/" \; 2>/dev/null; then
    echo "❌ No images found in: $cbr"
    [ "$CLEAN_TMP" = true ] && rm -rf "$TMP_EXTRACT_DIR" "$TMP_IMG_DIR"
    progress_bar "$count" "$TOTAL"
    continue
  fi

  # Check if images were extracted
  if ! ls "$TMP_IMG_DIR"/* >/dev/null 2>&1; then
    echo "❌ No image content detected in: $cbr"
    [ "$CLEAN_TMP" = true ] && rm -rf "$TMP_EXTRACT_DIR" "$TMP_IMG_DIR"
    progress_bar "$count" "$TOTAL"
    continue
  fi

  # Convert to PDF via ImageMagick
  IMG_FILES=($(find "$TMP_IMG_DIR" -type f \( -name "*.jpg" -o -name "*.jpeg" -o -name "*.png" -o -name "*.gif" -o -name "*.bmp" \) | sort))
  
  if [ ${#IMG_FILES[@]} -eq 0 ]; then
    echo "❌ No valid images found in: $cbr"
    [ "$CLEAN_TMP" = true ] && rm -rf "$TMP_EXTRACT_DIR" "$TMP_IMG_DIR"
    progress_bar "$count" "$TOTAL"
    continue
  fi
  
  # Limit number of images if too many
  MAX_IMAGES=100
  if [ ${#IMG_FILES[@]} -gt $MAX_IMAGES ]; then
    [ "$VERBOSE" = true ] && echo "⚠️ Limiting to $MAX_IMAGES images (${#IMG_FILES[@]} found)"
    LIMITED_IMGS=()
    for ((i=0; i<MAX_IMAGES && i<${#IMG_FILES[@]}; i++)); do
      LIMITED_IMGS+=("${IMG_FILES[$i]}")
    done
    IMG_FILES=("${LIMITED_IMGS[@]}")
  fi

  # Convert to PDF in small groups
  GROUP_SIZE=20
  TOTAL_GROUPS=$(( (${#IMG_FILES[@]} + GROUP_SIZE - 1) / GROUP_SIZE ))
  
  for ((i=0; i<${#IMG_FILES[@]}; i+=GROUP_SIZE)); do
    GROUP_START=$i
    GROUP_END=$((i + GROUP_SIZE - 1))
    if [ $GROUP_END -ge ${#IMG_FILES[@]} ]; then
      GROUP_END=$((${#IMG_FILES[@]} - 1))
    fi
    GROUP_IMAGES=()
    for ((j=GROUP_START; j<=GROUP_END; j++)); do
      GROUP_IMAGES+=("${IMG_FILES[$j]}")
    done
    GROUP_NUM=$((i/GROUP_SIZE + 1))
    
    # Create temporary file for this group
    GROUP_FILE="$TMP_IMG_DIR/group_${GROUP_NUM}.txt"
    printf '%s\n' "${GROUP_IMAGES[@]}" > "$GROUP_FILE"
    
    # Prepare conversion arguments
    CONVERT_ARGS=()
    if [ -n "$RESIZE" ]; then
      RESIZE_DIMS=$(get_resize_dimensions "$RESIZE")
      CONVERT_ARGS+=("-resize" "${RESIZE_DIMS}^" "-gravity" "center" "-extent" "$RESIZE_DIMS")
    fi
    $GRAYSCALE && CONVERT_ARGS+=("-colorspace" "Gray")
    CONVERT_ARGS+=("-quality" "100")
    
    # Convert this group
    if ! convert @"$GROUP_FILE" "${CONVERT_ARGS[@]}" "$TMP_IMG_DIR/group_${GROUP_NUM}.pdf" >/dev/null 2>&1; then
      echo "❌ Error converting group $GROUP_NUM"
      [ "$CLEAN_TMP" = true ] && rm -rf "$TMP_EXTRACT_DIR" "$TMP_IMG_DIR"
      progress_bar "$count" "$TOTAL"
      continue 2
    fi
  done
  
  # Combine all PDFs into one
  FINAL_ARGS=()
  $GRAYSCALE && FINAL_ARGS+=("-colorspace" "Gray")
  FINAL_ARGS+=("-quality" "100")
  
  if ! convert "$TMP_IMG_DIR"/group_*.pdf "${FINAL_ARGS[@]}" "$out" >/dev/null 2>&1; then
    echo "❌ Error combining PDFs"
    [ "$CLEAN_TMP" = true ] && rm -rf "$TMP_EXTRACT_DIR" "$TMP_IMG_DIR"
    progress_bar "$count" "$TOTAL"
    continue
  fi

  # Apply metadata if specified
  if [[ -n "$PDF_TITLE" || -n "$PDF_AUTHOR" || -n "$PDF_SUBJECT" || -n "$PDF_KEYWORDS" ]]; then
    apply_pdf_metadata "$out"
  fi

  [ "$CLEAN_TMP" = true ] && rm -rf "$TMP_EXTRACT_DIR" "$TMP_IMG_DIR"
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