# PDF Batch Processor

A powerful Python tool for batch processing PDF files with automated optimization, metadata removal, and standardized viewer settings.

## Features

### Core PDF Processing
- ✅ **Fast Web Viewing** - Linearizes PDFs for faster loading in browsers
- ✅ **Bookmarks Panel** - Sets initial view to show bookmarks automatically
- ✅ **Default Layout** - Standardizes page layout and magnification
- ✅ **Metadata Removal** - Completely removes all metadata (title, author, keywords, etc.)
- ✅ **Bookmark Management** - Keeps parent bookmarks visible, collapses children
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

### Examples

**Windows:**
```bash
python pdf_batch_processor.py C:\Users\Documents\PDFs
```

**macOS/Linux:**
```bash
python pdf_batch_processor.py /home/user/documents/pdfs
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
5. **Collapses child bookmarks** (keeps parents visible)
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
