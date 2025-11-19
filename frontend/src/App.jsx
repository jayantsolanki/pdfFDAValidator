import React, { useState, useEffect, useRef } from 'react'
import axios from 'axios'
import './App.css'

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api'

// Configure axios to send credentials
axios.defaults.withCredentials = true

function App() {
  const [sessionInfo, setSessionInfo] = useState(null)
  const [uploadedFiles, setUploadedFiles] = useState([])
  const [processedFiles, setProcessedFiles] = useState([])
  const [validationResults, setValidationResults] = useState([])
  const [bookmarkLevel, setBookmarkLevel] = useState(1)
  const [isUploading, setIsUploading] = useState(false)
  const [isProcessing, setIsProcessing] = useState(false)
  const [isValidating, setIsValidating] = useState(false)
  const [dragActive, setDragActive] = useState(false)
  const [message, setMessage] = useState(null)
  const fileInputRef = useRef(null)

  useEffect(() => {
    loadSessionInfo()
  }, [])

  const loadSessionInfo = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/session`)
      setSessionInfo(response.data)
      setUploadedFiles(response.data.uploaded_files || [])
      setProcessedFiles(response.data.processed_files || [])
    } catch (error) {
      showMessage('Error loading session info', 'error')
    }
  }

  const showMessage = (text, type = 'info') => {
    setMessage({ text, type })
    setTimeout(() => setMessage(null), 5000)
  }

  const handleDrag = (e) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true)
    } else if (e.type === 'dragleave') {
      setDragActive(false)
    }
  }

  const handleDrop = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)

    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFiles(e.dataTransfer.files)
    }
  }

  const handleFileInput = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      handleFiles(e.target.files)
    }
  }

  const handleFiles = async (files) => {
    const formData = new FormData()
    let pdfCount = 0

    for (let i = 0; i < files.length; i++) {
      if (files[i].type === 'application/pdf') {
        formData.append('files', files[i])
        pdfCount++
      }
    }

    if (pdfCount === 0) {
      showMessage('Please select PDF files only', 'error')
      return
    }

    setIsUploading(true)
    try {
      const response = await axios.post(`${API_BASE_URL}/upload`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })

      if (response.data.uploaded.length > 0) {
        showMessage(`Successfully uploaded ${response.data.uploaded.length} file(s)`, 'success')
        await loadSessionInfo()
        setValidationResults([])
      }

      if (response.data.errors.length > 0) {
        showMessage(`Errors: ${response.data.errors.join(', ')}`, 'error')
      }
    } catch (error) {
      showMessage('Error uploading files: ' + (error.response?.data?.error || error.message), 'error')
    } finally {
      setIsUploading(false)
    }
  }

  const handleValidate = async () => {
    setIsValidating(true)
    setValidationResults([])

    try {
      const response = await axios.post(`${API_BASE_URL}/validate`, {
        bookmark_level: bookmarkLevel
      })

      setValidationResults(response.data.validations)
      showMessage(`Validated ${response.data.total_files} file(s)`, 'success')
    } catch (error) {
      showMessage('Error validating files: ' + (error.response?.data?.error || error.message), 'error')
    } finally {
      setIsValidating(false)
    }
  }

  const handleProcess = async () => {
    setIsProcessing(true)

    try {
      const response = await axios.post(`${API_BASE_URL}/process`, {
        bookmark_level: bookmarkLevel
      })

      showMessage(
        `Processed ${response.data.summary.successful} file(s) successfully, ${response.data.summary.failed} failed`,
        response.data.summary.failed > 0 ? 'warning' : 'success'
      )

      await loadSessionInfo()
      setValidationResults([])
    } catch (error) {
      showMessage('Error processing files: ' + (error.response?.data?.error || error.message), 'error')
    } finally {
      setIsProcessing(false)
    }
  }

  const handleDownload = async (filename) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/download/${filename}`, {
        responseType: 'blob'
      })

      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', filename)
      document.body.appendChild(link)
      link.click()
      link.remove()
      window.URL.revokeObjectURL(url)
    } catch (error) {
      showMessage('Error downloading file', 'error')
    }
  }

  const handleDownloadAll = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/download-all`, {
        responseType: 'blob'
      })

      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `processed_pdfs_${Date.now()}.zip`)
      document.body.appendChild(link)
      link.click()
      link.remove()
      window.URL.revokeObjectURL(url)
    } catch (error) {
      showMessage('Error downloading files', 'error')
    }
  }

  const handleClear = async () => {
    if (!window.confirm('Are you sure you want to clear all files from this session?')) {
      return
    }

    try {
      await axios.post(`${API_BASE_URL}/clear`)
      showMessage('Session cleared successfully', 'success')
      setUploadedFiles([])
      setProcessedFiles([])
      setValidationResults([])
      await loadSessionInfo()
    } catch (error) {
      showMessage('Error clearing session: ' + (error.response?.data?.error || error.message), 'error')
    }
  }

  const handleDeleteFile = async (fileType, filename) => {
    try {
      await axios.delete(`${API_BASE_URL}/delete/${fileType}/${filename}`)
      showMessage(`Deleted ${filename}`, 'success')
      await loadSessionInfo()
      if (fileType === 'upload') {
        setValidationResults([])
      }
    } catch (error) {
      showMessage('Error deleting file', 'error')
    }
  }

  const formatBytes = (bytes) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
  }

  return (
    <div className="app">
      <header className="header">
        <h1>PDF Validator & Processor</h1>
        <p className="subtitle">Upload, validate, and process PDF files with metadata removal and optimization</p>
      </header>

      {message && (
        <div className={`message message-${message.type}`}>
          {message.text}
        </div>
      )}

      <div className="container">
        {/* Upload Section */}
        <div className="section">
          <h2>Upload PDFs</h2>
          <div
            className={`dropzone ${dragActive ? 'active' : ''}`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
          >
            <input
              ref={fileInputRef}
              type="file"
              multiple
              accept=".pdf"
              onChange={handleFileInput}
              style={{ display: 'none' }}
            />
            <div className="dropzone-content">
              <svg className="upload-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
              </svg>
              <p>Drag & drop PDF files here or click to browse</p>
              <p className="text-muted">Multiple files supported</p>
            </div>
          </div>

          {isUploading && <div className="loading">Uploading files...</div>}

          {uploadedFiles.length > 0 && (
            <div className="file-list">
              <h3>Uploaded Files ({uploadedFiles.length})</h3>
              {uploadedFiles.map((file, idx) => (
                <div key={idx} className="file-item">
                  <div className="file-info">
                    <span className="file-name">{file.name}</span>
                    <span className="file-size">{formatBytes(file.size)}</span>
                  </div>
                  <button
                    className="btn-delete"
                    onClick={() => handleDeleteFile('upload', file.name)}
                    title="Delete file"
                  >
                    ×
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Settings Section */}
        {uploadedFiles.length > 0 && (
          <div className="section">
            <h2>Processing Settings</h2>
            <div className="settings">
              <label>
                Bookmark Visibility Level:
                <select
                  value={bookmarkLevel}
                  onChange={(e) => setBookmarkLevel(Number(e.target.value))}
                  className="select"
                >
                  <option value="0">Expand All Bookmarks</option>
                  <option value="1">Top-level Only (Default)</option>
                  <option value="2">Top-level + 1 Child</option>
                  <option value="3">Top-level + 2 Children</option>
                </select>
              </label>
            </div>
          </div>
        )}

        {/* Actions Section */}
        {uploadedFiles.length > 0 && (
          <div className="section">
            <h2>Actions</h2>
            <div className="actions">
              <button
                className="btn btn-primary"
                onClick={handleValidate}
                disabled={isValidating}
              >
                {isValidating ? 'Validating...' : 'Validate Files'}
              </button>
              <button
                className="btn btn-success"
                onClick={handleProcess}
                disabled={isProcessing}
              >
                {isProcessing ? 'Processing...' : 'Process Files'}
              </button>
              <button
                className="btn btn-danger"
                onClick={handleClear}
              >
                Clear All
              </button>
            </div>
          </div>
        )}

        {/* Validation Results */}
        {validationResults.length > 0 && (
          <div className="section">
            <h2>Validation Results</h2>
            <div className="validation-results">
              {validationResults.map((result, idx) => (
                <div key={idx} className="validation-item">
                  <h4>{result.filename}</h4>
                  {result.valid ? (
                    <>
                      <div className="properties">
                        <p><strong>Pages:</strong> {result.properties.page_count}</p>
                        <p><strong>Size:</strong> {result.properties.file_size_kb} KB</p>
                        <p><strong>Linearized:</strong> {result.properties.is_linearized ? '✓ Yes' : '✗ No'}</p>
                        <p><strong>Has Metadata:</strong> {result.properties.has_metadata ? '✓ Yes' : '✗ No'}</p>
                        <p><strong>Bookmarks:</strong> {result.properties.bookmark_count}</p>
                      </div>
                      {result.issues.length > 0 && (
                        <div className="issues">
                          <strong>Issues Found:</strong>
                          <ul>
                            {result.issues.map((issue, i) => (
                              <li key={i}>{issue}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                      {result.issues.length === 0 && (
                        <p className="text-success">No issues found - file is already optimized!</p>
                      )}
                    </>
                  ) : (
                    <p className="text-error">Error: {result.error}</p>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Processed Files */}
        {processedFiles.length > 0 && (
          <div className="section">
            <h2>Processed Files ({processedFiles.length})</h2>
            <div className="actions">
              <button className="btn btn-primary" onClick={handleDownloadAll}>
                Download All as ZIP
              </button>
            </div>
            <div className="file-list">
              {processedFiles.map((file, idx) => (
                <div key={idx} className="file-item">
                  <div className="file-info">
                    <span className="file-name">{file.name}</span>
                    <span className="file-size">{formatBytes(file.size)}</span>
                  </div>
                  <div className="file-actions">
                    <button
                      className="btn btn-sm"
                      onClick={() => handleDownload(file.name)}
                    >
                      Download
                    </button>
                    <button
                      className="btn-delete"
                      onClick={() => handleDeleteFile('processed', file.name)}
                      title="Delete file"
                    >
                      ×
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Session Info */}
        {sessionInfo && (
          <div className="section session-info">
            <details>
              <summary>Session Info</summary>
              <p><strong>Session ID:</strong> <code>{sessionInfo.session_id}</code></p>
            </details>
          </div>
        )}
      </div>
    </div>
  )
}

export default App
