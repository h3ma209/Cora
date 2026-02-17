.PHONY: help build up down restart logs shell index test test-api clean setup

.DEFAULT_GOAL := help

# Colors
BLUE := \033[36m
NC := \033[0m

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "$(BLUE)%-15s$(NC) %s\n", $$1, $$2}'

build: ## Build docker images
	docker-compose build

up: ## Start services
	docker-compose up -d

down: ## Stop services
	docker-compose down

restart: ## Restart services
	docker-compose restart

logs: ## View logs
	docker-compose logs -f

shell: ## Open shell in API container
	docker-compose exec drift-cora-api /bin/bash

index: ## Index knowledge base
	docker-compose exec drift-cora-api python3 -m src.rag.indexer

test: ## Run tests
	@echo "$(BLUE)Running RAG tests...$(NC)"
	docker-compose exec drift-cora-api python3 tests/test_rag.py
	@echo "$(BLUE)Running Q&A tests...$(NC)"
	docker-compose exec drift-cora-api python3 tests/test_qa.py

test-api: ## Test API endpoints with curl
	@echo "$(BLUE)Testing Health...$(NC)"
	@curl -s http://localhost:8001/health | python3 -m json.tool
	@echo "$(BLUE)Testing Q&A...$(NC)"
	@curl -s -X POST http://localhost:8001/ask \
		-H 'Content-Type: application/json' \
		-d '{"question": "How do I reset my password?"}' | python3 -m json.tool

clean: ## Remove containers and volumes
	@read -p "Are you sure? This will delete data! [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		docker-compose down -v; \
		docker system prune -f; \
	fi

setup: build up index ## Full setup (build, up, index)
