
VENV_NAME?=.venv

.DEFAULT_GOAL := help

help: ## Show this help message
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

setup: ## Create virtual environment and sync dependencies
	uv sync

test: setup ## Run tests with pytest
	uv run -m pytest tests/ -v

build: setup ## Build the package
	uv run -m build

clean: ## Clean up generated files and virtual environment
	rm -rf $(VENV_NAME) dist/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
