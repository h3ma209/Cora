# Makefile Quick Reference Card

## 🚀 Most Common Commands

```bash
# View all commands
make help

# First time setup (build + start + index)
make dev

# Start services
make up

# Stop services
make down

# View logs
make logs

# Check health
make health

# Test endpoints
make quick-test

# Rebuild after code changes
make rebuild

# Index knowledge base
make index
```

## 📊 Command Categories

### **Setup & Start**

- `make dev` - Complete setup (first time)
- `make up` - Start services
- `make build` - Build images

### **Monitor**

- `make logs` - View all logs
- `make health` - Check health
- `make status` - Service status

### **Test**

- `make quick-test` - Test endpoints
- `make test` - Run RAG tests
- `make test-qa` - Run Q&A tests

### **Manage**

- `make index` - Reindex knowledge
- `make shell` - Open container shell
- `make restart` - Restart services

### **Stop & Clean**

- `make down` - Stop services
- `make clean` - Remove containers
- `make prune` - Clean Docker

## 🎯 Common Workflows

### First Time

```bash
make dev
make health
```

### Daily Use

```bash
make up
make logs-api  # In another terminal
```

### After Changes

```bash
make rebuild
make quick-test
```

### Add Articles

```bash
# Edit data/jsons/articles.json
make index
make quick-test
```

### Debugging

```bash
make logs-api
make shell
make health
```

## 📝 URLs

- **API**: <http://localhost:8001>
- **Docs**: <http://localhost:8001/docs>
- **Ollama**: <http://localhost:11434>

## 💡 Tips

- Run `make help` anytime for full list
- Use `make info` for project details
- Commands with colors work best in terminal
- Destructive commands ask for confirmation

## ⚡ One-Liners

```bash
# Full restart
make down && make up

# Fresh start
make clean-all && make dev

# Quick check
make health && make quick-test

# View API logs only
make logs-api

# Backup then reset
make backup-data && make db-reset
```
