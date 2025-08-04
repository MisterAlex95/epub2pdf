# 📘 epub2pdf

Bash script to convert EPUB files to PDF, optimized for manga and comics.

## 🎯 Features

- **EPUB → PDF Conversion**: Converts EPUB files to high-quality PDFs
- **Manga Optimized**: Automatically resizes images to A4 format
- **Batch Processing**: Converts multiple files in a single command
- **Recursive Search**: Searches subdirectories to find all EPUBs
- **Grayscale Mode**: Option to convert images to black and white
- **ZIP Archiving**: Automatically creates a ZIP archive of generated PDFs
- **Progress Bar**: Shows conversion progress
- **Dry-run Mode**: Preview files to convert without processing them
- **Graphical Interface**: User-friendly GUI for easy conversion

## 📋 Prerequisites

- **macOS** (tested on macOS)
- **Homebrew** for dependency installation

## 🚀 Installation

### Automatic Installation

```bash
# Clone the repository
git clone <repository-url>
cd epub2pdf

# Run the installation script
./install-epub2pdf.sh
```

### Manual Installation

```bash
# Install dependencies
brew install --cask calibre
brew install imagemagick ghostscript python-tk

# Make script executable
chmod +x epub2pdf.sh
```

## 🖥️ Graphical Interface

epub2pdf includes a user-friendly graphical interface that makes conversion even easier:

### Features
- **Intuitive Interface**: Simple and clean design
- **Directory Browsing**: Easy selection of input and output directories
- **Option Controls**: Checkboxes and dropdowns for all options
- **Real-time Log**: See conversion progress in real-time
- **Dry Run**: Test your settings before converting
- **Progress Bar**: Visual feedback during conversion

### Launching the GUI
```bash
# After installation
epub2pdf-gui

# Or directly
./epub2pdf_gui.sh
```

### GUI Options
- **Input/Output Directories**: Browse and select folders
- **Search Subdirectories**: Recursive search option
- **Overwrite Files**: Force overwrite existing PDFs
- **Grayscale**: Convert to black and white
- **Resize Images**: Choose from A4, A3, A5, HD, FHD, or custom size
- **Create ZIP**: Automatically archive results
- **Clean Temporary Files**: Remove temp files after conversion
- **Open Output Directory**: Open folder when done
- **Verbose Mode**: Show detailed progress

## 📖 Usage

### Basic Syntax

```bash
epub2pdf [OPTIONS]
```

### Available Options

| Option | Description | Default |
|--------|-------------|---------|
| `--input-dir DIR` | Directory containing EPUB files | `.` |
| `--output-dir DIR` | Output directory for PDFs | `./pdfs` |
| `--recursive` | Search in subdirectories | `false` |
| `--force` | Overwrite existing PDF files | `false` |
| `--grayscale` | Convert images to black and white | `false` |
| `--resize SIZE` | Resize images (A4, A3, A5, HD, FHD, or widthxheight) | `none` |
| `--zip-output` | Create a ZIP archive of PDFs | `false` |
| `--clean-tmp` | Remove temporary files | `false` |
| `--open-output-dir` | Open output directory at the end | `false` |
| `--dry-run` | Show files to convert without processing | `false` |
| `--verbose` | Verbose mode | `false` |
| `--help` | Show help | - |

### Usage Examples

**Simple conversion**:
```bash
epub2pdf
```

**Graphical interface**:
```bash
epub2pdf-gui
```

**Conversion with options**:
```bash
epub2pdf --input-dir ./mangas --output-dir ./pdfs --recursive --grayscale --zip-output
```

**Conversion with resizing**:
```bash
epub2pdf --input-dir ./mangas --resize A4 --verbose
epub2pdf --input-dir ./mangas --resize 800x600 --grayscale
```

**Preview**:
```bash
epub2pdf --input-dir ./books --recursive --dry-run --verbose
```

**Force conversion**:
```bash
epub2pdf --input-dir ./epub --output-dir ./pdf --force --clean-tmp
```

## 🔧 How it Works

1. **Detection**: Finds all `.epub` files in the input directory
2. **HTML Conversion**: Uses Calibre to convert EPUB to Open E-Book
3. **Image Extraction**: Extracts all images from the generated directory
4. **Resizing**: Resizes images if `--resize` option is specified
5. **PDF Conversion**: Uses ImageMagick to create the final PDF
6. **Cleanup**: Removes temporary files (if enabled)

## 📁 File Structure

```
epub2pdf/
├── epub2pdf.sh          # Main script
├── install-epub2pdf.sh  # Installation script
├── epub2pdf_gui.py      # Graphical user interface
├── epub2pdf_gui.sh      # GUI launcher script
└── README.md           # This file
```

## 🐛 Troubleshooting

### "Missing dependency" Error
```bash
# Check that all dependencies are installed
which ebook-convert
which convert
which zip
```

### Permission Issues
```bash
# Make script executable
chmod +x epub2pdf.sh
```

### No EPUB Files Found
- Check that files have `.epub` extension
- Use `--recursive` option if files are in subdirectories
- Check path with `--input-dir`

## 📝 Notes

- Generated PDFs preserve original quality by default
- The `--resize` option allows resizing images (A4, A3, A5, HD, FHD, or custom format)
- Images are centered and resized to fit the specified size
- The `--grayscale` option is useful for saving ink
- Automatic limitation to 100 images maximum per file

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest improvements
- Add new features

## 📄 License

This project is under free license. Use it as you wish!

---

**Version**: 1.0  
**Author**: epub2pdf  
**Last updated**: $(date +%Y-%m-%d)