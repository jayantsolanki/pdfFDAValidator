# PDF Validator & Processor - Web Application Documentation

## Overview

This project has been converted from a command-line PDF batch processor into a modern, user session-based web application. The application allows users to upload, validate, and process PDF files through an intuitive web interface with complete session isolation and data management capabilities.

## Architecture

### Technology Stack

**Backend:**
- **Flask** - Lightweight Python web framework
- **Flask-CORS** - Cross-Origin Resource Sharing support
- **pikepdf** - PDF manipulation library
- **Session Management** - Cookie-based user sessions with file isolation

**Frontend:**
- **React 18** - Modern UI library
- **Vite** - Fast build tool and dev server
- **Axios** - HTTP client for API communication
- **CSS3** - Modern responsive styling

**Infrastructure:**
- **Docker** - Containerization
- **Docker Compose** - Multi-container orchestration
- **Nginx** - Production web server and reverse proxy

### System Design

```
┌─────────────────────────────────────────────────────────┐
│                       User Browser                       │
│                    http://localhost                      │
└───────────────────────┬─────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│                  Nginx (Frontend Container)              │
│  ┌──────────────┐              ┌───────────────────┐   │
│  │ Static Files │              │   Reverse Proxy   │   │
│  │ (React App)  │              │   /api -> backend │   │
│  └──────────────┘              └───────────────────┘   │
└───────────────────────────────────┬─────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────┐
│                Flask API (Backend Container)             │
│  ┌──────────────────┐  ┌─────────────────────────────┐ │
│  │ Session Manager  │  │    PDF Service Module       │ │
│  │ - File Upload    │  │ - Validation                │ │
│  │ - File Storage   │  │ - Processing                │ │
│  │ - Session Mgmt   │  │ - Metadata Removal          │ │
│  └──────────────────┘  └─────────────────────────────┘ │
└───────────────────────────────────┬─────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────┐
│              Docker Named Volumes                        │
│  ┌──────────────────┐  ┌─────────────────────────────┐ │
│  │  pdf_uploads/    │  │    pdf_processed/          │ │
│  │  └─ session_id/  │  │    └─ session_id/          │ │
│  └──────────────────┘  └─────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

## Features

### 1. User Session Management

Each user gets an isolated session with:
- Unique session ID (UUID)
- Separate storage for uploaded and processed files
- Session persistence for 24 hours
- Secure HTTP-only cookies

### 2. File Upload

**Capabilities:**
- Drag & drop interface
- Multiple file selection
- Click to browse option
- PDF-only validation
- 100MB per file size limit
- Real-time upload progress

**Implementation:**
```javascript
// Frontend: App.jsx
- Drag and drop event handlers
- File type validation
- FormData API for multipart upload
- Axios with progress tracking

// Backend: app.py
- Werkzeug secure_filename
- Session-based folder creation
- File existence checks
```

### 3. PDF Validation

**Checks Performed:**
- ✅ File size and page count
- ✅ Linearization status (fast web view)
- ✅ Metadata presence
- ✅ Bookmark count
- ✅ Document properties

**Validation Output:**
```json
{
  "valid": true,
  "properties": {
    "file_size_kb": 1234.56,
    "page_count": 50,
    "is_linearized": false,
    "has_metadata": true,
    "bookmark_count": 15
  },
  "issues": [
    "Contains metadata that can be removed",
    "Not linearized (not optimized for fast web viewing)",
    "Has 15 bookmarks that can be managed"
  ]
}
```

### 4. PDF Processing

**Operations:**
1. **Linearization** - Enables fast web viewing
2. **Metadata Removal** - Strips all identifying information
   - Title, Author, Subject, Keywords
   - Creator, Producer
   - Creation/Modification dates
   - XMP metadata streams
3. **Bookmark Management** - Configurable visibility levels
4. **Standardized Settings** - Consistent page layout and magnification
5. **Structure Cleaning** - Removes tagged PDF elements

**Bookmark Levels:**
- **Level 0**: All bookmarks expanded
- **Level 1**: Top-level only (default)
- **Level 2**: Top-level + immediate children
- **Level 3+**: Custom depth levels

### 5. Download Options

**Individual Files:**
```http
GET /api/download/<filename>
```
- Single file download
- Maintains original filename
- PDF content type

**Bulk Download:**
```http
GET /api/download-all
```
- ZIP archive of all processed files
- Timestamp-based filename
- In-memory ZIP creation

### 6. Session Management

**Clear Session:**
```http
POST /api/clear
```
- Removes all uploaded files
- Removes all processed files
- Maintains session ID for reuse

**Delete Individual Files:**
```http
DELETE /api/delete/<type>/<filename>
```
- Delete from upload or processed folder
- Type: 'upload' or 'processed'

## API Reference

### Session Endpoints

#### Get Session Info
```http
GET /api/session
```

**Response:**
```json
{
  "session_id": "uuid-string",
  "uploaded_files": [
    {
      "name": "document.pdf",
      "size": 1024000,
      "uploaded_at": "2025-11-19T12:00:00"
    }
  ],
  "processed_files": [
    {
      "name": "document.pdf",
      "size": 980000,
      "processed_at": "2025-11-19T12:05:00"
    }
  ]
}
```

### File Operation Endpoints

#### Upload Files
```http
POST /api/upload
Content-Type: multipart/form-data
```

**Request:**
```
files: [File, File, ...]
```

**Response:**
```json
{
  "uploaded": [
    {"name": "doc1.pdf", "size": 1024, "uploaded_at": "..."}
  ],
  "errors": []
}
```

#### Validate Files
```http
POST /api/validate
Content-Type: application/json
```

**Request:**
```json
{
  "bookmark_level": 1
}
```

**Response:**
```json
{
  "validations": [
    {
      "filename": "doc.pdf",
      "valid": true,
      "properties": {...},
      "issues": [...]
    }
  ],
  "total_files": 1
}
```

#### Process Files
```http
POST /api/process
Content-Type: application/json
```

**Request:**
```json
{
  "bookmark_level": 1
}
```

**Response:**
```json
{
  "results": [
    {
      "success": true,
      "filename": "doc.pdf",
      "before": {...},
      "after": {...}
    }
  ],
  "summary": {
    "total": 1,
    "successful": 1,
    "failed": 0
  }
}
```

## Deployment

### Docker Compose (Recommended)

**Quick Start:**
```bash
# Linux/macOS
./start.sh

# Windows
start.bat

# Or manually
docker compose up -d
```

**Access:**
- Frontend: http://localhost
- Backend: http://localhost:5000

**Environment Configuration:**
```bash
# .env file
SECRET_KEY=your-secure-random-key-here
```

**Generate Secure Key:**
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### Manual Deployment

#### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

#### Frontend
```bash
cd frontend
npm install
npm run build
npm run preview
# Or for development:
npm run dev
```

### Production Considerations

1. **Security:**
   - Set strong SECRET_KEY
   - Use HTTPS/SSL
   - Configure CORS origins
   - Enable rate limiting
   - Implement authentication if needed

2. **Scaling:**
   - Add load balancer
   - Use Redis for session storage
   - Implement file cleanup cron jobs
   - Configure max file sizes
   - Set resource limits

3. **Monitoring:**
   - Enable health checks
   - Set up logging aggregation
   - Monitor disk usage
   - Track API response times
   - Alert on errors

4. **Backup:**
   - Regular volume backups
   - Database backups (if added)
   - Configuration backups

## Development

### Project Structure

```
pdfFDAValidator/
├── backend/
│   ├── app.py                 # Flask API application
│   │   - Session management
│   │   - File upload/download
│   │   - API endpoints
│   │
│   ├── pdf_service.py         # PDF processing service
│   │   - PDFProcessor class
│   │   - Validation logic
│   │   - Processing operations
│   │
│   ├── requirements.txt       # Python dependencies
│   ├── Dockerfile            # Backend container
│   └── .dockerignore
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx           # Main React component
│   │   │   - File upload UI
│   │   │   - Validation display
│   │   │   - Processing controls
│   │   │   - Download management
│   │   │
│   │   ├── App.css           # Component styles
│   │   ├── main.jsx          # React entry point
│   │   └── index.css         # Global styles
│   │
│   ├── index.html            # HTML template
│   ├── package.json          # Node dependencies
│   ├── vite.config.js        # Build configuration
│   ├── nginx.conf            # Nginx configuration
│   ├── Dockerfile            # Frontend container
│   └── .dockerignore
│
├── docker-compose.yml         # Container orchestration
├── .env.example              # Environment template
├── start.sh                  # Linux/macOS startup
├── start.bat                 # Windows startup
├── WEB_APP_README.md         # User documentation
└── claude.md                 # This file
```

### Backend Code Structure

**app.py - Main API Application:**
- Flask app initialization
- CORS configuration
- Session management functions
- API route handlers
- Error handlers

**pdf_service.py - PDF Processing:**
- `PDFProcessor` class
  - `process_pdf()` - Main processing function
  - `validate_pdf()` - Validation function
  - `remove_metadata()` - Metadata removal
  - `process_bookmarks()` - Bookmark management
  - `get_pdf_properties()` - Property extraction

### Frontend Code Structure

**App.jsx - Main Component:**
- State management (hooks)
- API communication (axios)
- File upload handling
- Drag & drop implementation
- UI rendering

**Component Breakdown:**
1. Header section
2. Message notifications
3. Upload dropzone
4. Uploaded files list
5. Processing settings
6. Action buttons
7. Validation results display
8. Processed files list
9. Session info

### Key Implementation Details

#### Session Management
```python
# Backend: Session ID generation
def get_session_id():
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
        session.permanent = True
    return session['session_id']

# Session folder isolation
def get_session_folder(folder_type='upload'):
    session_id = get_session_id()
    base_folder = app.config['UPLOAD_FOLDER'] if folder_type == 'upload'
                  else app.config['PROCESSED_FOLDER']
    session_folder = base_folder / session_id
    session_folder.mkdir(parents=True, exist_ok=True)
    return session_folder
```

#### File Upload (Frontend)
```javascript
// Drag and drop handling
const handleDrop = (e) => {
  e.preventDefault()
  setDragActive(false)
  if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
    handleFiles(e.dataTransfer.files)
  }
}

// File upload
const handleFiles = async (files) => {
  const formData = new FormData()
  for (let i = 0; i < files.length; i++) {
    if (files[i].type === 'application/pdf') {
      formData.append('files', files[i])
    }
  }
  await axios.post(`${API_BASE_URL}/upload`, formData)
}
```

#### PDF Processing
```python
# Backend: PDF processing flow
def process_pdf(self, input_path, output_path):
    # 1. Get before properties
    result['before'] = self.get_pdf_properties(input_path)

    # 2. Open and modify PDF
    with pikepdf.open(input_path) as pdf:
        pdf.Root.PageMode = pikepdf.Name.UseNone
        pdf.Root.PageLayout = pikepdf.Name.SinglePage
        self.remove_metadata(pdf)
        self.process_bookmarks(pdf, self.bookmark_level)
        pdf.save(output_path, linearize=True)

    # 3. Double-clean metadata
    with pikepdf.open(output_path, allow_overwriting_input=True) as pdf:
        self.remove_metadata(pdf)
        pdf.save(output_path, linearize=True)

    # 4. Get after properties
    result['after'] = self.get_pdf_properties(output_path)
    return result
```

## Testing

### Manual Testing Checklist

**Upload Functionality:**
- [ ] Drag and drop single PDF
- [ ] Drag and drop multiple PDFs
- [ ] Click to browse and select files
- [ ] Upload non-PDF file (should reject)
- [ ] Upload file > 100MB (should reject)

**Validation:**
- [ ] Validate files with metadata
- [ ] Validate linearized files
- [ ] Validate files with bookmarks
- [ ] Validate already-optimized files

**Processing:**
- [ ] Process with default settings (level 1)
- [ ] Process with level 0 (expand all)
- [ ] Process with level 2
- [ ] Process multiple files
- [ ] Verify metadata removal
- [ ] Verify linearization

**Download:**
- [ ] Download single processed file
- [ ] Download all as ZIP
- [ ] Verify file integrity after download

**Session Management:**
- [ ] Delete individual uploaded file
- [ ] Delete individual processed file
- [ ] Clear entire session
- [ ] Verify session persistence across page refresh

**Error Handling:**
- [ ] Upload with no files selected
- [ ] Process with no files uploaded
- [ ] Download non-existent file
- [ ] Network error handling

### API Testing

```bash
# Health check
curl http://localhost:5000/api/health

# Get session info
curl -b cookies.txt -c cookies.txt http://localhost:5000/api/session

# Upload file
curl -b cookies.txt -c cookies.txt \
  -F "files=@test.pdf" \
  http://localhost:5000/api/upload

# Validate files
curl -b cookies.txt -c cookies.txt \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"bookmark_level": 1}' \
  http://localhost:5000/api/validate

# Process files
curl -b cookies.txt -c cookies.txt \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"bookmark_level": 1}' \
  http://localhost:5000/api/process

# Download file
curl -b cookies.txt -c cookies.txt \
  -O -J \
  http://localhost:5000/api/download/test.pdf

# Clear session
curl -b cookies.txt -c cookies.txt \
  -X POST \
  http://localhost:5000/api/clear
```

## Troubleshooting

### Common Issues

**1. Container fails to start**
```bash
# Check logs
docker compose logs backend
docker compose logs frontend

# Restart services
docker compose restart

# Rebuild containers
docker compose up -d --build
```

**2. Cannot upload files**
- Check file size (< 100MB)
- Verify file is PDF
- Check browser console for errors
- Verify backend is running

**3. API connection errors**
```bash
# Test backend health
curl http://localhost:5000/api/health

# Check container networking
docker compose ps
docker network inspect pdf-processor-network
```

**4. Session data not persisting**
```bash
# List volumes
docker volume ls

# Inspect volume
docker volume inspect pdfFDAValidator_pdf_uploads

# Don't use -v flag when stopping
docker compose down  # Good
docker compose down -v  # Removes volumes!
```

**5. Port conflicts**
```bash
# Check what's using port 80 or 5000
sudo lsof -i :80
sudo lsof -i :5000

# Modify docker-compose.yml ports if needed
```

### Debug Mode

**Backend Debug:**
```bash
# Set in .env
FLASK_ENV=development

# Or export
export FLASK_ENV=development
python backend/app.py
```

**Frontend Debug:**
```bash
# Development mode with hot reload
cd frontend
npm run dev

# Check API proxy
# vite.config.js proxy configuration
```

## Performance Optimization

### Backend

1. **File Processing:**
   - Process files asynchronously
   - Implement job queue (Celery)
   - Add progress tracking

2. **Session Storage:**
   - Use Redis for sessions
   - Implement session cleanup
   - Set appropriate TTL

3. **File Storage:**
   - Implement file size limits
   - Add compression
   - Use object storage (S3)

### Frontend

1. **Bundle Size:**
   - Code splitting
   - Lazy loading
   - Tree shaking

2. **Asset Optimization:**
   - Image optimization
   - CSS minification
   - Gzip compression

3. **API Calls:**
   - Request debouncing
   - Response caching
   - Parallel requests

## Security Considerations

### Backend Security

1. **Input Validation:**
   - File type checking
   - File size limits
   - Filename sanitization
   - Path traversal prevention

2. **Session Security:**
   - HTTP-only cookies
   - Secure flag (HTTPS)
   - SameSite attribute
   - Session timeout

3. **File Security:**
   - Isolated storage
   - Permission checks
   - Malware scanning
   - Content-type verification

### Frontend Security

1. **XSS Prevention:**
   - React auto-escaping
   - DOMPurify for user input
   - CSP headers

2. **CSRF Protection:**
   - SameSite cookies
   - CSRF tokens (if needed)

3. **API Security:**
   - Credentials: 'include'
   - Validate responses
   - Error message sanitization

## Future Enhancements

### Planned Features

1. **User Authentication:**
   - User accounts
   - Password protection
   - OAuth integration

2. **Advanced Processing:**
   - PDF merging
   - Page extraction
   - Watermarking
   - OCR support

3. **Batch Operations:**
   - Queue management
   - Progress tracking
   - Email notifications
   - Scheduled processing

4. **Analytics:**
   - Processing statistics
   - Usage metrics
   - Performance monitoring

5. **Storage Options:**
   - Cloud storage integration
   - FTP/SFTP support
   - WebDAV support

### Technical Improvements

1. **Performance:**
   - Background job processing
   - Caching layer
   - CDN integration
   - Database for metadata

2. **Scalability:**
   - Horizontal scaling
   - Load balancing
   - Distributed storage
   - Microservices architecture

3. **Developer Experience:**
   - API documentation (Swagger)
   - Unit tests
   - Integration tests
   - CI/CD pipeline

## Changelog

### Version 2.0.0 (Current)

**Major Changes:**
- ✅ Converted from CLI to web application
- ✅ Added React frontend with modern UI
- ✅ Implemented Flask REST API backend
- ✅ Added session-based file management
- ✅ Dockerized entire application
- ✅ Added validation before processing
- ✅ Implemented file download (individual and bulk)
- ✅ Added clear session functionality
- ✅ Created comprehensive documentation

**Features:**
- Drag & drop file upload
- Real-time validation
- Configurable processing settings
- Individual and bulk downloads
- Session persistence
- Responsive design

**Infrastructure:**
- Docker containers for backend and frontend
- Docker Compose orchestration
- Nginx reverse proxy
- Named volumes for data persistence
- Health checks

### Version 1.0.0 (Original CLI)

**Features:**
- Command-line PDF batch processing
- Metadata removal
- Linearization
- Bookmark management
- Recursive folder processing

## Support

### Resources

- **User Documentation:** WEB_APP_README.md
- **Original CLI Documentation:** README.md
- **API Documentation:** This file (claude.md)

### Getting Help

1. Check the troubleshooting section
2. Review error messages in logs
3. Verify configuration files
4. Test with minimal example
5. Check Docker container status

## License

This project is open source and available under the MIT License.

## Contributors

- Original CLI tool: PDF Batch Processor
- Web application conversion: Claude Code
- Framework: Flask, React, Docker

---

**Last Updated:** 2025-11-19
**Version:** 2.0.0
**Status:** Production Ready
