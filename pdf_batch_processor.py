import os
import sys
from pathlib import Path
import pikepdf
from pikepdf import Pdf, Dictionary, Name
import csv
from datetime import datetime

def get_pdf_properties(pdf_path):
    """
    Extract properties from a PDF file for reporting.
    Returns a dictionary of property names and their values.
    """
    properties = {}
    
    try:
        pdf = Pdf.open(pdf_path)
        
        # Check linearization (fast web view)
        try:
            properties['Fast Web View'] = 'Yes' if pdf.is_linearized else 'No'
        except:
            properties['Fast Web View'] = 'Unknown'
        
        # Page Mode (Navigation Tab)
        if '/PageMode' in pdf.Root:
            page_mode = str(pdf.Root.PageMode)
            properties['Page Mode'] = page_mode.replace('/Name.', '').replace('/', '')
        else:
            properties['Page Mode'] = 'Not Set'
        
        # Page Layout
        if '/PageLayout' in pdf.Root:
            page_layout = str(pdf.Root.PageLayout)
            properties['Page Layout'] = page_layout.replace('/Name.', '').replace('/', '')
        else:
            properties['Page Layout'] = 'Not Set'
        
        # Tagged PDF
        has_mark_info = '/MarkInfo' in pdf.Root
        has_struct_tree = '/StructTreeRoot' in pdf.Root
        properties['Tagged PDF'] = 'Yes' if (has_mark_info or has_struct_tree) else 'No'
        
        # Metadata - Title
        properties['Title'] = str(pdf.docinfo.get('/Title', 'None')) if pdf.docinfo else 'None'
        
        # Metadata - Author
        properties['Author'] = str(pdf.docinfo.get('/Author', 'None')) if pdf.docinfo else 'None'
        
        # Metadata - Subject
        properties['Subject'] = str(pdf.docinfo.get('/Subject', 'None')) if pdf.docinfo else 'None'
        
        # Metadata - Keywords
        properties['Keywords'] = str(pdf.docinfo.get('/Keywords', 'None')) if pdf.docinfo else 'None'
        
        # Metadata - Creator
        properties['Creator'] = str(pdf.docinfo.get('/Creator', 'None')) if pdf.docinfo else 'None'
        
        # Metadata - Producer
        properties['Producer'] = str(pdf.docinfo.get('/Producer', 'None')) if pdf.docinfo else 'None'
        
        # Has XMP Metadata
        properties['XMP Metadata'] = 'Yes' if '/Metadata' in pdf.Root else 'No'
        
        # Bookmarks structure
        if '/Outlines' in pdf.Root and pdf.Root.Outlines and '/First' in pdf.Root.Outlines:
            # Check if first bookmark has children and if they're collapsed
            first_bookmark = pdf.Root.Outlines.First
            if '/First' in first_bookmark and '/Count' in first_bookmark:
                count = int(first_bookmark.Count)
                properties['Child Bookmarks'] = 'Collapsed' if count < 0 else 'Expanded'
            else:
                properties['Child Bookmarks'] = 'No Children'
        else:
            properties['Child Bookmarks'] = 'No Bookmarks'
        
        pdf.close()
        
    except Exception as e:
        properties['Error'] = str(e)
    
    return properties

def create_comparison_report(report_data, output_dir):
    """
    Create a CSV report comparing before and after properties.
    """
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_path = output_dir / f'processing_report_{timestamp}.csv'
    
    with open(report_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        
        # Write header
        writer.writerow(['PDF Name', 'Property', 'Before Processing', 'After Processing'])
        
        # Write data
        for pdf_name, properties in report_data.items():
            for prop_name, values in properties.items():
                writer.writerow([
                    pdf_name,
                    prop_name,
                    values.get('before', 'N/A'),
                    values.get('after', 'N/A')
                ])
    
    return report_path

def collapse_child_bookmarks(outline_item):
    """
    Recursively collapse all child bookmarks (set Count to negative).
    """
    try:
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
    except Exception as e:
        # Silently continue if there's an issue with a specific bookmark
        pass

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
                    if '/Next' in current:
                        current = current.Next
                    else:
                        break
    except Exception as e:
        print(f"  Warning: Could not process bookmarks: {e}")
        # Don't fail the entire processing if bookmarks fail
        pass

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
    2. Set Navigation Tab to Bookmarks Panel (if bookmarks exist) or Page Only (if no bookmarks)
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
        
        # Check if bookmarks exist
        has_bookmarks = ('/Outlines' in pdf.Root and 
                        pdf.Root.Outlines and 
                        '/First' in pdf.Root.Outlines)
        
        # Set the catalog (Root) properties
        # PageMode: UseOutlines if bookmarks exist, UseNone if no bookmarks (Page Only)
        if has_bookmarks:
            pdf.Root.PageMode = Name.UseOutlines  # Bookmarks Panel and Page
            # Process bookmarks to collapse children
            process_bookmarks(pdf)
        else:
            pdf.Root.PageMode = Name.UseNone  # Page Only
        
        # PageLayout: Default (SinglePage is the standard default)
        pdf.Root.PageLayout = Name.SinglePage
        
        # ViewerPreferences for additional settings
        viewer_prefs = pdf.Root.ViewerPreferences
        
        # Remove Tagged PDF structure if it exists
        if '/MarkInfo' in pdf.Root:
            del pdf.Root.MarkInfo
        if '/StructTreeRoot' in pdf.Root:
            del pdf.Root.StructTreeRoot
        
        # Remove metadata (do this before saving)
        remove_metadata(pdf)
        
        # Save with linearization (fast web view)
        pdf.save(output_path, linearize=True)
        pdf.close()
        
        # Re-open and remove any metadata added during save (including pikepdf producer)
        pdf = Pdf.open(output_path, allow_overwriting_input=True)
        
        # Remove all metadata again after save
        remove_metadata(pdf)
        
        # Final save WITH linearization to maintain fast web view
        pdf.save(output_path, linearize=True)
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
    report_data = {}
    
    for pdf_file in pdf_files:
        # Double check - skip if somehow a processed file got through
        if 'processed' in pdf_file.parts:
            continue
        
        # Get properties before processing
        print(f"Processing: {pdf_file.relative_to(root_path)}")
        before_properties = get_pdf_properties(pdf_file)
        
        # Create output directory (processed subfolder in the same directory)
        output_dir = pdf_file.parent / "processed"
        output_dir.mkdir(exist_ok=True)
        
        # Output file path
        output_file = output_dir / pdf_file.name
        
        # Process the PDF
        success, message = process_pdf(pdf_file, output_file)
        
        if success:
            print(f"  ✓ Saved to: {output_file.relative_to(root_path)}")
            
            # Get properties after processing
            after_properties = get_pdf_properties(output_file)
            
            # Store comparison data
            pdf_name = pdf_file.name
            report_data[pdf_name] = {}
            
            # Combine all properties
            all_props = set(before_properties.keys()) | set(after_properties.keys())
            for prop in all_props:
                report_data[pdf_name][prop] = {
                    'before': before_properties.get(prop, 'N/A'),
                    'after': after_properties.get(prop, 'N/A')
                }
            
            success_count += 1
        else:
            print(f"  ✗ Failed: {message}")
            failed_count += 1
        print()
    
    # Generate comparison report
    if report_data:
        # Use the first processed folder as report location
        report_dir = pdf_files[0].parent / "processed"
        report_path = create_comparison_report(report_data, report_dir)
        print(f"\n📊 Comparison report generated: {report_path.relative_to(root_path)}\n")
    
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