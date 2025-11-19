# PDF Validator & Processor - Web Application

A modern, user-friendly web application for validating and processing PDF files with session-based management. Built with React and Flask, fully dockerized for easy deployment.

## Features

### Core Functionality
- 📤 **Drag & Drop Upload** - Easy file upload with drag and drop support
- 🔍 **PDF Validation** - Check PDFs for metadata, linearization, and optimization issues
- ⚙️ **Batch Processing** - Process multiple PDFs with customizable settings
- 📥 **Download Options** - Download individual files or all processed files as a ZIP
- 🗑️ **Session Management** - User-specific sessions with ability to clear data
- 🔖 **Bookmark Control** - Configurable bookmark visibility levels

### PDF Processing Features
- ✅ **Fast Web Viewing** - Linearizes PDFs for faster browser loading
- ✅ **Metadata Removal** - Completely removes all metadata (title, author, keywords, etc.)
- ✅ **Bookmark Management** - Configurable bookmark visibility levels
- ✅ **Standardized Settings** - Consistent page layout and viewing preferences
- ✅ **Remove Tagging** - Strips PDF accessibility structure

## Quick Start with Docker

### Prerequisites
- Docker
- Docker Compose

### Running the Application

1. **Clone the repository**
```bash
git clone <repository-url>
cd pdfFDAValidator
```

2. **Start the application**
```bash
docker-compose up -d
```

3. **Access the application**
Open your browser and navigate to:
```
http://localhost
```

The application is now running with:
- Frontend: http://localhost (port 80)
- Backend API: http://localhost:5000

4. **Stop the application**
```bash
docker-compose down
```

5. **Stop and remove all data**
```bash
docker-compose down -v
```

## Configuration

### Environment Variables

Create a `.env` file in the root directory (copy from `.env.example`):

```bash
# Secret key for Flask session management
SECRET_KEY=your-secure-random-key-here
```

Generate a secure secret key:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### Bookmark Levels

The application supports different bookmark visibility levels:

- **Level 0**: All bookmarks expanded (entire bookmark tree visible)
- **Level 1** (default): Only top-level bookmarks visible, children collapsed
- **Level 2**: Top-level + immediate children visible
- **Level 3+**: Specified number of levels visible from the top

## Architecture

### Technology Stack

**Frontend:**
- React 18
- Vite (build tool)
- Axios (HTTP client)
- Nginx (production server)

**Backend:**
- Flask (Python web framework)
- Flask-CORS (Cross-Origin Resource Sharing)
- pikepdf (PDF processing)
- Session-based file management

**Infrastructure:**
- Docker & Docker Compose
- Named volumes for data persistence
- Health checks for both services

### Project Structure

```
pdfFDAValidator/
├── backend/
│   ├── app.py                 # Flask API application
│   ├── pdf_service.py         # PDF processing service
│   ├── requirements.txt       # Python dependencies
│   ├── Dockerfile            # Backend container definition
│   └── .dockerignore
├── frontend/
│   ├── src/
│   │   ├── App.jsx           # Main React component
│   │   ├── App.css           # Application styles
│   │   ├── main.jsx          # React entry point
│   │   └── index.css         # Global styles
│   ├── index.html            # HTML template
│   ├── package.json          # Node dependencies
│   ├── vite.config.js        # Vite configuration
│   ├── nginx.conf            # Nginx configuration
│   ├── Dockerfile            # Frontend container definition
│   └── .dockerignore
├── docker-compose.yml        # Docker orchestration
├── .env.example              # Environment variables template
└── README.md                 # This file
```

## API Endpoints

### Session Management
- `GET /api/session` - Get current session information
- `POST /api/clear` - Clear all files from current session

### File Operations
- `POST /api/upload` - Upload PDF files
- `POST /api/validate` - Validate uploaded PDFs
- `POST /api/process` - Process uploaded PDFs
- `GET /api/download/<filename>` - Download a processed file
- `GET /api/download-all` - Download all processed files as ZIP
- `DELETE /api/delete/<type>/<filename>` - Delete a specific file

### Health Check
- `GET /api/health` - API health check

## Usage Guide

### 1. Upload PDFs
- Drag and drop PDF files onto the upload area, or click to browse
- Multiple files can be uploaded at once
- Only PDF files are accepted

### 2. Configure Settings
- Select bookmark visibility level from the dropdown
- Choose between expanding all bookmarks or collapsing at specific levels

### 3. Validate Files (Optional)
- Click "Validate Files" to check PDFs for issues
- Review the validation report showing:
  - File properties (pages, size, linearization status)
  - Metadata presence
  - Bookmark count
  - Optimization suggestions

### 4. Process Files
- Click "Process Files" to optimize and clean PDFs
- Processing includes:
  - Metadata removal
  - Linearization for fast web viewing
  - Bookmark management
  - Standardized viewer settings

### 5. Download Results
- Download individual files using the "Download" button
- Use "Download All as ZIP" to get all processed files at once

### 6. Clear Session
- Click "Clear All" to remove all uploaded and processed files
- Starts a fresh session

## Development Setup

### Backend Development

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Backend runs on http://localhost:5000

### Frontend Development

```bash
cd frontend
npm install
npm run dev
```

Frontend runs on http://localhost:3000 with hot reload

## Data Persistence

The application uses Docker named volumes for data persistence:

- `pdf_uploads` - Stores uploaded files by session
- `pdf_processed` - Stores processed files by session

To completely reset the application and remove all data:

```bash
docker-compose down -v
```

## Security Considerations

1. **Session Management**: Uses secure HTTP-only cookies
2. **File Validation**: Only accepts PDF files
3. **File Size Limit**: 100MB maximum per file
4. **Session Isolation**: Each user session has isolated file storage
5. **Secret Key**: Use a strong, random secret key in production

## Troubleshooting

### Container fails to start

Check logs:
```bash
docker-compose logs backend
docker-compose logs frontend
```

### Cannot upload files

- Check file size (max 100MB)
- Ensure files are PDFs
- Check browser console for errors

### API connection issues

- Verify backend is running: `docker-compose ps`
- Check backend health: `curl http://localhost:5000/api/health`
- Review nginx proxy configuration

### Data not persisting

- Ensure you're not using `-v` flag when stopping: `docker-compose down` (not `down -v`)
- Check volume status: `docker volume ls`

## Production Deployment

### Recommendations

1. **Environment Variables**
   - Set a strong `SECRET_KEY`
   - Use environment-specific configuration

2. **HTTPS/SSL**
   - Use a reverse proxy (nginx, Traefik, Caddy)
   - Enable SSL certificates (Let's Encrypt)

3. **Resource Limits**
   - Configure memory and CPU limits in docker-compose.yml
   - Adjust file size limits based on needs

4. **Monitoring**
   - Enable health check endpoints
   - Set up logging aggregation
   - Monitor disk usage for volumes

5. **Backup**
   - Regularly backup Docker volumes
   - Consider object storage for processed files

## License

This project is open source and available under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Acknowledgments

- Built with [Flask](https://flask.palletsprojects.com/)
- Built with [React](https://react.dev/)
- PDF processing powered by [pikepdf](https://github.com/pikepdf/pikepdf)
