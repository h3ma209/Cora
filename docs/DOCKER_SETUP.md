# 🐳 Docker Setup & Troubleshooting

## ❌ Error: "Cannot connect to the Docker daemon"

This means Docker Desktop is not running on your Mac.

## ✅ Solution

### Step 1: Start Docker Desktop

1. **Open Docker Desktop**:
   - Find "Docker" in your Applications folder
   - Or use Spotlight: Press `Cmd + Space`, type "Docker"
   - Click to open

2. **Wait for Docker to Start**:
   - Look for the whale icon in your menu bar (top right)
   - Wait until it's steady (not animated)
   - You'll see "Docker Desktop is running" when ready
   - This can take 30-60 seconds

3. **Verify Docker is Running**:

   ```bash
   docker ps
   ```

   Should show: `CONTAINER ID   IMAGE   ...` (even if empty)

   If you see an error, Docker is not ready yet.

### Step 2: Run Makefile Commands

Once Docker is running:

```bash
# Full setup
make dev
```

Or step by step:

```bash
# Build images
make build

# Start services
make up

# Index knowledge base
make index

# Check health
make health
```

## 🔍 Checking Docker Status

### Is Docker Running?

```bash
docker info
```

**Success**: Shows Docker version and system info  
**Failure**: "Cannot connect to the Docker daemon"

### Quick Test

```bash
docker ps
```

**Success**: Shows container list (may be empty)  
**Failure**: Connection error

## 🚀 Quick Start After Docker is Running

```bash
# Option 1: All-in-one command
make dev

# Option 2: Step by step
make build    # Build images
make up       # Start services
make index    # Index knowledge base
make health   # Check health
```

## 🐛 Common Issues

### Issue 1: Docker Desktop Won't Start

**Symptoms**: Docker Desktop crashes or won't open

**Solutions**:

1. Restart your Mac
2. Reinstall Docker Desktop
3. Check system requirements (macOS 10.15+)

### Issue 2: "docker: command not found"

**Symptoms**: Terminal doesn't recognize `docker` command

**Solutions**:

1. Install Docker Desktop from <https://www.docker.com/products/docker-desktop>
2. Restart terminal after installation
3. Check PATH: `echo $PATH` should include `/usr/local/bin`

### Issue 3: Permission Denied

**Symptoms**: "permission denied while trying to connect"

**Solutions**:

1. Don't use `sudo` with Docker commands
2. Make sure Docker Desktop is running
3. Add your user to docker group (usually not needed on Mac)

### Issue 4: Port Already in Use

**Symptoms**: "port is already allocated"

**Solutions**:

```bash
# Check what's using port 8001
lsof -ti:8001

# Kill the process
lsof -ti:8001 | xargs kill -9

# Or stop your local server first
pkill -f "python3 server.py"

# Then start Docker
make up
```

### Issue 5: Build Fails

**Symptoms**: Error during `make build`

**Solutions**:

```bash
# Clean everything
make clean

# Remove old images
docker system prune -a

# Try again
make build
```

## 📋 Pre-Flight Checklist

Before running `make dev`:

- [ ] Docker Desktop is installed
- [ ] Docker Desktop is running (whale icon in menu bar)
- [ ] `docker ps` command works
- [ ] No local server running on port 8001
- [ ] No local Ollama running on port 11434

## 🎯 Complete Workflow

### First Time Ever

1. **Install Docker Desktop**:
   - Download from <https://www.docker.com/products/docker-desktop>
   - Install and open
   - Wait for it to start

2. **Verify Installation**:

   ```bash
   docker --version
   docker ps
   ```

3. **Run Setup**:

   ```bash
   cd /Users/hema/Desktop/Drift/Cora
   make dev
   ```

4. **Wait for Completion** (5-10 minutes first time):
   - Downloads images
   - Builds containers
   - Indexes knowledge base

5. **Test**:

   ```bash
   make health
   make quick-test
   ```

### Daily Use

1. **Start Docker Desktop** (if not running)

2. **Start Services**:

   ```bash
   make up
   ```

3. **Check Status**:

   ```bash
   make health
   ```

4. **View Logs**:

   ```bash
   make logs
   ```

5. **When Done**:

   ```bash
   make down
   ```

## 💡 Pro Tips

### Tip 1: Auto-Start Docker

Set Docker Desktop to start automatically:

- Open Docker Desktop
- Settings → General
- Check "Start Docker Desktop when you log in"

### Tip 2: Check Before Commands

```bash
# Quick check if Docker is ready
docker ps && echo "✓ Docker is ready" || echo "✗ Start Docker Desktop first"
```

### Tip 3: Monitor Resources

Docker Desktop → Dashboard → Resources

- Shows CPU, memory usage
- Can adjust limits if needed

### Tip 4: Clean Up Regularly

```bash
# Remove unused resources
make prune

# Or full cleanup
docker system prune -a --volumes
```

## 🆘 Still Having Issues?

### Check Docker Desktop Logs

Docker Desktop → Troubleshoot → View Logs

### Reset Docker Desktop

Docker Desktop → Troubleshoot → Reset to factory defaults

### Reinstall Docker Desktop

1. Quit Docker Desktop
2. Remove from Applications
3. Download fresh copy
4. Install and restart

## ✅ Success Indicators

You'll know everything is working when:

1. **Docker Desktop shows**:
   - Green "running" status
   - Containers listed in dashboard

2. **Terminal shows**:

   ```bash
   $ docker ps
   CONTAINER ID   IMAGE                    STATUS
   abc123         cora-api                 Up 2 minutes
   def456         ollama/ollama:latest     Up 2 minutes
   ```

3. **Health check passes**:

   ```bash
   $ make health
   ✓ Cora API: {"status": "healthy"}
   ✓ Ollama: {...}
   ```

4. **Endpoints work**:

   ```bash
   $ curl http://localhost:8001/health
   {"status":"healthy","version":"2.0.0"}
   ```

## 📚 Resources

- **Docker Desktop**: <https://www.docker.com/products/docker-desktop>
- **Docker Docs**: <https://docs.docker.com/desktop/mac/>
- **Makefile Guide**: `docs/MAKEFILE_GUIDE.md`
- **Project README**: `README.md`

---

## 🚀 TL;DR

1. **Start Docker Desktop** (whale icon in menu bar)
2. **Wait for it to be ready** (30-60 seconds)
3. **Run**: `make dev`
4. **Check**: `make health`

That's it! 🎉
