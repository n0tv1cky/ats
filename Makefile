.PHONY: help install dev up down build test clean migrate seed

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install dependencies
	cd services/backend && pip install -r requirements.txt
	cd services/frontend && npm install

dev: ## Start development environment
	docker-compose -f docker-compose.dev.yaml up --build

up: ## Start production environment
	docker-compose -f docker-compose.prod.yaml up -d

down: ## Stop all containers
	docker-compose -f docker-compose.dev.yaml down
	docker-compose -f docker-compose.prod.yaml down

build: ## Build all Docker images
	docker-compose -f docker-compose.prod.yaml build

test: ## Run tests
	cd services/backend && pytest tests/
	cd services/frontend && npm test

clean: ## Clean up containers and volumes
	docker-compose -f docker-compose.dev.yaml down -v
	docker-compose -f docker-compose.prod.yaml down -v

migrate: ## Run database migrations
	cd services/backend && alembic upgrade head

migrate-create: ## Create a new migration
	cd services/backend && alembic revision --autogenerate -m "$(message)"

seed: ## Seed initial data
	cd services/backend && python scripts/seed_data.py

logs: ## View logs
	docker-compose -f docker-compose.dev.yaml logs -f

logs-backend: ## View backend logs
	docker-compose -f docker-compose.dev.yaml logs -f backend

logs-frontend: ## View frontend logs
	docker-compose -f docker-compose.dev.yaml logs -f frontend

