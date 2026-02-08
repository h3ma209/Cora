.PHONY: help build up down restart logs shell index test clean prune status health

# Default target
.DEFAULT_GOAL := help

# Colors for output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m # No Color

##@ General

help: ## Display this help message
	@echo "$(BLUE)Cora AI - Docker Management$(NC)"
	@echo ""
	@awk 'BEGIN {FS = ":.*##"; printf "Usage:\n  make $(GREEN)<target>$(NC)\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  $(GREEN)%-15s$(NC) %s\n", $$1, $$2 } /^##@/ { printf "\n$(YELLOW)%s$(NC)\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

##@ Docker Operations

build: ## Build Docker images
	@echo "$(BLUE)Building Docker images...$(NC)"
	docker-compose build --no-cache
	@echo "$(GREEN)✓ Build complete$(NC)"
build-cached: ## Build Docker images
	@echo "$(BLUE)Building Docker images...$(NC)"
	docker-compose build
	@echo "$(GREEN)✓ Build complete$(NC)"
up: ## Start all services
	@echo "$(BLUE)Starting services...$(NC)"
	docker-compose up -d
	@echo "$(GREEN)✓ Services started$(NC)"
	@echo "$(YELLOW)Run 'make logs' to view logs$(NC)"
	@echo "$(YELLOW)Run 'make health' to check status$(NC)"

down: ## Stop all services
	@echo "$(BLUE)Stopping services...$(NC)"
	docker-compose down
	@echo "$(GREEN)✓ Services stopped$(NC)"

restart: ## Restart all services
	@echo "$(BLUE)Restarting services...$(NC)"
	docker-compose restart
	@echo "$(GREEN)✓ Services restarted$(NC)"

stop: ## Stop services without removing containers
	@echo "$(BLUE)Stopping services...$(NC)"
	docker-compose stop
	@echo "$(GREEN)✓ Services stopped$(NC)"

start: ## Start existing containers
	@echo "$(BLUE)Starting existing containers...$(NC)"
	docker-compose start
	@echo "$(GREEN)✓ Services started$(NC)"

##@ Monitoring & Logs

logs: ## View logs from all services
	docker-compose logs -f

logs-api: ## View logs from Cora API only
	docker-compose logs -f cora-api

logs-ollama: ## View logs from Ollama only
	docker-compose logs -f ollama

status: ## Show status of all services
	@echo "$(BLUE)Service Status:$(NC)"
	@docker-compose ps

health: ## Check health of services
	@echo "$(BLUE)Checking service health...$(NC)"
	@echo ""
	@echo "$(YELLOW)Cora API:$(NC)"
	@curl -s http://localhost:8001/health | python3 -m json.tool || echo "$(RED)✗ API not responding$(NC)"
	@echo ""
	@echo "$(YELLOW)Ollama:$(NC)"
	@curl -s http://localhost:11434/api/tags || echo "$(RED)✗ Ollama not responding$(NC)"

##@ Development

shell: ## Open shell in Cora API container
	@echo "$(BLUE)Opening shell in cora-api container...$(NC)"
	docker-compose exec cora-api /bin/bash

shell-ollama: ## Open shell in Ollama container
	@echo "$(BLUE)Opening shell in ollama container...$(NC)"
	docker-compose exec ollama /bin/bash

index: ## Index knowledge base in container
	@echo "$(BLUE)Indexing knowledge base...$(NC)"
	docker-compose exec cora-api python3 indexer.py
	@echo "$(GREEN)✓ Indexing complete$(NC)"

test: ## Run tests in container
	@echo "$(BLUE)Running tests...$(NC)"
	docker-compose exec cora-api python3 test_rag.py

test-qa: ## Run Q&A tests in container
	@echo "$(BLUE)Running Q&A tests...$(NC)"
	docker-compose exec cora-api python3 tests/test_qa.py

##@ Database & Data

db-stats: ## Show vector database statistics
	@echo "$(BLUE)Vector Database Statistics:$(NC)"
	docker-compose exec cora-api python3 indexer.py --stats

db-reset: ## Reset and reindex vector database
	@echo "$(RED)WARNING: This will delete all indexed data!$(NC)"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		echo "$(BLUE)Resetting database...$(NC)"; \
		docker-compose exec cora-api python3 indexer.py --reset; \
		echo "$(GREEN)✓ Database reset complete$(NC)"; \
	else \
		echo "$(YELLOW)Cancelled$(NC)"; \
	fi

backup-data: ## Backup vector database
	@echo "$(BLUE)Backing up vector database...$(NC)"
	@mkdir -p backups
	@docker cp $$(docker-compose ps -q cora-api):/app/chroma_db ./backups/chroma_db_$$(date +%Y%m%d_%H%M%S)
	@echo "$(GREEN)✓ Backup complete$(NC)"

##@ Cleanup

clean: ## Remove containers and networks (keeps volumes)
	@echo "$(BLUE)Cleaning up containers and networks...$(NC)"
	docker-compose down
	@echo "$(GREEN)✓ Cleanup complete$(NC)"

clean-all: ## Remove everything including volumes
	@echo "$(RED)WARNING: This will delete all data!$(NC)"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		echo "$(BLUE)Removing all containers, networks, and volumes...$(NC)"; \
		docker-compose down -v; \
		echo "$(GREEN)✓ Complete cleanup done$(NC)"; \
	else \
		echo "$(YELLOW)Cancelled$(NC)"; \
	fi

prune: ## Remove unused Docker resources
	@echo "$(BLUE)Pruning unused Docker resources...$(NC)"
	docker system prune -f
	@echo "$(GREEN)✓ Prune complete$(NC)"

##@ Quick Commands

dev: build up index ## Build, start, and index (full setup)
	@echo "$(GREEN)✓ Development environment ready!$(NC)"
	@echo "$(YELLOW)API: http://localhost:8001$(NC)"
	@echo "$(YELLOW)Docs: http://localhost:8001/docs$(NC)"

rebuild: down build up ## Rebuild and restart everything
	@echo "$(GREEN)✓ Rebuild complete$(NC)"

quick-test: ## Quick test of both endpoints
	@echo "$(BLUE)Testing endpoints...$(NC)"
	@echo ""
	@echo "$(YELLOW)1. Health Check:$(NC)"
	@curl -s http://localhost:8001/health | python3 -m json.tool
	@echo ""
	@echo "$(YELLOW)2. Classification Test:$(NC)"
	@curl -s -X POST http://localhost:8001/classify \
		-H 'Content-Type: application/json' \
		-d '{"text": "my internet is slow"}' | python3 -m json.tool | head -20
	@echo ""
	@echo "$(YELLOW)3. Q&A Test:$(NC)"
	@curl -s -X POST http://localhost:8001/ask \
		-H 'Content-Type: application/json' \
		-d '{"question": "How do I reset my password?"}' | python3 -m json.tool | head -20

##@ Model Management

pull-model: ## Pull Ollama model
	@echo "$(BLUE)Pulling Ollama model...$(NC)"
	docker-compose exec ollama ollama pull qwen2.5:1.5b
	@echo "$(GREEN)✓ Model pulled$(NC)"

list-models: ## List available Ollama models
	@echo "$(BLUE)Available models:$(NC)"
	docker-compose exec ollama ollama list

##@ Information

info: ## Show project information
	@echo "$(BLUE)Cora AI - Project Information$(NC)"
	@echo ""
	@echo "$(YELLOW)Services:$(NC)"
	@echo "  • Cora API:    http://localhost:8001"
	@echo "  • API Docs:    http://localhost:8001/docs"
	@echo "  • Ollama:      http://localhost:11434"
	@echo ""
	@echo "$(YELLOW)Endpoints:$(NC)"
	@echo "  • POST /classify - Classify support text"
	@echo "  • POST /ask      - Answer questions"
	@echo "  • GET  /health   - Health check"
	@echo ""
	@echo "$(YELLOW)Volumes:$(NC)"
	@echo "  • ollama_data  - Ollama models"
	@echo "  • chroma_data  - Vector database"
	@echo ""
	@echo "$(YELLOW)Quick Start:$(NC)"
	@echo "  make dev       - Full setup"
	@echo "  make logs      - View logs"
	@echo "  make health    - Check status"

ports: ## Show port mappings
	@echo "$(BLUE)Port Mappings:$(NC)"
	@echo "  8001  → Cora API"
	@echo "  11434 → Ollama"
