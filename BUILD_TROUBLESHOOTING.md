# Docker Build Troubleshooting Guide

## Common Build Errors and Solutions

### Error: apt-get update/install fails

**Error Message:**
```
ERROR [backend 3/7] RUN apt-get update && apt-get install...
```

This error occurs when Docker can't access package repositories during build.

#### Solution 1: Check Network Connection

```bash
# Test your internet connection
ping google.com

# Test DNS resolution
nslookup debian.org
```

If network is down, fix your connection and try again.

#### Solution 2: Clear Docker Build Cache

```bash
# Clean everything and rebuild
docker system prune -a
docker compose build --no-cache
docker compose up -d
```

#### Solution 3: Use Minimal Dockerfile

Build with the minimal version that has fewer dependencies:

```bash
# Build backend with minimal Dockerfile
cd backend
docker build -f Dockerfile.minimal -t pdf-backend .
cd ..

# Update docker-compose.yml to use the built image
# Or use docker-compose.minimal.yml
docker compose -f docker-compose.simple.yml up -d
```

#### Solution 4: Configure Docker DNS

If DNS is the issue, configure Docker to use public DNS:

**Linux/Mac - Create or edit `/etc/docker/daemon.json`:**
```json
{
  "dns": ["8.8.8.8", "8.8.4.4"]
}
```

**Windows - Docker Desktop Settings:**
1. Open Docker Desktop
2. Go to Settings → Docker Engine
3. Add DNS configuration:
```json
{
  "dns": ["8.8.8.8", "8.8.4.4"]
}
```

Then restart Docker:
```bash
# Linux
sudo systemctl restart docker

# Windows/Mac - Restart Docker Desktop
```

#### Solution 5: Retry the Build

Sometimes it's just a temporary network glitch:

```bash
# Try building 2-3 times
docker compose build --no-cache
```

#### Solution 6: Use Different Debian Mirror

Add to beginning of Dockerfile before apt-get:

```dockerfile
RUN sed -i 's/deb.debian.org/mirrors.kernel.org/g' /etc/apt/sources.list
```

## Quick Fix: Run Without Docker

If builds keep failing, run the app directly on your system:

### Backend Setup
```bash
cd backend

# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install pikepdf system dependencies first
# Ubuntu/Debian:
sudo apt-get install libqpdf-dev

# macOS:
brew install qpdf

# Windows: Download from https://github.com/qpdf/qpdf/releases

# Install Python packages
pip install -r requirements.txt

# Run the backend
python app.py
```

Backend will run on http://localhost:5000

### Frontend Setup (separate terminal)
```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

Frontend will run on http://localhost:3000

## Alternative: Simpler Build Process

### Step 1: Build Backend Without Healthcheck Dependencies

Use `backend/Dockerfile.minimal` (already created):

```bash
cd backend
docker build -f Dockerfile.minimal -t pdf-backend:latest .
cd ..
```

### Step 2: Build Frontend
```bash
cd frontend
docker build -t pdf-frontend:latest .
cd ..
```

### Step 3: Run Manually
```bash
# Create network
docker network create pdf-processor-network

# Run backend
docker run -d \
  --name pdf-processor-backend \
  --network pdf-processor-network \
  -p 5000:5000 \
  -v pdf_uploads:/tmp/pdf_uploads \
  -v pdf_processed:/tmp/pdf_processed \
  -e SECRET_KEY=your-secret-key \
  pdf-backend:latest

# Run frontend
docker run -d \
  --name pdf-processor-frontend \
  --network pdf-processor-network \
  -p 80:80 \
  pdf-frontend:latest
```

## Debugging Build Issues

### Get detailed build output:

```bash
# Use plain progress for detailed output
docker compose build --progress=plain --no-cache 2>&1 | tee build.log
```

### Check what's failing:

```bash
# Build just backend
docker compose build backend

# Build just frontend
docker compose build frontend
```

### Test network in build:

Add this to Dockerfile temporarily to test:
```dockerfile
RUN ping -c 3 deb.debian.org || echo "Cannot reach Debian repos"
RUN cat /etc/resolv.conf
```

## System Checks

### Check Docker resources:

```bash
# Check disk space
docker system df

# Clean up
docker system prune -a

# Check if Docker daemon is running
docker ps
```

### Verify Docker configuration:

```bash
# Check Docker version
docker --version
docker compose version

# Check Docker info
docker info
```

## Common Specific Errors

### "Unable to locate package"

The Debian package repository might be temporarily down or your Docker can't reach it.

**Fix:**
```bash
# Try again in a few minutes, or
# Use the Dockerfile.minimal version, or
# Configure different DNS (see Solution 4 above)
```

### "Connection timed out"

Network/firewall issue blocking Docker.

**Fix:**
```bash
# Check if you're behind a corporate firewall
# Configure proxy if needed
export HTTP_PROXY=http://your-proxy:port
export HTTPS_PROXY=http://your-proxy:port

docker compose build
```

### "No space left on device"

Docker is out of disk space.

**Fix:**
```bash
# Clean Docker system
docker system prune -a --volumes

# Check disk usage
df -h
```

## If All Else Fails

### Option 1: Use the pre-built images (when available)
```bash
# If images are pushed to a registry
docker compose pull
docker compose up -d
```

### Option 2: Run natively without Docker
See "Quick Fix: Run Without Docker" section above

### Option 3: Use a different environment
- Try on a different network
- Try on a different machine
- Use a cloud environment (AWS, GCP, Azure)

## Need Help?

When asking for help, provide:

1. **Full error message:**
   ```bash
   docker compose build --progress=plain --no-cache 2>&1 | tee error.log
   ```

2. **System information:**
   ```bash
   docker --version
   docker compose --version
   uname -a  # Linux/Mac
   ```

3. **Network test:**
   ```bash
   ping deb.debian.org
   ping pypi.org
   ```

4. **Docker info:**
   ```bash
   docker info
   docker system df
   ```

Share the error.log and this information when requesting help.
