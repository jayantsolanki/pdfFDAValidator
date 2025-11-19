# Quick Start Guide

## Using Docker Compose V2 (Recommended)

Most modern Docker installations include Docker Compose V2 as a plugin.

### Check Your Version
```bash
# Docker Compose V2 (plugin)
docker compose version

# Docker Compose V1 (standalone - deprecated)
docker-compose version
```

## Running the Application

The startup scripts automatically detect which version you have installed.

### Option 1: Use Startup Scripts (Easiest)

**Linux/macOS:**
```bash
./start.sh
```

**Windows:**
```bash
start.bat
```

### Option 2: Manual Commands

**Using Docker Compose V2 (recommended):**
```bash
# Start application
docker compose up -d

# View logs
docker compose logs -f

# Stop application
docker compose down

# Stop and remove data
docker compose down -v

# Rebuild containers
docker compose build --no-cache
docker compose up -d
```

**Using Docker Compose V1 (older systems):**
```bash
# Start application
docker-compose up -d

# View logs
docker-compose logs -f

# Stop application
docker-compose down

# Stop and remove data
docker-compose down -v

# Rebuild containers
docker-compose build --no-cache
docker-compose up -d
```

### Option 3: Use Simple Version (Without Healthchecks)

If you encounter healthcheck issues:

```bash
# V2
docker compose -f docker-compose.simple.yml up -d

# V1
docker-compose -f docker-compose.simple.yml up -d
```

## First Time Setup

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd pdfFDAValidator
   ```

2. **(Optional) Create .env file:**
   ```bash
   cp .env.example .env
   # Edit .env and set SECRET_KEY for production
   ```

3. **Start the application:**
   ```bash
   ./start.sh  # or start.bat on Windows
   # or
   docker compose up -d
   ```

4. **Access the application:**
   - Frontend: http://localhost
   - Backend API: http://localhost:5000

## Common Commands

### View Container Status
```bash
docker compose ps
docker ps -a
```

### View Logs
```bash
# All services
docker compose logs

# Specific service
docker compose logs backend
docker compose logs frontend

# Follow logs in real-time
docker compose logs -f
```

### Restart Services
```bash
# Restart all
docker compose restart

# Restart specific service
docker compose restart backend
```

### Update After Code Changes
```bash
docker compose down
docker compose build
docker compose up -d
```

### Clean Up
```bash
# Stop containers
docker compose down

# Stop and remove volumes (deletes data)
docker compose down -v

# Clean up unused Docker resources
docker system prune -a
```

## Troubleshooting

### Port Already in Use

**Change ports in docker-compose.yml:**
```yaml
services:
  backend:
    ports:
      - "5001:5000"  # Changed from 5000:5000

  frontend:
    ports:
      - "8080:80"    # Changed from 80:80
```

Then access:
- Frontend: http://localhost:8080
- Backend: http://localhost:5001

### Docker Compose Not Found

**Install Docker Compose V2:**
```bash
# Usually comes with Docker Desktop
# For Linux servers:
sudo apt-get update
sudo apt-get install docker-compose-plugin
```

### Containers Won't Start

```bash
# Check logs for errors
docker compose logs

# Rebuild from scratch
docker compose down -v
docker compose build --no-cache
docker compose up -d
```

## Without Docker

If you prefer not to use Docker:

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

**Frontend (separate terminal):**
```bash
cd frontend
npm install
npm run dev
```

Access at http://localhost:3000

## Need Help?

See the detailed troubleshooting guide:
- [DOCKER_TROUBLESHOOTING.md](DOCKER_TROUBLESHOOTING.md)
- [WEB_APP_README.md](WEB_APP_README.md)
- [claude.md](claude.md) (Technical documentation)
