# 📘 epub2pdf, cbr2pdf & cbz2pdf

A comprehensive toolset for converting EPUB, CBR, and CBZ files to PDF format, optimized for manga, comics, and books.

## 🚀 Features

- **📖 EPUB to PDF**: Convert EPUB files to PDF with optimized settings for manga
- **📚 CBR to PDF**: Convert CBR (Comic Book RAR) files to PDF for comics
- **📖 CBZ to PDF**: Convert CBZ (Comic Book ZIP) files to PDF for books
- **🔄 Batch Processing**: Convert multiple files at once with progress tracking
- **⚡ Parallel Processing**: Convert files simultaneously for faster processing
- **🎨 Grayscale Mode**: Convert to black and white to save ink
- **📏 Resize Options**: Resize images to standard formats (A4, A3, A5, HD, FHD)
- **📦 ZIP Archiving**: Automatically create ZIP archives of converted PDFs
- **🧹 Clean Up**: Automatic temporary file cleanup
- **🖥️ Graphical Interfaces**: Multiple GUI options for easy use
- **📊 File Listing**: Automatic scanning and display of found files
- **🔄 Real-time Progress**: Live progress tracking and detailed logging
- **💾 Settings Persistence**: Remember your preferences between sessions
- **⌨️ Keyboard Shortcuts**: Quick access to common functions
- **ℹ️ About Dialog**: Version information and feature overview
- **🎯 Smart Error Handling**: Helpful error messages and user guidance
- **🎨 Modern UI Design**: Beautiful and ergonomic interface
- **📊 Visual Status Indicators**: Dynamic status icons and progress tracking
- **🔍 File Counters**: Real-time file counting per tab
- **🎨 Color-Coded Elements**: Intuitive color scheme for better UX

## 📋 Prerequisites

- **macOS** (tested on macOS 10.15+)
- **Homebrew** for package management
- **Calibre** for EPUB processing
- **ImageMagick** for image manipulation
- **Ghostscript** for PDF operations
- **unar** for CBR extraction
- **unzip** for CBZ extraction (built-in)
- **Python 3** with tkinter for GUI
- **zip** for archiving

## 🛠️ Installation

### Automatic Installation (Recommended)

```bash
# Clone or download the project
git clone <repository-url>
cd epub2pdf

# Run the unified installer
./install.sh
```

The installer will:
- Check and install all required dependencies
- Set up command-line aliases
- Configure GUI launchers
- Create necessary directories

### Manual Installation

If you prefer manual installation:

```bash
# Install dependencies
brew install calibre imagemagick ghostscript unar python-tk

# Make scripts executable
chmod +x *.sh *.py

# Set up aliases manually in your shell RC file
echo 'alias epub2pdf="~/.epub2pdf/epub2pdf.sh"' >> ~/.zshrc
echo 'alias cbr2pdf="~/.cbr2pdf/cbr2pdf.sh"' >> ~/.zshrc
echo 'alias cbz2pdf="~/.epub2pdf/cbz2pdf.sh"' >> ~/.zshrc
echo 'alias unified-gui="~/.epub2pdf/unified_gui.sh"' >> ~/.zshrc
```

## 🖥️ Graphical Interface

epub2pdf includes multiple user-friendly graphical interfaces:

### Unified Interface
- **unified-gui**: Modern interface with tabbed interface for all formats (EPUB, CBR, CBZ)

### Features
- **Intuitive Interface**: Simple and clean design
- **Directory Browsing**: Easy selection of input and output directories
- **File Listing**: Automatic scanning and display of found files
- **Tabbed Interface**: Separate tabs for EPUB, CBR, and CBZ files
- **Option Controls**: Checkboxes and dropdowns for all options
- **Real-time Log**: See conversion progress in real-time
- **Parallel Processing**: Convert multiple files simultaneously
- **Progress Tracking**: Visual feedback with progress bar
- **Dry Run**: Test your settings before converting
- **Settings Persistence**: Remember your preferences between sessions
- **Keyboard Shortcuts**: Quick access to common functions (Ctrl+O, Ctrl+F, Ctrl+R, etc.)
- **About Dialog**: Version information and feature overview (F1)
- **Smart Error Handling**: Helpful error messages and user guidance
- **Menu Bar**: Organized menu system with accelerators
- **Modern UI Design**: Beautiful interface with modern colors and typography
- **Visual Status Indicators**: Dynamic icons and status messages
- **File Counters**: Real-time file counting with visual feedback
- **Color-Coded Elements**: Intuitive color scheme for better user experience
- **Responsive Layout**: Adaptive design that works on different screen sizes

### Launching the GUI
```bash
# After installation
unified-gui                        # All formats with tabs

# Or directly
./unified_gui.sh
python3 unified_gui.py
```

### 🎨 Modern Interface Features

The unified GUI has been completely redesigned with modern aesthetics and improved ergonomics:

- **🎨 Modern Design**: Clean, professional interface with harmonious colors
- **📱 Responsive Layout**: Adaptive design that works on different screen sizes
- **🎯 Visual Feedback**: Dynamic status icons and progress indicators
- **📊 File Counters**: Real-time file counting with color-coded status
- **⌨️ Enhanced UX**: Intuitive navigation with visual cues
- **🎨 Color Scheme**: Professional color palette with semantic meaning
- **📝 Improved Typography**: Better fonts and spacing for readability
- **🏗️ Modular Architecture**: Clean, maintainable code structure
- **🔧 Extensible Design**: Easy to add new formats and features
- **📚 Well Documented**: Comprehensive documentation and comments

### Unified Interface Features
- **Tabbed Interface**: Separate tabs for EPUB, CBR, and CBZ files
- **File Scanning**: Automatically finds files of each type
- **Individual Lists**: Separate lists for each file type
- **Parallel Processing**: Convert multiple files simultaneously (configurable workers)
- **Selective Conversion**: Convert all files or specific types only
- **Real-time Progress**: Live progress bar and status updates
- **Comprehensive Logging**: Timestamped log with detailed conversion status

## 🛠️ Tools

### epub2pdf
Converts EPUB files to PDF, optimized for manga and books:
- Uses Calibre's `ebook-convert` for EPUB processing
- Extracts images and text content
- Optimizes layout for reading
- Supports all EPUB features (tables, images, formatting)

### cbr2pdf
Converts CBR (Comic Book RAR) files to PDF:
- Uses `unar` for RAR extraction
- Processes extracted images into PDF
- Optimized for comic book layouts
- Supports various image formats

### cbz2pdf
Converts CBZ (Comic Book ZIP) files to PDF:
- Uses `unzip` for ZIP extraction
- Processes extracted images into PDF
- Optimized for book layouts
- Supports various image formats

## 📖 Usage

### Command Line

```bash
# Basic usage
epub2pdf --input-dir ./mangas --output-dir ./pdfs
cbr2pdf --input-dir ./comics --output-dir ./pdfs
cbz2pdf --input-dir ./books --output-dir ./pdfs

# With options
epub2pdf --input-dir ./mangas --output-dir ./pdfs --recursive --grayscale --resize A4
cbr2pdf --input-dir ./comics --output-dir ./pdfs --verbose --force
cbz2pdf --input-dir ./books --output-dir ./pdfs --zip-output --open-output-dir
```

### GUI Usage

1. **Launch the GUI**: Run `unified-gui` or use individual GUIs
2. **Select Directories**: Choose input and output directories
3. **Scan Files**: Click "Scan All" to find files
4. **Configure Options**: Set conversion options as needed
5. **Convert**: Click "Convert All" or use individual tab buttons

## 📖 Usage Examples

```bash
# Convert all EPUB files in a directory
epub2pdf --input-dir ./mangas --output-dir ./pdfs --recursive

# Convert CBR files with grayscale and A4 size
cbr2pdf --input-dir ./comics --output-dir ./pdfs --grayscale --resize A4

# Convert CBZ files with verbose output
cbz2pdf --input-dir ./books --output-dir ./pdfs --verbose

# Test conversion without actually doing it
epub2pdf --input-dir ./test --dry-run

# Convert and create ZIP archive
cbr2pdf --input-dir ./comics --output-dir ./pdfs --zip-output

# Convert with custom size
cbz2pdf --input-dir ./books --output-dir ./pdfs --resize 800x600
```

## 🔧 How it Works

### EPUB Conversion
1. Uses Calibre's `ebook-convert` to convert EPUB to Open E-Book format
2. Extracts images and content from the OEB directory
3. Processes images with ImageMagick for optimal quality
4. Combines everything into a single PDF

### CBR Conversion
1. Uses `unar` to extract RAR archive
2. Finds all image files in the extracted directory
3. Processes images with ImageMagick (with optional resizing)
4. Combines images into a single PDF

### CBZ Conversion
1. Uses `unzip` to extract ZIP archive
2. Finds all image files in the extracted directory
3. Processes images with ImageMagick (with optional resizing)
4. Combines images into a single PDF

### Performance Optimizations
- **Batch Processing**: Images are processed in batches to avoid memory issues
- **Parallel Processing**: Multiple files can be converted simultaneously
- **Image Limiting**: Large files are limited to prevent memory overflow
- **Temporary Cleanup**: Automatic cleanup of temporary files

## 📁 File Structure

```
epub2pdf/
├── epub2pdf.sh          # EPUB to PDF conversion script
├── cbr2pdf.sh           # CBR to PDF conversion script
├── cbz2pdf.sh           # CBZ to PDF conversion script
├── unified_gui.py       # Unified graphical user interface
├── unified_gui.sh       # Unified GUI launcher script
├── install.sh           # Unified installation script
├── config.py            # Centralized configuration
├── ui_components.py     # Reusable UI components
├── tab_converter.py     # Tab management
├── conversion_manager.py # Conversion handling
├── settings_manager.py  # Settings persistence
├── STRUCTURE.md         # Modular architecture documentation
└── README.md           # This file
```

## 🔧 Options

All tools support the following options:

- `--input-dir DIR`: Input directory containing files
- `--output-dir DIR`: Output directory for PDF files
- `--recursive`: Search for files in subdirectories
- `--force`: Overwrite existing PDF files
- `--grayscale`: Convert images to grayscale (saves ink)
- `--resize SIZE`: Resize images (A4, A3, A5, HD, FHD, or custom)
- `--zip-output`: Create ZIP archive of all PDFs
- `--clean-tmp`: Clean temporary files (default: true)
- `--open-output-dir`: Open output directory when done
- `--verbose`: Verbose output
- `--dry-run`: Show what would be done without doing it

## 🚨 Troubleshooting

### Common Issues

**"No EPUB/CBR/CBZ files found"**
- Check that the input directory contains files with the correct extensions
- Use `--recursive` to search subdirectories
- Verify file permissions

**"Command not found" errors**
- Run `./install.sh` to install dependencies
- Check that Homebrew is installed
- Verify that all required tools are available

**"Permission denied" errors**
- Make scripts executable: `chmod +x *.sh`
- Check file permissions in input/output directories

**"Memory issues" with large files**
- The tools automatically limit image count to prevent memory issues
- Use `--resize` to reduce image size
- Process files in smaller batches

**GUI not launching**
- Install Python tkinter: `brew install python-tk`
- Check Python installation: `python3 --version`
- Verify script permissions

### Dependency Issues

**Calibre not found**
```bash
brew install calibre
```

**ImageMagick not found**
```bash
brew install imagemagick
```

**Ghostscript not found**
```bash
brew install ghostscript
```

**unar not found**
```bash
brew install unar
```

**Python tkinter not found**
```bash
brew install python-tk
```

## 📝 Notes

- **EPUB files**: Use Calibre for conversion, supports all EPUB features
- **CBR files**: Use `unar` for extraction (more reliable than `unrar`)
- **CBZ files**: Use `unzip` for extraction (built-in on macOS)
- **Image formats**: Supports JPG, PNG, GIF, BMP, TIFF, WebP
- **Memory management**: Large files are automatically limited to prevent issues
- **Temporary files**: Automatically cleaned up unless `--clean-tmp` is disabled

## 👨‍💻 Author

epub2pdf, cbr2pdf & cbz2pdf - A comprehensive PDF conversion toolkit

## 📄 License

This project is open source and available under the MIT License.