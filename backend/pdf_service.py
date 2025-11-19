"""
PDF Processing Service Module
Refactored from pdf_batch_processor.py for API use
"""

import pikepdf
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import datetime


class PDFProcessor:
    """Service class for processing PDF files"""

    def __init__(self, bookmark_level: int = 1):
        """
        Initialize PDF Processor

        Args:
            bookmark_level: Level of bookmark visibility (0=all, 1=top-level only, etc.)
        """
        self.bookmark_level = bookmark_level

    def process_pdf(self, input_path: Path, output_path: Path) -> Dict:
        """
        Process a single PDF file with linearization, metadata removal, and bookmark management

        Args:
            input_path: Path to input PDF file
            output_path: Path for processed PDF output

        Returns:
            Dict containing processing results and before/after properties
        """
        result = {
            'success': False,
            'filename': input_path.name,
            'error': None,
            'before': {},
            'after': {}
        }

        try:
            # Get properties before processing
            result['before'] = self.get_pdf_properties(input_path)

            # Open and process PDF
            with pikepdf.open(input_path) as pdf:
                # Set page mode and layout for standardized viewing
                pdf.Root.PageMode = pikepdf.Name.UseNone
                pdf.Root.PageLayout = pikepdf.Name.SinglePage

                # Remove tagged PDF structures
                if '/MarkInfo' in pdf.Root:
                    del pdf.Root.MarkInfo
                if '/StructTreeRoot' in pdf.Root:
                    del pdf.Root.StructTreeRoot

                # Remove metadata before saving
                self.remove_metadata(pdf)

                # Process bookmarks
                self.process_bookmarks(pdf, self.bookmark_level)

                # Save with linearization (fast web view)
                pdf.save(
                    output_path,
                    linearize=True,
                    compress_streams=True,
                    object_stream_mode=pikepdf.ObjectStreamMode.generate
                )

            # Remove metadata again after saving (double-clean)
            with pikepdf.open(output_path, allow_overwriting_input=True) as pdf:
                self.remove_metadata(pdf)
                pdf.save(
                    output_path,
                    linearize=True,
                    compress_streams=True,
                    object_stream_mode=pikepdf.ObjectStreamMode.generate
                )

            # Get properties after processing
            result['after'] = self.get_pdf_properties(output_path)
            result['success'] = True

        except Exception as e:
            result['error'] = str(e)

        return result

    def validate_pdf(self, file_path: Path) -> Dict:
        """
        Validate and check PDF properties without processing

        Args:
            file_path: Path to PDF file to validate

        Returns:
            Dict containing validation results and PDF properties
        """
        validation = {
            'valid': False,
            'properties': {},
            'issues': [],
            'error': None
        }

        try:
            # Get PDF properties
            props = self.get_pdf_properties(file_path)
            validation['properties'] = props

            # Check for issues
            if props.get('has_metadata', False):
                validation['issues'].append('Contains metadata that can be removed')

            if not props.get('is_linearized', False):
                validation['issues'].append('Not linearized (not optimized for fast web viewing)')

            if props.get('bookmark_count', 0) > 0:
                validation['issues'].append(f"Has {props['bookmark_count']} bookmarks that can be managed")

            validation['valid'] = True

        except Exception as e:
            validation['error'] = str(e)

        return validation

    def remove_metadata(self, pdf: pikepdf.Pdf) -> None:
        """
        Remove all metadata from PDF

        Args:
            pdf: pikepdf.Pdf object to clean
        """
        # Remove document info dictionary
        with pdf.open_metadata(set_pikepdf_as_editor=False, update_docinfo=False) as meta:
            meta.clear()

        # Remove XMP metadata if present
        if '/Metadata' in pdf.Root:
            del pdf.Root.Metadata

    def process_bookmarks(self, pdf: pikepdf.Pdf, level: int) -> None:
        """
        Process bookmarks to set visibility level

        Args:
            pdf: pikepdf.Pdf object
            level: Visibility level (0=all expanded, 1=top-level only, etc.)
        """
        try:
            if '/Outlines' not in pdf.Root:
                return

            outlines = pdf.Root.Outlines

            if level == 0:
                # Expand all bookmarks
                if hasattr(outlines, 'Count'):
                    del outlines.Count
            elif level >= 1:
                # Collapse bookmarks at specified level
                if '/First' in outlines:
                    first_bookmark = outlines.First
                    self.collapse_child_bookmarks(first_bookmark, 1, level)

                    # Count top-level bookmarks
                    count = 0
                    current = first_bookmark
                    while current:
                        count += 1
                        current = current.get('/Next')

                    # Set negative count to show collapsed state
                    outlines.Count = -count

        except Exception:
            pass  # Silently handle bookmark processing errors

    def collapse_child_bookmarks(self, bookmark, current_level: int, target_level: int) -> None:
        """
        Recursively collapse child bookmarks

        Args:
            bookmark: Current bookmark object
            current_level: Current depth level
            target_level: Target level to collapse at
        """
        try:
            if '/First' in bookmark and '/Count' in bookmark:
                if current_level >= target_level:
                    # Make count negative to collapse
                    count = abs(int(bookmark.Count))
                    bookmark.Count = -count

                # Process child bookmarks
                child = bookmark.First
                while child:
                    self.collapse_child_bookmarks(child, current_level + 1, target_level)
                    child = child.get('/Next')

        except Exception:
            pass  # Silently handle bookmark processing errors

    def get_pdf_properties(self, file_path: Path) -> Dict:
        """
        Extract PDF properties

        Args:
            file_path: Path to PDF file

        Returns:
            Dict containing PDF properties
        """
        properties = {
            'file_size_kb': 0,
            'page_count': 0,
            'is_linearized': False,
            'has_metadata': False,
            'bookmark_count': 0,
            'title': '',
            'author': '',
            'subject': '',
            'keywords': ''
        }

        try:
            properties['file_size_kb'] = round(file_path.stat().st_size / 1024, 2)

            with pikepdf.open(file_path) as pdf:
                properties['page_count'] = len(pdf.pages)
                properties['is_linearized'] = pdf.is_linearized

                # Check for metadata
                with pdf.open_metadata(set_pikepdf_as_editor=False, update_docinfo=False) as meta:
                    properties['has_metadata'] = len(meta) > 0

                    # Get basic metadata
                    properties['title'] = str(meta.get('dc:title', ''))
                    properties['author'] = str(meta.get('dc:creator', ''))
                    properties['subject'] = str(meta.get('dc:subject', ''))
                    properties['keywords'] = str(meta.get('pdf:Keywords', ''))

                # Count bookmarks
                if '/Outlines' in pdf.Root and '/First' in pdf.Root.Outlines:
                    count = 0
                    current = pdf.Root.Outlines.First
                    while current:
                        count += 1
                        current = current.get('/Next')
                    properties['bookmark_count'] = count

        except Exception:
            pass  # Return partial properties on error

        return properties
