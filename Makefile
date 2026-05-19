# ============================================================================
# AgentOrchestra - Makefile
# Project常用命令集合
# ============================================================================

.PHONY: help dev dev-backend dev-frontend build up down restart logs \
        test test-backend test-frontend lint lint-backend lint-frontend \
        typecheck typecheck-backend typecheck-frontend format \
        clean clean-docker clean-all \
        docker-build docker-up docker-down docker-restart docker-logs \
        install install-backend install-frontend \
        pre-commit setup \
        redis-cli redis-flush \
        check

# ---------------------------------------------------------------------------
# Default variables
# ---------------------------------------------------------------------------
DOCKER_COMPOSE = docker compose
DOCKER_COMPOSE_DEV = docker compose -f docker-compose.dev.yml
PYTHON = python3
PNPM = pnpm

# ---------------------------------------------------------------------------
# Colors for output
# ---------------------------------------------------------------------------
BLUE   := \033[0;34m
GREEN  := \033[0;32m
YELLOW := \033[0;33m
RED    := \033[0;31m
NC     := \033[0m

# ---------------------------------------------------------------------------
# Help
# ---------------------------------------------------------------------------
help: ## Show this help message
	@echo ""
	@echo "$(BLUE)AgentOrchestra - Available Commands$(NC)"
	@echo "================================"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-22s$(NC) %s\n", $$1, $$2}'
	@echo ""

# ---------------------------------------------------------------------------
# Setup & Installation
# ---------------------------------------------------------------------------
setup: ## Initial project setup (install dependencies + pre-commit hooks)
	@echo "$(BLUE)Setting up AgentOrchestra...$(NC)"
	$(MAKE) install
	$(MAKE) pre-commit
	@echo "$(GREEN)Setup complete!$(NC)"

install: install-backend install-frontend ## Install all dependencies

install-backend: ## Install backend Python dependencies
	@echo "$(BLUE)Installing backend dependencies...$(NC)"
	cd backend && $(PYTHON) -m pip install --upgrade pip
	cd backend && $(PYTHON) -m pip install -e ".[dev,test]"
	@echo "$(GREEN)Backend dependencies installed$(NC)"

install-frontend: ## Install frontend Node.js dependencies
	@echo "$(BLUE)Installing frontend dependencies...$(NC)"
	cd frontend && corepack enable
	cd frontend && $(PNPM) install
	@echo "$(GREEN)Frontend dependencies installed$(NC)"

pre-commit: ## Install pre-commit hooks
	@echo "$(BLUE)Installing pre-commit hooks...$(NC)"
	pre-commit install
	pre-commit install --hook-type commit-msg
	@echo "$(GREEN)Pre-commit hooks installed$(NC)"

# ---------------------------------------------------------------------------
# Development
# ---------------------------------------------------------------------------
dev: ## Start development environment (docker-compose.dev.yml)
	@echo "$(BLUE)Starting development environment...$(NC)"
	$(DOCKER_COMPOSE_DEV) up --build

dev-backend: ## Start backend only (development)
	@echo "$(BLUE)Starting backend in development mode...$(NC)"
	cd backend && $(PYTHON) -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

dev-frontend: ## Start frontend only (development)
	@echo "$(BLUE)Starting frontend in development mode...$(NC)"
	cd frontend && $(PNPM) dev

# ---------------------------------------------------------------------------
# Docker (Production)
# ---------------------------------------------------------------------------
docker-build: ## Build production Docker images
	@echo "$(BLUE)Building production images...$(NC)"
	$(DOCKER_COMPOSE) build

docker-up: ## Start production environment
	@echo "$(BLUE)Starting production environment...$(NC)"
	$(DOCKER_COMPOSE) up -d

docker-down: ## Stop production environment
	@echo "$(BLUE)Stopping production environment...$(NC)"
	$(DOCKER_COMPOSE) down

docker-restart: ## Restart production environment
	@echo "$(BLUE)Restarting production environment...$(NC)"
	$(DOCKER_COMPOSE) restart

docker-logs: ## Show Docker logs (follow mode)
	$(DOCKER_COMPOSE) logs -f

docker-logs-backend: ## Show backend logs
	$(DOCKER_COMPOSE) logs -f backend

docker-logs-frontend: ## Show frontend logs
	$(DOCKER_COMPOSE) logs -f frontend

docker-logs-redis: ## Show Redis logs
	$(DOCKER_COMPOSE) logs -f redis

# ---------------------------------------------------------------------------
# Docker (Development)
# ---------------------------------------------------------------------------
build: ## Build development Docker images
	@echo "$(BLUE)Building development images...$(NC)"
	$(DOCKER_COMPOSE_DEV) build

up: ## Start development environment (detached)
	@echo "$(BLUE)Starting development environment...$(NC)"
	$(DOCKER_COMPOSE_DEV) up -d

down: ## Stop development environment
	@echo "$(BLUE)Stopping development environment...$(NC)"
	$(DOCKER_COMPOSE_DEV) down

restart: ## Restart development environment
	@echo "$(BLUE)Restarting development environment...$(NC)"
	$(DOCKER_COMPOSE_DEV) restart

logs: ## Show development logs (follow mode)
	$(DOCKER_COMPOSE_DEV) logs -f

# ---------------------------------------------------------------------------
# Testing
# ---------------------------------------------------------------------------
test: test-backend test-frontend ## Run all tests

test-backend: ## Run backend tests
	@echo "$(BLUE)Running backend tests...$(NC)"
	cd backend && $(PYTHON) -m pytest tests/ -v --tb=short --cov=app --cov-report=term-missing

test-backend-verbose: ## Run backend tests (verbose)
	cd backend && $(PYTHON) -m pytest tests/ -vv --tb=long --cov=app --cov-report=html

test-backend-watch: ## Run backend tests in watch mode
	cd backend && $(PYTHON) -m pytest-watch tests/ -- -v --tb=short

test-frontend: ## Run frontend tests
	@echo "$(BLUE)Running frontend tests...$(NC)"
	cd frontend && $(PNPM) test

test-frontend-watch: ## Run frontend tests in watch mode
	cd frontend && $(PNPM) test:watch

test-frontend-coverage: ## Run frontend tests with coverage
	cd frontend && $(PNPM) test:coverage

# ---------------------------------------------------------------------------
# Linting
# ---------------------------------------------------------------------------
lint: lint-backend lint-frontend ## Run all linters

lint-backend: ## Lint backend with ruff
	@echo "$(BLUE)Linting backend...$(NC)"
	cd backend && ruff check . --fix
	cd backend && ruff format --check .

lint-frontend: ## Lint frontend with ESLint
	@echo "$(BLUE)Linting frontend...$(NC)"
	cd frontend && $(PNPM) lint

# ---------------------------------------------------------------------------
# Type Checking
# ---------------------------------------------------------------------------
typecheck: typecheck-backend typecheck-frontend ## Run all type checks

typecheck-backend: ## Type check backend with mypy
	@echo "$(BLUE)Type checking backend...$(NC)"
	cd backend && mypy app/ --ignore-missing-imports

typecheck-frontend: ## Type check frontend with TypeScript
	@echo "$(BLUE)Type checking frontend...$(NC)"
	cd frontend && npx tsc --noEmit

# ---------------------------------------------------------------------------
# Formatting
# ---------------------------------------------------------------------------
format: format-backend format-frontend ## Format all code

format-backend: ## Format backend code with ruff
	@echo "$(BLUE)Formatting backend code...$(NC)"
	cd backend && ruff check --fix .
	cd backend && ruff format .

format-frontend: ## Format frontend code with Prettier
	@echo "$(BLUE)Formatting frontend code...$(NC)"
	cd frontend && $(PNPM) format

# ---------------------------------------------------------------------------
# Redis
# ---------------------------------------------------------------------------
redis-cli: ## Open Redis CLI
	docker exec -it agentorchestra-redis-dev redis-cli

redis-flush: ## Flush Redis database
	docker exec -it agentorchestra-redis-dev redis-cli FLUSHALL
	@echo "$(YELLOW)Redis database flushed$(NC)"

redis-info: ## Show Redis info
	docker exec agentorchestra-redis-dev redis-cli INFO

# ---------------------------------------------------------------------------
# Quality Checks
# ---------------------------------------------------------------------------
check: lint typecheck test ## Run all quality checks (lint + typecheck + test)
	@echo "$(GREEN)All quality checks passed!$(NC)"

# ---------------------------------------------------------------------------
# Cleanup
# ---------------------------------------------------------------------------
clean: ## Clean build artifacts and caches
	@echo "$(BLUE)Cleaning build artifacts...$(NC)"
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .mypy_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .ruff_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .next -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name node_modules -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .venv -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name dist -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name build -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name *.egg-info -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
	find . -name "*.pyo" -delete 2>/dev/null || true
	@echo "$(GREEN)Clean complete$(NC)"

clean-docker: ## Clean Docker resources
	@echo "$(BLUE)Cleaning Docker resources...$(NC)"
	$(DOCKER_COMPOSE_DEV) down -v --remove-orphans 2>/dev/null || true
	$(DOCKER_COMPOSE) down -v --remove-orphans 2>/dev/null || true
	docker system prune -f
	@echo "$(GREEN)Docker cleanup complete$(NC)"

clean-all: clean clean-docker ## Clean everything (artifacts + Docker)
	@echo "$(GREEN)Full cleanup complete$(NC)"

# ---------------------------------------------------------------------------
# Release
# ---------------------------------------------------------------------------
release-patch: ## Bump patch version and create tag
	@echo "$(BLUE)Creating patch release...$(NC)"
	bumpversion patch
	git push && git push --tags

release-minor: ## Bump minor version and create tag
	@echo "$(BLUE)Creating minor release...$(NC)"
	bumpversion minor
	git push && git push --tags

release-major: ## Bump major version and create tag
	@echo "$(BLUE)Creating major release...$(NC)"
	bumpversion major
	git push && git push --tags
