#!/bin/bash

# Strict mode for error detection, but not for help
if [[ "$*" == *"--help"* ]] || [[ "$*" == *"-h"* ]]; then
  set -e  # Less strict mode for help
else
  set -euo pipefail  # Strict mode for error detection
fi

VERSION="1.0"

# Required dependencies
REQUIRED_CMDS=("ebook-convert" "convert" "zip")

for cmd in "${REQUIRED_CMDS[@]}"; do
  if ! command -v "$cmd" &>/dev/null; then
    echo "❌ Missing dependency: $cmd"
    echo "💡 Install dependencies with: ./install-epub2pdf.sh"
    exit 1
  fi
done

# Default options
INPUT_DIR="."
OUTPUT_DIR="./pdfs"
RECURSIVE=false
FORCE=false
GRAYSCALE=false
ZIP_OUTPUT=false
CLEAN_TMP=true
OPEN_DIR=false
DRY_RUN=false
VERBOSE=false
RESIZE=""

# Check first if help is requested
for arg in "$@"; do
  if [ "$arg" = "--help" ] || [ "$arg" = "-h" ]; then
    cat <<EOF
📘 epub2pdf v$VERSION

Usage: epub2pdf [OPTIONS]

Options:
  --input-dir DIR        Input directory containing EPUB files (default: .)
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
  --help                 Show this help

Examples:
  epub2pdf --input-dir ./mangas --output-dir ./pdfs --recursive --grayscale --zip-output
  epub2pdf --input-dir ./mangas --resize A4 --verbose

EOF
    exit 0
  fi
done

# Simple argument parsing
while [[ $# -gt 0 ]]; do
  case "$1" in
    --input-dir)
      INPUT_DIR="$2"
      shift 2
      ;;
    --output-dir)
      OUTPUT_DIR="$2"
      shift 2
      ;;
    --recursive)
      RECURSIVE=true
      shift
      ;;
    --force)
      FORCE=true
      shift
      ;;
    --grayscale)
      GRAYSCALE=true
      shift
      ;;
    --resize)
      RESIZE="$2"
      shift 2
      ;;
    --zip-output)
      ZIP_OUTPUT=true
      shift
      ;;
    --clean-tmp)
      CLEAN_TMP=true
      shift
      ;;
    --open-output-dir)
      OPEN_DIR=true
      shift
      ;;
    --dry-run)
      DRY_RUN=true
      shift
      ;;
    --verbose)
      VERBOSE=true
      shift
      ;;
    *)
      echo "❌ Unknown option: $1"
      echo "Use --help to see available options"
      exit 1
      ;;
  esac
done

# Path validation
if [ ! -d "$INPUT_DIR" ]; then
  echo "❌ Input directory does not exist: $INPUT_DIR"
  exit 1
fi

# Find EPUB files
if $RECURSIVE; then
  IFS=$'\n' EPUBS=($(find "$INPUT_DIR" -type f -name "*.epub"))
else
  IFS=$'\n' EPUBS=($(find "$INPUT_DIR" -maxdepth 1 -type f -name "*.epub"))
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

  TMP_OE_DIR="$OUTPUT_DIR/${clean_name}_oe"
  TMP_IMG_DIR="$OUTPUT_DIR/${clean_name}_img"
  
  # Clean existing temporary files
  rm -rf "$TMP_OE_DIR" "$TMP_IMG_DIR"
  mkdir -p "$TMP_IMG_DIR"

  # Convert EPUB to Open E-Book
  if ! ebook-convert "$epub" "$TMP_OE_DIR" \
    --disable-font-rescaling \
    --margin-top 0 --margin-bottom 0 --margin-left 0 --margin-right 0 \
    --enable-heuristics >/dev/null 2>&1; then
    echo "❌ Error converting: $epub"
    continue
  fi

  # Copy images from Open E-Book directory
  if [ -d "$TMP_OE_DIR/OPS/images" ]; then
    cp "$TMP_OE_DIR/OPS/images"/* "$TMP_IMG_DIR/" 2>/dev/null || true
  fi

  # Check if images were extracted
  if ! ls "$TMP_IMG_DIR"/* >/dev/null 2>&1; then
    echo "❌ No image content detected in: $epub"
    [ "$CLEAN_TMP" = true ] && rm -rf "$TMP_OE_DIR" "$TMP_IMG_DIR"
    progress_bar "$count" "$TOTAL"
    continue
  fi

  # Convert to PDF via ImageMagick
  IMG_FILES=($(find "$TMP_IMG_DIR" -type f \( -name "*.jpg" -o -name "*.jpeg" -o -name "*.png" -o -name "*.gif" -o -name "*.bmp" \) | sort))
  
  if [ ${#IMG_FILES[@]} -eq 0 ]; then
    echo "❌ No valid images found in: $epub"
    [ "$CLEAN_TMP" = true ] && rm -rf "$TMP_OE_DIR" "$TMP_IMG_DIR"
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
      [ "$CLEAN_TMP" = true ] && rm -rf "$TMP_OE_DIR" "$TMP_IMG_DIR"
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
    [ "$CLEAN_TMP" = true ] && rm -rf "$TMP_OE_DIR" "$TMP_IMG_DIR"
    progress_bar "$count" "$TOTAL"
    continue
  fi

  [ "$CLEAN_TMP" = true ] && rm -rf "$TMP_OE_DIR" "$TMP_IMG_DIR"
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

$OPEN_DIR && open "$OUTPUT_DIR"
