# PDF Batch Processor

A powerful Python tool for batch processing PDF files with automated optimization, metadata removal, and standardized viewer settings.

## Features

### Core PDF Processing
- ✅ **Fast Web Viewing** - Linearizes PDFs for faster loading in browsers
- ✅ **Bookmarks Panel** - Sets initial view to show bookmarks automatically
- ✅ **Default Layout** - Standardizes page layout and magnification
- ✅ **Metadata Removal** - Completely removes all metadata (title, author, keywords, etc.)
- ✅ **Bookmark Management** - Configurable bookmark visibility levels (expand all, top-level only, or custom depth)
- ✅ **Remove Tagging** - Strips PDF accessibility structure

### Operational Features
- 🔄 **Batch Processing** - Process multiple PDFs recursively
- 📁 **Organized Output** - Creates "processed" subfolder for each directory
- 📊 **Progress Tracking** - Real-time status and detailed summary reports
- 🔍 **Smart Filtering** - Avoids reprocessing files in "processed" folders
- 🌐 **Cross-Platform** - Works on Windows, macOS, and Linux
- 🛡️ **Error Handling** - Continues processing even if individual files fail

## Installation

### Prerequisites
- Python 3.7 or higher
- pip

### Setup

1. **Clone the repository**
```bash
git clone <repository-url>
cd pdfFDAValidator
```

2. **Create virtual environment**

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage
```bash
python pdf_batch_processor.py /path/to/pdf/folder
```

### Command-Line Options

```bash
python pdf_batch_processor.py <folder_path> [options]

Options:
  -b, --bookmark-levels N    Number of bookmark levels to keep visible
                            0 = Expand all bookmark levels
                            1 = Only top-level bookmarks visible (default)
                            2 = Top-level + first children visible
                            3+ = Keep specified number of levels visible

  -h, --help                Show help message and exit
```

### Examples

**Windows:**
```bash
# Process with default settings (top-level bookmarks only)
python pdf_batch_processor.py C:\Users\Documents\PDFs

# Expand all bookmark levels
python pdf_batch_processor.py C:\Users\Documents\PDFs --bookmark-levels 0

# Keep top-level and first children visible
python pdf_batch_processor.py C:\Users\Documents\PDFs -b 2
```

**macOS/Linux:**
```bash
# Process with default settings (top-level bookmarks only)
python pdf_batch_processor.py /home/user/documents/pdfs

# Expand all bookmark levels
python pdf_batch_processor.py /home/user/documents/pdfs --bookmark-levels 0

# Keep three levels of bookmarks visible
python pdf_batch_processor.py /home/user/documents/pdfs -b 3
```

### Output Structure
```
your_folder/
├── document1.pdf
├── document2.pdf
└── processed/
    ├── document1.pdf (processed)
    └── document2.pdf (processed)
```

### Bookmark Levels Explained

The `--bookmark-levels` option controls how many levels of bookmarks are visible when the PDF is opened:

- **Level 0**: All bookmarks are expanded (entire bookmark tree visible)
- **Level 1** (default): Only top-level bookmarks are visible, all children are collapsed
- **Level 2**: Top-level bookmarks AND their immediate children are visible, deeper levels are collapsed
- **Level 3+**: The specified number of levels are visible from the top

**Example bookmark structure:**
```
Chapter 1                    ← Level 1
├── Section 1.1             ← Level 2
│   ├── Subsection 1.1.1   ← Level 3
│   └── Subsection 1.1.2   ← Level 3
└── Section 1.2             ← Level 2
Chapter 2                    ← Level 1
```

With `--bookmark-levels 1`: Only "Chapter 1" and "Chapter 2" are visible
With `--bookmark-levels 2`: "Chapter 1", "Section 1.1", "Section 1.2", and "Chapter 2" are visible
With `--bookmark-levels 0`: All bookmarks are expanded and visible

## What It Does

For each PDF file, the processor:

1. **Enables fast web viewing** (linearization)
2. **Sets navigation to Bookmarks Panel** for initial view
3. **Applies default page layout** and magnification
4. **Removes all metadata** including:
   - Title, Author, Subject, Keywords
   - Creator, Producer
   - Creation Date, Modification Date
   - XMP metadata streams
5. **Manages bookmark visibility** (configurable levels: expand all, top-level only, or custom depth)
6. **Removes tagged PDF structure**

## Use Cases

- **Privacy** - Remove identifying metadata from documents
- **Web Publishing** - Optimize PDFs for faster web loading
- **Document Management** - Standardize PDF settings across collections
- **Archiving** - Clean and optimize PDFs before storage
- **Distribution** - Prepare professional PDFs with consistent settings

## Requirements

- pikepdf >= 8.0.0

## Project Structure

```
pdfFDAValidator/
├── pdf_batch_processor.py   # Main script
├── requirements.txt          # Python dependencies
├── README.md                 # This file
├── .gitignore               # Git ignore rules
└── venv/                    # Virtual environment (not in repo)
```

## Troubleshooting

### "python not found" error
- **Windows**: Use `py` instead of `python`
- **macOS/Linux**: Use `python3` instead of `python`

### Permission denied (macOS/Linux)
```bash
chmod +x pdf_batch_processor.py
```

### Virtual environment not activating
- Ensure you're in the correct directory
- Check that the `venv` folder was created successfully
- On Windows, try PowerShell or Command Prompt instead of Git Bash

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the MIT License.

## Author

Created to automate PDF processing and optimization tasks.

## Acknowledgments

- Built with [pikepdf](https://github.com/pikepdf/pikepdf) - A Python library for reading and writing PDF files
