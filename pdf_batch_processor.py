import os
import sys
from pathlib import Path
import pikepdf
from pikepdf import Pdf, Dictionary, Name

def collapse_child_bookmarks(outline_item):
    """
    Recursively collapse all child bookmarks (set Count to negative).
    """
    if '/First' in outline_item:  # Has children
        # Count the number of children
        count = 0
        child = outline_item.First
        while child:
            count += 1
            # Recursively collapse children's children
            collapse_child_bookmarks(child)
            child = child.Next if '/Next' in child else None
        
        # Set Count to negative to collapse
        if count > 0:
            outline_item.Count = -count

def process_bookmarks(pdf):
    """
    Process bookmarks to keep only parent bookmarks visible (collapse children).
    """
    try:
        if '/Outlines' in pdf.Root and pdf.Root.Outlines:
            outlines = pdf.Root.Outlines
            
            if '/First' in outlines:
                # Process each top-level bookmark
                current = outlines.First
                while current:
                    # Collapse children of this parent bookmark
                    collapse_child_bookmarks(current)
                    current = current.Next if '/Next' in current else None
    except Exception as e:
        print(f"  Warning: Could not process bookmarks: {e}")

def remove_metadata(pdf):
    """
    Remove all metadata from the PDF including XMP and Info dictionary.
    """
    # Remove XMP metadata stream if present
    if '/Metadata' in pdf.Root:
        del pdf.Root.Metadata
    
    # Remove XMP metadata
    try:
        with pdf.open_metadata(set_pikepdf_as_editor=False, update_docinfo=False) as meta:
            # Delete all XMP metadata properties
            for key in list(meta):
                try:
                    del meta[key]
                except:
                    pass
    except:
        pass
    
    # Remove the Info dictionary entirely from the trailer
    if hasattr(pdf, 'trailer') and '/Info' in pdf.trailer:
        del pdf.trailer['/Info']
    
    # Also try to clear docinfo if it still exists
    if pdf.docinfo:
        info_keys = list(pdf.docinfo.keys())
        for key in info_keys:
            try:
                del pdf.docinfo[key]
            except:
                pass

def process_pdf(input_path, output_path):
    """
    Process a single PDF file with the specified settings:
    1. Enable fast web viewing (linearization)
    2. Set Navigation Tab to Bookmarks Panel
    3. Set Page Layout and Magnification to Default
    4. Remove tagged PDF structure
    5. Remove metadata
    6. Collapse child bookmarks (keep only parent bookmarks expanded)
    """
    try:
        # Open the PDF
        pdf = Pdf.open(input_path)
        
        # Create or update the ViewerPreferences dictionary
        if '/ViewerPreferences' not in pdf.Root:
            pdf.Root.ViewerPreferences = Dictionary()
        
        # Set the catalog (Root) properties
        # PageMode: UseOutlines = Bookmarks Panel and Page
        pdf.Root.PageMode = Name.UseOutlines
        
        # PageLayout: Default (SinglePage is the standard default)
        pdf.Root.PageLayout = Name.SinglePage
        
        # ViewerPreferences for additional settings
        viewer_prefs = pdf.Root.ViewerPreferences
        
        # Remove Tagged PDF structure if it exists
        if '/MarkInfo' in pdf.Root:
            del pdf.Root.MarkInfo
        if '/StructTreeRoot' in pdf.Root:
            del pdf.Root.StructTreeRoot
        
        # Remove metadata
        remove_metadata(pdf)
        
        # Process bookmarks to collapse children
        process_bookmarks(pdf)
        
        # Save with linearization (fast web view)
        # Note: linearize=True enables fast web viewing
        # compress_streams=True optimizes file size
        # Set producer to empty string to avoid pikepdf branding
        pdf.save(
            output_path, 
            linearize=True,
            compress_streams=True
        )
        
        # Re-open the saved PDF and remove any producer metadata that was added
        pdf.close()
        pdf = Pdf.open(output_path, allow_overwriting_input=True)
        
        # Remove Producer metadata added by pikepdf
        if pdf.docinfo and '/Producer' in pdf.docinfo:
            del pdf.docinfo['/Producer']
        
        # Save again without adding new metadata
        pdf.save(output_path)
        pdf.close()
        
        return True, "Success"
    
    except Exception as e:
        return False, str(e)

def process_pdf_batch(root_path):
    """
    Process all PDF files in the given directory and its subdirectories.
    Creates a 'processed' subfolder in each directory containing PDFs.
    """
    root_path = Path(root_path)
    
    if not root_path.exists():
        print(f"Error: Path '{root_path}' does not exist.")
        return
    
    # Find all PDF files recursively (case-insensitive)
    # Use a set to avoid duplicates from case-insensitive matching on Windows
    all_pdf_files = []
    seen_files = set()
    
    for pattern in ["*.pdf", "*.PDF"]:
        for pdf_file in root_path.rglob(pattern):
            # Normalize path to avoid duplicates on case-insensitive filesystems
            normalized_path = pdf_file.resolve()
            if normalized_path not in seen_files:
                seen_files.add(normalized_path)
                all_pdf_files.append(pdf_file)
    
    # Filter out PDFs in 'processed' folders
    pdf_files = [f for f in all_pdf_files if 'processed' not in f.parts]
    
    if not pdf_files:
        print(f"No PDF files found in '{root_path}' (excluding 'processed' folders)")
        return
    
    print(f"Found {len(pdf_files)} PDF file(s) to process.\n")
    
    success_count = 0
    failed_count = 0
    
    for pdf_file in pdf_files:
        # Double check - skip if somehow a processed file got through
        if 'processed' in pdf_file.parts:
            continue
        
        # Create output directory (processed subfolder in the same directory)
        output_dir = pdf_file.parent / "processed"
        output_dir.mkdir(exist_ok=True)
        
        # Output file path
        output_file = output_dir / pdf_file.name
        
        print(f"Processing: {pdf_file.relative_to(root_path)}")
        
        # Process the PDF
        success, message = process_pdf(pdf_file, output_file)
        
        if success:
            print(f"  ✓ Saved to: {output_file.relative_to(root_path)}")
            success_count += 1
        else:
            print(f"  ✗ Failed: {message}")
            failed_count += 1
        print()
    
    # Summary
    print("="*60)
    print(f"Processing complete!")
    print(f"  Successful: {success_count}")
    print(f"  Failed: {failed_count}")
    print(f"  Total: {len(pdf_files)}")
    print("="*60)

def main():
    """Main entry point for the script."""
    if len(sys.argv) < 2:
        print("Usage: python pdf_batch_processor.py <path_to_folder>")
        print("\nExample:")
        print("  python pdf_batch_processor.py /path/to/pdf/folder")
        print("  python pdf_batch_processor.py C:\\Users\\Documents\\PDFs")
        sys.exit(1)
    
    folder_path = sys.argv[1]
    process_pdf_batch(folder_path)

if __name__ == "__main__":
    main()