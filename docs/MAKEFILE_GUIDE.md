# Makefile Usage Guide

## 🎯 Overview

The Makefile provides convenient commands for managing your Cora AI Docker deployment.

## 📋 Quick Reference

### View All Commands

```bash
make help
```

## 🚀 Common Workflows

### 1. **First Time Setup**

```bash
make dev
```

This will:

- Build Docker images
- Start all services
- Index the knowledge base
- Set up everything for development

### 2. **Daily Development**

```bash
# Start services
make up

# View logs
make logs

# Check status
make health

# Stop services
make down
```

### 3. **After Code Changes**

```bash
make rebuild
```

This rebuilds images and restarts services.

### 4. **Testing**

```bash
# Quick endpoint test
make quick-test

# Full RAG test
make test

# Q&A test
make test-qa
```

## 📚 All Commands

### **General**

| Command | Description |
|---------|-------------|
| `make help` | Display help message with all commands |
| `make info` | Show project information and URLs |
| `make ports` | Show port mappings |

### **Docker Operations**

| Command | Description |
|---------|-------------|
| `make build` | Build Docker images from scratch |
| `make up` | Start all services in background |
| `make down` | Stop and remove containers |
| `make restart` | Restart all services |
| `make stop` | Stop services (keep containers) |
| `make start` | Start existing containers |

### **Monitoring & Logs**

| Command | Description |
|---------|-------------|
| `make logs` | View logs from all services (follow mode) |
| `make logs-api` | View Cora API logs only |
| `make logs-ollama` | View Ollama logs only |
| `make status` | Show status of all services |
| `make health` | Check health of all services |

### **Development**

| Command | Description |
|---------|-------------|
| `make shell` | Open bash shell in Cora API container |
| `make shell-ollama` | Open bash shell in Ollama container |
| `make index` | Index/reindex knowledge base |
| `make test` | Run RAG tests |
| `make test-qa` | Run Q&A tests |

### **Database & Data**

| Command | Description |
|---------|-------------|
| `make db-stats` | Show vector database statistics |
| `make db-reset` | Reset and reindex database (with confirmation) |
| `make backup-data` | Backup vector database to ./backups/ |

### **Cleanup**

| Command | Description |
|---------|-------------|
| `make clean` | Remove containers and networks (keep data) |
| `make clean-all` | Remove everything including volumes (with confirmation) |
| `make prune` | Remove unused Docker resources |

### **Quick Commands**

| Command | Description |
|---------|-------------|
| `make dev` | Full setup: build + start + index |
| `make rebuild` | Rebuild and restart everything |
| `make quick-test` | Quick test of both endpoints |

### **Model Management**

| Command | Description |
|---------|-------------|
| `make pull-model` | Pull Ollama model (qwen2.5:1.5b) |
| `make list-models` | List available Ollama models |

## 🎓 Usage Examples

### Example 1: Fresh Start

```bash
# First time setup
make dev

# Check if everything is running
make health

# View logs
make logs
```

### Example 2: Add New Articles

```bash
# Add articles to data/jsons/articles.json

# Reindex
make index

# Test
make quick-test
```

### Example 3: Debugging

```bash
# View API logs
make logs-api

# Open shell in container
make shell

# Inside container:
python3 indexer.py --stats
exit

# Check health
make health
```

### Example 4: Update Code

```bash
# After changing code in src/

# Rebuild and restart
make rebuild

# Test changes
make quick-test
```

### Example 5: Backup Before Reset

```bash
# Backup current data
make backup-data

# Reset database
make db-reset

# Reindex
make index
```

### Example 6: Complete Cleanup

```bash
# Stop everything
make down

# Remove all data (careful!)
make clean-all

# Fresh start
make dev
```

## 🔧 Advanced Usage

### Run Custom Commands in Container

```bash
# Open shell
make shell

# Inside container, run any command:
python3 -c "from src.rag.vector_store import get_vector_store; print(get_vector_store().collection.count())"
```

### Check Specific Service

```bash
# API logs only
make logs-api

# Ollama logs only
make logs-ollama
```

### Manual Index with Options

```bash
make shell
python3 indexer.py --reset  # Reset and reindex
python3 indexer.py --stats  # Show stats only
exit
```

## 📊 Monitoring

### Check Everything is Working

```bash
# Quick health check
make health

# Detailed status
make status

# Test endpoints
make quick-test
```

### View Real-time Logs

```bash
# All services
make logs

# Just API (useful for debugging)
make logs-api
```

## 🎯 Common Scenarios

### Scenario 1: "Server won't start"

```bash
# Check status
make status

# View logs for errors
make logs-api

# Try rebuilding
make rebuild
```

### Scenario 2: "No documents retrieved"

```bash
# Check if database is indexed
make db-stats

# If empty, reindex
make index

# Test again
make quick-test
```

### Scenario 3: "Out of disk space"

```bash
# Clean up unused resources
make prune

# If needed, remove old data
make clean-all
make dev
```

### Scenario 4: "Want to start fresh"

```bash
# Backup first (optional)
make backup-data

# Complete cleanup
make clean-all

# Fresh setup
make dev
```

## 🚨 Important Notes

### Destructive Commands

These commands will **delete data** and ask for confirmation:

- `make db-reset` - Deletes vector database
- `make clean-all` - Deletes all volumes

### Safe Commands

These are always safe to run:

- `make help`
- `make status`
- `make health`
- `make logs`
- `make info`

### Background Services

These commands run services in background:

- `make up`
- `make start`
- `make dev`

Use `make logs` to view output.

## 📝 Tips

1. **Always check health after starting:**

   ```bash
   make up && sleep 5 && make health
   ```

2. **View logs while developing:**

   ```bash
   make logs-api
   ```

3. **Quick iteration cycle:**

   ```bash
   # Edit code
   make rebuild
   make quick-test
   ```

4. **Backup before major changes:**

   ```bash
   make backup-data
   make db-reset
   ```

5. **Check what's using space:**

   ```bash
   docker system df
   make prune  # Clean up
   ```

## 🎉 Summary

**Most Used Commands:**

```bash
make dev         # First time setup
make up          # Start services
make down        # Stop services
make logs        # View logs
make health      # Check status
make index       # Reindex knowledge
make quick-test  # Test endpoints
make rebuild     # After code changes
```

**For help anytime:**

```bash
make help
```

Happy coding! 🚀
