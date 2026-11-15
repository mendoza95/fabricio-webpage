.PHONY: help install lint format test check all clean

# Default target when you just run 'make'
.DEFAULT_GOAL := help

help: ## Show this help menu
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Install production and dev dependencies
	python -m pip install --upgrade pip
	pip install ruff pytest
	@if [ -f requirements.txt ]; then pip install -r requirements.txt; fi

lint: ## Run Ruff linter checks
	ruff check . --exclude backend --exclude frontend

format: ## Auto-format code with Ruff
	ruff check . --exclude backend --exclude frontend --fix
	ruff format . --exclude backend --exclude frontend

test: ## Run tests with Pytest
	pytest -v tests/

check: lint test ## Run all checks (linting + tests) locally before pushing

all: format check ## Auto-format code, run linter, and run tests

clean: ## Clean up temporary Python cache and pytest files
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +