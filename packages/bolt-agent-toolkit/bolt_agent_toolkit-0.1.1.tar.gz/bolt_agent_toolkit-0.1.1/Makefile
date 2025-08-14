
VENV_NAME?=.venv

.DEFAULT_GOAL := help

help: ## Show this help message
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

setup: ## Create virtual environment and sync dependencies
	uv sync

test: setup ## Run tests with pytest
	uv run -m pytest tests/ -v

lint: setup ## Format and lint code with isort, black, and mypy
	uv run isort bolt_agent_toolkit/
	uv run black bolt_agent_toolkit/
	uv run pylint bolt_agent_toolkit/
	uv run mypy bolt_agent_toolkit/

lint-isort: setup ## Check import sorting with isort
	uv run isort --check-only --diff bolt_agent_toolkit/

lint-black: setup ## Check code formatting with black
	uv run black --check --diff bolt_agent_toolkit/

lint-pylint: setup ## Run pylint checks
	uv run pylint bolt_agent_toolkit/

lint-mypy: setup ## Run mypy type checking
	uv run mypy bolt_agent_toolkit/

build: setup ## Build the package
	cp ../LICENSE LICENSE
	uv run -m build
	rm LICENSE

clean: ## Clean up generated files and virtual environment
	rm -rf $(VENV_NAME) dist/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
