# Docker Compose Troubleshooting Guide

## Common Issues and Solutions

### 1. Docker or Docker Compose Not Installed

**Error:**
```
docker: command not found
docker compose: command not found
```

**Solution:**
- **Windows:** Install [Docker Desktop](https://docs.docker.com/desktop/install/windows-install/)
- **Mac:** Install [Docker Desktop](https://docs.docker.com/desktop/install/mac-install/)
- **Linux:**
  ```bash
  # Install Docker
  curl -fsSL https://get.docker.com -o get-docker.sh
  sudo sh get-docker.sh

  # Install Docker Compose
  sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
  sudo chmod +x /usr/local/bin/docker-compose
  ```

### 2. Docker Daemon Not Running

**Error:**
```
Cannot connect to the Docker daemon
Is the docker daemon running?
```

**Solution:**
- **Windows/Mac:** Start Docker Desktop
- **Linux:**
  ```bash
  sudo systemctl start docker
  sudo systemctl enable docker
  ```

### 3. Port Already in Use

**Error:**
```
Bind for 0.0.0.0:80 failed: port is already allocated
Bind for 0.0.0.0:5000 failed: port is already allocated
```

**Solution:**

**Option A - Stop conflicting service:**
```bash
# Find what's using the port
sudo lsof -i :80
sudo lsof -i :5000

# Stop the service
sudo systemctl stop apache2  # or nginx, or whatever is using port 80
```

**Option B - Change ports in docker-compose.yml:**
```yaml
services:
  backend:
    ports:
      - "5001:5000"  # Use port 5001 instead of 5000

  frontend:
    ports:
      - "8080:80"    # Use port 8080 instead of 80
```

### 4. Build Failures

**Error:**
```
ERROR [build stage] failed to solve
npm install failed
pip install failed
```

**Solutions:**

**Check Docker disk space:**
```bash
docker system df
docker system prune -a  # Clean up unused images/containers
```

**Rebuild from scratch:**
```bash
docker compose down -v
docker compose build --no-cache
docker compose up -d
```

**Check network connectivity:**
```bash
# Test if you can reach package repositories
ping npmjs.org
ping pypi.org
```

### 5. Permission Denied Errors

**Error:**
```
Permission denied while trying to connect to Docker daemon
```

**Solution (Linux):**
```bash
# Add your user to docker group
sudo usermod -aG docker $USER

# Log out and back in, or run:
newgrp docker

# Test
docker ps
```

### 6. Healthcheck Failures

**Error:**
```
Unhealthy
healthcheck failed
```

**Solution:**

**Use the simple version without healthchecks:**
```bash
docker compose -f docker-compose.simple.yml up -d
```

**Or manually check services:**
```bash
# Check if backend is responding
curl http://localhost:5000/api/health

# Check if frontend is responding
curl http://localhost/
```

### 7. Backend Build Errors

**Error:**
```
ERROR: Could not build wheels for pikepdf
```

**Solution:**

This usually means missing system dependencies. The Dockerfile should have them, but if it fails:

```bash
# Rebuild backend manually
cd backend
docker build -t pdf-backend .

# If it fails, check the error and update Dockerfile to include missing dependencies
```

### 8. Frontend Build Errors

**Error:**
```
npm ERR! code ELIFECYCLE
npm ERR! errno 1
Module not found
```

**Solutions:**

**Check package.json exists:**
```bash
ls -la frontend/package.json
```

**Verify all frontend files are present:**
```bash
ls -la frontend/src/
# Should see: App.jsx, App.css, main.jsx, index.css
```

**Rebuild manually:**
```bash
cd frontend
npm install
npm run build
```

### 9. Volume Permission Issues

**Error:**
```
Permission denied: '/tmp/pdf_uploads'
```

**Solution:**

**On Linux, fix volume permissions:**
```bash
# Find the volume location
docker volume inspect pdfFDAValidator_pdf_uploads

# Fix permissions (adjust path based on above output)
sudo chmod -R 777 /var/lib/docker/volumes/pdfFDAValidator_pdf_uploads
```

**Or recreate volumes:**
```bash
docker compose down -v
docker compose up -d
```

### 10. Network Issues

**Error:**
```
network pdf-processor-network declared as external, but could not be found
backend: connection refused
```

**Solution:**

**Recreate network:**
```bash
docker network rm pdf-processor-network
docker compose up -d
```

**Check network connectivity:**
```bash
docker network ls
docker network inspect pdf-processor-network
```

## Diagnostic Commands

### Check Status
```bash
# View running containers
docker compose ps

# View all containers (including stopped)
docker ps -a

# View logs
docker compose logs
docker compose logs backend
docker compose logs frontend

# Follow logs in real-time
docker compose logs -f
```

### Test Services

```bash
# Test backend health
curl http://localhost:5000/api/health

# Test frontend
curl http://localhost/

# Get session info (creates a session)
curl -c cookies.txt -b cookies.txt http://localhost:5000/api/session
```

### Resource Usage

```bash
# Check container resource usage
docker stats

# Check disk usage
docker system df

# Check specific container
docker logs pdf-processor-backend
docker logs pdf-processor-frontend
```

## Step-by-Step Troubleshooting

### Complete Reset

If nothing works, try a complete reset:

```bash
# Stop all containers
docker compose down

# Remove all volumes (WARNING: deletes all data)
docker compose down -v

# Remove all images
docker compose down --rmi all

# Clean Docker system
docker system prune -a --volumes

# Rebuild and start fresh
docker compose build --no-cache
docker compose up -d
```

### Manual Testing

Test each component separately:

**1. Test Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Visit: http://localhost:5000/api/health

**2. Test Frontend:**
```bash
cd frontend
npm install
npm run dev
```

Visit: http://localhost:3000

## Alternative Deployment Methods

### Method 1: Use Simple Docker Compose (No Healthchecks)

```bash
docker compose -f docker-compose.simple.yml up -d
```

### Method 2: Run Without Docker

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
export FLASK_ENV=development
python app.py
```

**Frontend (separate terminal):**
```bash
cd frontend
npm install
npm run dev
```

### Method 3: Build Images Separately

```bash
# Build backend
cd backend
docker build -t pdf-backend .

# Build frontend
cd frontend
docker build -t pdf-frontend .

# Run containers manually
docker network create pdf-processor-network

docker run -d \
  --name pdf-processor-backend \
  --network pdf-processor-network \
  -p 5000:5000 \
  -v pdf_uploads:/tmp/pdf_uploads \
  -v pdf_processed:/tmp/pdf_processed \
  pdf-backend

docker run -d \
  --name pdf-processor-frontend \
  --network pdf-processor-network \
  -p 80:80 \
  pdf-frontend
```

## Getting Help

### Collect Information

When asking for help, provide:

1. **Error message:**
```bash
docker compose logs > error.log
```

2. **System information:**
```bash
docker --version
docker compose --version
uname -a  # Linux/Mac
systeminfo  # Windows
```

3. **Container status:**
```bash
docker compose ps
docker ps -a
```

4. **Resource usage:**
```bash
docker stats --no-stream
docker system df
```

### Common Error Messages and Quick Fixes

| Error | Quick Fix |
|-------|-----------|
| "port is already allocated" | Change ports or stop conflicting service |
| "command not found" | Install Docker/Docker Compose |
| "permission denied" | Add user to docker group (Linux) |
| "no space left on device" | Run `docker system prune -a` |
| "network not found" | Run `docker compose down && docker compose up -d` |
| "build failed" | Run `docker compose build --no-cache` |
| "cannot connect to daemon" | Start Docker service/Desktop |
| "unhealthy" | Use docker-compose.simple.yml |

## Contact

If you continue to experience issues, please provide:
- Full error message
- Output of `docker compose logs`
- Your operating system and Docker version
- What you were trying to do when the error occurred
