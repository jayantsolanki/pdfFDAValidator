"""
Flask API for PDF Processing with Session Management
"""

from flask import Flask, request, jsonify, send_file, session
from flask_cors import CORS
from werkzeug.utils import secure_filename
from pathlib import Path
import uuid
import shutil
from datetime import datetime, timedelta
import os

from pdf_service import PDFProcessor

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size
app.config['UPLOAD_FOLDER'] = Path('/tmp/pdf_uploads')
app.config['PROCESSED_FOLDER'] = Path('/tmp/pdf_processed')
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)

# Enable CORS for React frontend
CORS(app, supports_credentials=True, origins=['http://localhost:3000', 'http://localhost:5173'])

# Ensure upload directories exist
app.config['UPLOAD_FOLDER'].mkdir(parents=True, exist_ok=True)
app.config['PROCESSED_FOLDER'].mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {'pdf'}


def allowed_file(filename):
    """Check if file has allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_session_id():
    """Get or create session ID"""
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
        session.permanent = True
    return session['session_id']


def get_session_folder(folder_type='upload'):
    """Get session-specific folder path"""
    session_id = get_session_id()
    base_folder = app.config['UPLOAD_FOLDER'] if folder_type == 'upload' else app.config['PROCESSED_FOLDER']
    session_folder = base_folder / session_id
    session_folder.mkdir(parents=True, exist_ok=True)
    return session_folder


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})


@app.route('/api/session', methods=['GET'])
def get_session_info():
    """Get current session information"""
    session_id = get_session_id()
    upload_folder = get_session_folder('upload')
    processed_folder = get_session_folder('processed')

    uploaded_files = []
    processed_files = []

    # Get uploaded files info
    if upload_folder.exists():
        for file_path in upload_folder.glob('*.pdf'):
            uploaded_files.append({
                'name': file_path.name,
                'size': file_path.stat().st_size,
                'uploaded_at': datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
            })

    # Get processed files info
    if processed_folder.exists():
        for file_path in processed_folder.glob('*.pdf'):
            processed_files.append({
                'name': file_path.name,
                'size': file_path.stat().st_size,
                'processed_at': datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
            })

    return jsonify({
        'session_id': session_id,
        'uploaded_files': uploaded_files,
        'processed_files': processed_files
    })


@app.route('/api/upload', methods=['POST'])
def upload_files():
    """Upload PDF files to session folder"""
    if 'files' not in request.files:
        return jsonify({'error': 'No files provided'}), 400

    files = request.files.getlist('files')
    if not files:
        return jsonify({'error': 'No files selected'}), 400

    session_folder = get_session_folder('upload')
    uploaded_files = []
    errors = []

    for file in files:
        if file.filename == '':
            continue

        if not allowed_file(file.filename):
            errors.append(f'{file.filename}: Only PDF files are allowed')
            continue

        filename = secure_filename(file.filename)
        file_path = session_folder / filename

        try:
            file.save(str(file_path))
            uploaded_files.append({
                'name': filename,
                'size': file_path.stat().st_size,
                'uploaded_at': datetime.now().isoformat()
            })
        except Exception as e:
            errors.append(f'{filename}: {str(e)}')

    return jsonify({
        'uploaded': uploaded_files,
        'errors': errors
    })


@app.route('/api/validate', methods=['POST'])
def validate_files():
    """Validate uploaded PDF files and check for issues"""
    data = request.get_json() or {}
    bookmark_level = data.get('bookmark_level', 1)

    session_folder = get_session_folder('upload')
    pdf_files = list(session_folder.glob('*.pdf'))

    if not pdf_files:
        return jsonify({'error': 'No PDF files found in session'}), 400

    processor = PDFProcessor(bookmark_level=bookmark_level)
    results = []

    for pdf_file in pdf_files:
        validation = processor.validate_pdf(pdf_file)
        validation['filename'] = pdf_file.name
        results.append(validation)

    return jsonify({
        'validations': results,
        'total_files': len(results)
    })


@app.route('/api/process', methods=['POST'])
def process_files():
    """Process uploaded PDF files"""
    data = request.get_json() or {}
    bookmark_level = data.get('bookmark_level', 1)

    session_folder = get_session_folder('upload')
    processed_folder = get_session_folder('processed')
    pdf_files = list(session_folder.glob('*.pdf'))

    if not pdf_files:
        return jsonify({'error': 'No PDF files found in session'}), 400

    processor = PDFProcessor(bookmark_level=bookmark_level)
    results = []

    for pdf_file in pdf_files:
        output_path = processed_folder / pdf_file.name
        result = processor.process_pdf(pdf_file, output_path)
        results.append(result)

    successful = sum(1 for r in results if r['success'])
    failed = len(results) - successful

    return jsonify({
        'results': results,
        'summary': {
            'total': len(results),
            'successful': successful,
            'failed': failed
        }
    })


@app.route('/api/download/<filename>', methods=['GET'])
def download_file(filename):
    """Download a processed file"""
    filename = secure_filename(filename)
    processed_folder = get_session_folder('processed')
    file_path = processed_folder / filename

    if not file_path.exists():
        return jsonify({'error': 'File not found'}), 404

    return send_file(
        str(file_path),
        as_attachment=True,
        download_name=filename,
        mimetype='application/pdf'
    )


@app.route('/api/download-all', methods=['GET'])
def download_all():
    """Download all processed files as a zip"""
    import zipfile
    from io import BytesIO

    processed_folder = get_session_folder('processed')
    pdf_files = list(processed_folder.glob('*.pdf'))

    if not pdf_files:
        return jsonify({'error': 'No processed files found'}), 404

    # Create zip file in memory
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for pdf_file in pdf_files:
            zip_file.write(str(pdf_file), pdf_file.name)

    zip_buffer.seek(0)
    return send_file(
        zip_buffer,
        as_attachment=True,
        download_name=f'processed_pdfs_{datetime.now().strftime("%Y%m%d_%H%M%S")}.zip',
        mimetype='application/zip'
    )


@app.route('/api/clear', methods=['POST'])
def clear_session():
    """Clear all files from current session"""
    session_id = get_session_id()

    upload_folder = app.config['UPLOAD_FOLDER'] / session_id
    processed_folder = app.config['PROCESSED_FOLDER'] / session_id

    try:
        if upload_folder.exists():
            shutil.rmtree(upload_folder)
        if processed_folder.exists():
            shutil.rmtree(processed_folder)

        return jsonify({'message': 'Session cleared successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/delete/<file_type>/<filename>', methods=['DELETE'])
def delete_file(file_type, filename):
    """Delete a specific file from session"""
    if file_type not in ['upload', 'processed']:
        return jsonify({'error': 'Invalid file type'}), 400

    filename = secure_filename(filename)
    session_folder = get_session_folder(file_type)
    file_path = session_folder / filename

    try:
        if file_path.exists():
            file_path.unlink()
            return jsonify({'message': f'File {filename} deleted successfully'})
        else:
            return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle file too large error"""
    return jsonify({'error': 'File too large. Maximum size is 100MB'}), 413


@app.errorhandler(500)
def internal_server_error(error):
    """Handle internal server error"""
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=os.environ.get('FLASK_ENV') == 'development'
    )
