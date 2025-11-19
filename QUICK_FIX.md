# Quick Fix for Build Errors

## Your Error
```
ERROR [backend 3/7] RUN apt-get update && apt-get install...
```

## Fastest Solutions (Try in Order)

### 1. Retry the Build (30 seconds)
Sometimes it's just a temporary network issue:

```bash
docker compose down
docker compose build --no-cache
docker compose up -d
```

### 2. Use Simple Version Without Healthchecks (1 minute)
```bash
docker compose -f docker-compose.simple.yml build --no-cache
docker compose -f docker-compose.simple.yml up -d
```

### 3. Configure DNS (2 minutes)

**Linux/Mac:**
```bash
sudo nano /etc/docker/daemon.json
```

Add:
```json
{
  "dns": ["8.8.8.8", "8.8.4.4"]
}
```

Save and restart Docker:
```bash
sudo systemctl restart docker
```

**Windows:**
1. Open Docker Desktop
2. Settings → Docker Engine
3. Add: `"dns": ["8.8.8.8", "8.8.4.4"]`
4. Apply & Restart

Then rebuild:
```bash
docker compose build --no-cache
docker compose up -d
```

### 4. Run Without Docker (5 minutes)

**Backend:**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install system dependencies first
# Ubuntu/Debian:
sudo apt-get update
sudo apt-get install libqpdf-dev

# Then install Python packages
pip install -r requirements.txt
python app.py
```

**Frontend (new terminal):**
```bash
cd frontend
npm install
npm run dev
```

Access at:
- Frontend: http://localhost:3000
- Backend: http://localhost:5000

## Still Not Working?

See detailed troubleshooting:
- [BUILD_TROUBLESHOOTING.md](BUILD_TROUBLESHOOTING.md) - Comprehensive build fixes
- [DOCKER_TROUBLESHOOTING.md](DOCKER_TROUBLESHOOTING.md) - Docker runtime issues
- [QUICK_START.md](QUICK_START.md) - General setup guide

## Common Causes

1. **Network/DNS issues** - Can't reach Debian package repositories
2. **Firewall/Proxy** - Corporate network blocking Docker
3. **Temporary repository outage** - Try again in a few minutes
4. **Docker cache corruption** - Use `--no-cache` flag

## Need More Help?

Collect this information:
```bash
# Save build output
docker compose build --progress=plain --no-cache 2>&1 | tee build-error.log

# Check network
ping deb.debian.org

# Check Docker
docker --version
docker info
```

Then share the build-error.log when asking for help.
