#!/bin/bash

set -euo pipefail

echo "📦 Installing epub2pdf and its dependencies..."

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

# Install Python tkinter (GUI)
if ! python3 -c "import tkinter" 2>/dev/null; then
  echo "🖥️ Installing Python tkinter..."
  brew install python-tk
else
  echo "✅ Python tkinter already installed"
fi

# Check zip (archiving)
if ! command -v zip &>/dev/null; then
  echo "⚠️ zip not found (normally included in macOS)"
else
  echo "✅ zip available"
fi

echo "✅ All dependencies are installed."

# Create installation directory
echo "📁 Creating installation directory..."
mkdir -p "$HOME/.epub2pdf"

# Copy main script
echo "📜 Copying main script..."
if [ -f "$(dirname "$0")/epub2pdf.sh" ]; then
  cp "$(dirname "$0")/epub2pdf.sh" "$HOME/.epub2pdf/epub2pdf.sh"
  chmod +x "$HOME/.epub2pdf/epub2pdf.sh"
else
  echo "❌ epub2pdf.sh script not found in current directory"
  exit 1
fi

# Copy GUI script
echo "🖥️ Copying GUI script..."
if [ -f "$(dirname "$0")/epub2pdf_gui.py" ]; then
  cp "$(dirname "$0")/epub2pdf_gui.py" "$HOME/.epub2pdf/epub2pdf_gui.py"
  chmod +x "$HOME/.epub2pdf/epub2pdf_gui.py"
else
  echo "⚠️ epub2pdf_gui.py not found, GUI will not be available"
fi

# Copy GUI launcher
echo "🚀 Copying GUI launcher..."
if [ -f "$(dirname "$0")/epub2pdf_gui.sh" ]; then
  cp "$(dirname "$0")/epub2pdf_gui.sh" "$HOME/.epub2pdf/epub2pdf_gui.sh"
  chmod +x "$HOME/.epub2pdf/epub2pdf_gui.sh"
else
  echo "⚠️ epub2pdf_gui.sh not found, GUI launcher will not be available"
fi

# Configure alias
echo "🔗 Configuring alias..."
SHELL_RC="$HOME/.bash_profile"
[[ "$SHELL" =~ zsh ]] && SHELL_RC="$HOME/.zshrc"

if ! grep -q "alias epub2pdf=" "$SHELL_RC"; then
  echo "alias epub2pdf='$HOME/.epub2pdf/epub2pdf.sh'" >> "$SHELL_RC"
  echo "✅ Alias added to $SHELL_RC"
  echo "🔁 Reload your terminal or run: source $SHELL_RC"
else
  echo "ℹ️ Alias already present in $SHELL_RC"
fi

# Add GUI alias if GUI files exist
if [ -f "$HOME/.epub2pdf/epub2pdf_gui.sh" ]; then
  if ! grep -q "alias epub2pdf-gui=" "$SHELL_RC"; then
    echo "alias epub2pdf-gui='$HOME/.epub2pdf/epub2pdf_gui.sh'" >> "$SHELL_RC"
    echo "✅ GUI alias added to $SHELL_RC"
  else
    echo "ℹ️ GUI alias already present in $SHELL_RC"
  fi
fi

echo ""
echo "🎉 Installation completed successfully!"
echo ""
echo "📖 Usage:"
echo "   epub2pdf --help                    # Show help"
echo "   epub2pdf --input-dir ./mangas --output-dir ./pdfs --recursive"
echo "   epub2pdf-gui                       # Launch graphical interface"
echo ""
echo "💡 Example:"
echo "   epub2pdf --input-dir \"./Hokuto no Ken - Deluxe Epub/\" --output-dir ./manga --verbose"
echo ""
echo "🔧 Features:"
echo "   ✅ EPUB to PDF conversion optimized for manga"
echo "   ✅ Batch processing with progress bar"
echo "   ✅ Grayscale mode to save ink"
echo "   ✅ Automatic ZIP archiving"
echo "   ✅ Temporary file cleanup"
echo "   ✅ Graphical user interface"
