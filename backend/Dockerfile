# Backend Dockerfile for PDF Processor API
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies required for pikepdf
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libqpdf-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directories for uploads and processed files
RUN mkdir -p /tmp/pdf_uploads /tmp/pdf_processed

# Expose port
EXPOSE 5000

# Set environment variables
ENV FLASK_APP=app.py
ENV PYTHONUNBUFFERED=1

# Run the application
CMD ["python", "app.py"]
