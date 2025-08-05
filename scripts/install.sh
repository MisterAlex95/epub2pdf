#!/bin/bash

set -euo pipefail

echo "📦 Installing epub2pdf & cbr2pdf and their dependencies..."

# Check Homebrew
if ! command -v brew &>/dev/null; then
  echo "❌ Homebrew not found. Install it first:"
  echo "   /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
  echo "   Then run this script again."
  exit 1
fi

echo "🔍 Checking dependencies..."

# Install Calibre (EPUB conversion)
if ! command -v ebook-convert &>/dev/null; then
  echo "📚 Installing Calibre..."
  brew install --cask calibre
else
  echo "✅ Calibre already installed"
fi

# Install ImageMagick (image processing)
if ! command -v convert &>/dev/null; then
  echo "🖼️ Installing ImageMagick..."
  brew install imagemagick
else
  echo "✅ ImageMagick already installed"
fi

# Install Ghostscript (PDF combination)
if ! command -v gs &>/dev/null; then
  echo "📄 Installing Ghostscript..."
  brew install ghostscript
else
  echo "✅ Ghostscript already installed"
fi

# Install unar (CBR extraction)
if ! command -v unar &>/dev/null; then
  echo "📚 Installing unar..."
  brew install unar
else
  echo "✅ unar already installed"
fi

# Install exiftool (PDF metadata editing)
if ! command -v exiftool &>/dev/null; then
  echo "📝 Installing exiftool..."
  brew install exiftool
else
  echo "✅ exiftool already installed"
fi

# Install pdftk (PDF merging)
if ! command -v pdftk &>/dev/null; then
  echo "📄 Installing pdftk..."
  brew install pdftk-java
else
  echo "✅ pdftk already installed"
fi

# Install Python dependencies
echo "🐍 Installing Python dependencies..."
if ! python3 -c "import tkinter" 2>/dev/null; then
  echo "🖥️ Installing Python tkinter..."
  brew install python-tk
else
  echo "✅ Python tkinter already installed"
fi

# Install Pillow for image processing
if ! python3 -c "import PIL" 2>/dev/null; then
  echo "🖼️ Installing Pillow..."
  python3 -m pip install Pillow --break-system-packages
else
  echo "✅ Pillow already installed"
fi

# Check zip (archiving)
if ! command -v zip &>/dev/null; then
  echo "⚠️ zip not found (normally included in macOS)"
else
  echo "✅ zip available"
fi

# Check unzip (extraction)
if ! command -v unzip &>/dev/null; then
  echo "⚠️ unzip not found (normally included in macOS)"
else
  echo "✅ unzip available"
fi

echo "✅ All dependencies are installed."

# Create installation directories
echo "📁 Creating installation directories..."
mkdir -p "$HOME/.epub2pdf"
mkdir -p "$HOME/.cbr2pdf"

# Copy conversion scripts
echo "📜 Copying conversion scripts..."
if [ -f "$(dirname "$0")/epub2pdf.sh" ]; then
  cp "$(dirname "$0")/epub2pdf.sh" "$HOME/.epub2pdf/epub2pdf.sh"
  chmod +x "$HOME/.epub2pdf/epub2pdf.sh"
  echo "✅ epub2pdf.sh copied"
else
  echo "❌ epub2pdf.sh script not found in scripts directory"
  exit 1
fi

if [ -f "$(dirname "$0")/cbr2pdf.sh" ]; then
  cp "$(dirname "$0")/cbr2pdf.sh" "$HOME/.cbr2pdf/cbr2pdf.sh"
  chmod +x "$HOME/.cbr2pdf/cbr2pdf.sh"
  echo "✅ cbr2pdf.sh copied"
else
  echo "❌ cbr2pdf.sh script not found in scripts directory"
  exit 1
fi

if [ -f "$(dirname "$0")/cbz2pdf.sh" ]; then
  cp "$(dirname "$0")/cbz2pdf.sh" "$HOME/.epub2pdf/cbz2pdf.sh"
  chmod +x "$HOME/.epub2pdf/cbz2pdf.sh"
  echo "✅ cbz2pdf.sh copied"
else
  echo "❌ cbz2pdf.sh script not found in scripts directory"
  exit 1
fi

# Copy GUI files
echo "🖥️ Copying GUI files..."
if [ -f "$(dirname "$0")/../main.py" ]; then
  cp "$(dirname "$0")/../main.py" "$HOME/.epub2pdf/main.py"
  chmod +x "$HOME/.epub2pdf/main.py"
  echo "✅ main.py copied"
else
  echo "⚠️ main.py not found, GUI will not be available"
fi

if [ -f "$(dirname "$0")/../run.py" ]; then
  cp "$(dirname "$0")/../run.py" "$HOME/.epub2pdf/run.py"
  chmod +x "$HOME/.epub2pdf/run.py"
  echo "✅ run.py copied"
else
  echo "⚠️ run.py not found, launcher will not be available"
fi

# Copy source code
echo "📁 Copying source code..."
if [ -d "$(dirname "$0")/../src" ]; then
  cp -r "$(dirname "$0")/../src" "$HOME/.epub2pdf/"
  echo "✅ Source code copied"
else
  echo "⚠️ src directory not found"
fi

# Configure aliases
echo "🔗 Configuring aliases..."
SHELL_RC="$HOME/.bash_profile"
[[ "$SHELL" =~ zsh ]] && SHELL_RC="$HOME/.zshrc"

# EPUB alias
if ! grep -q "alias epub2pdf=" "$SHELL_RC"; then
  echo "alias epub2pdf='$HOME/.epub2pdf/epub2pdf.sh'" >> "$SHELL_RC"
  echo "✅ EPUB alias added to $SHELL_RC"
else
  echo "ℹ️ EPUB alias already present in $SHELL_RC"
fi

# CBR alias
if ! grep -q "alias cbr2pdf=" "$SHELL_RC"; then
  echo "alias cbr2pdf='$HOME/.cbr2pdf/cbr2pdf.sh'" >> "$SHELL_RC"
  echo "✅ CBR alias added to $SHELL_RC"
else
  echo "ℹ️ CBR alias already present in $SHELL_RC"
fi

# CBZ alias
if [ -f "$HOME/.epub2pdf/cbz2pdf.sh" ]; then
  if ! grep -q "alias cbz2pdf=" "$SHELL_RC"; then
    echo "alias cbz2pdf='$HOME/.epub2pdf/cbz2pdf.sh'" >> "$SHELL_RC"
    echo "✅ CBZ alias added to $SHELL_RC"
  else
    echo "ℹ️ CBZ alias already present in $SHELL_RC"
  fi
fi

# Unified GUI alias
if [ -f "$HOME/.epub2pdf/main.py" ]; then
  if ! grep -q "alias epub2pdf-gui=" "$SHELL_RC"; then
    echo "alias epub2pdf-gui='cd $HOME/.epub2pdf && python3 main.py'" >> "$SHELL_RC"
    echo "✅ Unified GUI alias added to $SHELL_RC"
  else
    echo "ℹ️ Unified GUI alias already present in $SHELL_RC"
  fi
fi

echo ""
echo "🎉 Installation completed successfully!"
echo ""
echo "📖 Usage:"
echo "   epub2pdf --help                    # Show EPUB help"
echo "   cbr2pdf --help                     # Show CBR help"
echo "   cbz2pdf --help                     # Show CBZ help"
echo "   epub2pdf-gui                       # Launch unified GUI"
echo ""
echo "💡 Examples:"
echo "   epub2pdf --input-dir ./mangas --output-dir ./pdfs --recursive"
echo "   cbr2pdf --input-dir ./comics --output-dir ./pdfs --verbose"
echo "   cbz2pdf --input-dir ./books --output-dir ./pdfs --grayscale"
echo ""
echo "🔧 Features:"
echo "   ✅ EPUB to PDF conversion with Calibre"
echo "   ✅ CBR to PDF conversion optimized for comics"
echo "   ✅ CBZ to PDF conversion optimized for books"
echo "   ✅ Batch processing with progress bar"
echo "   ✅ Grayscale mode to save ink"
echo "   ✅ Automatic ZIP archiving"
echo "   ✅ Temporary file cleanup"
echo "   ✅ PDF metadata editing with exiftool"
echo "   ✅ PDF merging with pdftk"
echo "   ✅ Unified interface with file listing and parallel processing"
echo "   ✅ File preview and selection"
echo "   ✅ Automatic format detection"
echo "   ✅ File filtering and sorting"
echo ""
echo "🔄 To reload your shell configuration:"
echo "   source $SHELL_RC" 