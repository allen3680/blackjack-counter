# Makefile for Blackjack Counter
# 21點計牌器 - 使用 Wong Halves 系統與基本策略

# Variables
PYTHON := python3
PIP := $(PYTHON) -m pip
SRC_DIR := src
TEST_DIR := tests
MODULE := blackjack-counter

# Colors for output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m # No Color

# Default target - show help
.DEFAULT_GOAL := help

.PHONY: help
help: ## Show this help message
	@echo "$(BLUE)Blackjack Counter - Development Commands$(NC)"
	@echo ""
	@echo "$(GREEN)Available targets:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-15s$(NC) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(BLUE)Examples:$(NC)"
	@echo "  make install    # Install project with all dependencies"
	@echo "  make run        # Run the application"
	@echo "  make check      # Run all quality checks"

.PHONY: install
install: ## Install project in development mode with all dependencies
	@echo "$(BLUE)Installing blackjack-counter in development mode...$(NC)"
	$(PIP) install -e ".[dev]"
	@echo "$(GREEN)✓ Installation complete$(NC)"

.PHONY: dev-install
dev-install: ## Install only development dependencies
	@echo "$(BLUE)Installing development dependencies...$(NC)"
	$(PIP) install black mypy ruff pytest pytest-cov pytest-mock pyyaml
	@echo "$(GREEN)✓ Development dependencies installed$(NC)"

.PHONY: run
run: ## Run the blackjack counter application (PyQt6)
	@echo "$(BLUE)Starting Blackjack Counter (PyQt6)...$(NC)"
	$(PYTHON) -m src.gui.app_modern_qt

.PHONY: format
format: ## Format code with Black
	@echo "$(BLUE)Formatting code with Black...$(NC)"
	$(PYTHON) -m black $(SRC_DIR) $(TEST_DIR) --line-length 100
	@echo "$(GREEN)✓ Code formatted$(NC)"

.PHONY: lint
lint: ## Run linting with Ruff
	@echo "$(BLUE)Running Ruff linter...$(NC)"
	$(PYTHON) -m ruff check $(SRC_DIR) $(TEST_DIR)
	@echo "$(GREEN)✓ Linting complete$(NC)"

.PHONY: lint-fix
lint-fix: ## Run linting with Ruff and auto-fix issues
	@echo "$(BLUE)Running Ruff linter with auto-fix...$(NC)"
	$(PYTHON) -m ruff check $(SRC_DIR) $(TEST_DIR) --fix
	@echo "$(GREEN)✓ Linting and fixes complete$(NC)"

.PHONY: type
type: ## Type check with MyPy
	@echo "$(BLUE)Running MyPy type checker...$(NC)"
	$(PYTHON) -m mypy $(SRC_DIR) --strict
	@echo "$(GREEN)✓ Type checking complete$(NC)"

.PHONY: test
test: ## Run tests with pytest
	@echo "$(BLUE)Running tests...$(NC)"
	@if [ -d "$(TEST_DIR)" ] && [ "$$(find $(TEST_DIR) -name 'test_*.py' -type f | wc -l)" -gt 0 ]; then \
		$(PYTHON) -m pytest $(TEST_DIR) -v; \
		echo "$(GREEN)✓ Tests complete$(NC)"; \
	else \
		echo "$(YELLOW)⚠ No tests found in $(TEST_DIR)$(NC)"; \
	fi

.PHONY: test-cov
test-cov: ## Run tests with coverage report
	@echo "$(BLUE)Running tests with coverage...$(NC)"
	@if [ -d "$(TEST_DIR)" ] && [ "$$(find $(TEST_DIR) -name 'test_*.py' -type f | wc -l)" -gt 0 ]; then \
		$(PYTHON) -m pytest $(TEST_DIR) --cov=$(SRC_DIR) --cov-report=html --cov-report=term; \
		echo "$(GREEN)✓ Coverage report generated in htmlcov/$(NC)"; \
	else \
		echo "$(YELLOW)⚠ No tests found in $(TEST_DIR)$(NC)"; \
	fi

.PHONY: check
check: format lint type test ## Run all quality checks (format, lint, type, test)
	@echo "$(GREEN)✓ All quality checks passed!$(NC)"

.PHONY: check-fast
check-fast: lint type ## Run quick quality checks (lint, type only)
	@echo "$(GREEN)✓ Quick checks passed!$(NC)"

.PHONY: clean
clean: ## Clean build artifacts and cache files
	@echo "$(BLUE)Cleaning build artifacts...$(NC)"
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf $(SRC_DIR)/*.egg-info
	rm -rf $(SRC_DIR)/**/__pycache__
	rm -rf $(TEST_DIR)/**/__pycache__
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	find . -type f -name '*.pyc' -delete
	find . -type f -name '*.pyo' -delete
	find . -type d -name '__pycache__' -delete
	@echo "$(GREEN)✓ Clean complete$(NC)"

.PHONY: build
build: clean ## Build distribution packages
	@echo "$(BLUE)Building distribution packages...$(NC)"
	$(PYTHON) -m pip install --upgrade build
	$(PYTHON) -m build
	@echo "$(GREEN)✓ Build complete - check dist/ directory$(NC)"

.PHONY: dev
dev: install run ## Install and run the application

.PHONY: requirements
requirements: ## Generate requirements.txt from pyproject.toml
	@echo "$(BLUE)Generating requirements.txt...$(NC)"
	$(PIP) install pip-tools
	pip-compile pyproject.toml -o requirements.txt
	pip-compile pyproject.toml --extra dev -o requirements-dev.txt
	@echo "$(GREEN)✓ Requirements files generated$(NC)"

.PHONY: update
update: ## Update all dependencies to latest versions
	@echo "$(BLUE)Updating dependencies...$(NC)"
	$(PIP) install --upgrade pip setuptools wheel
	$(PIP) install --upgrade -e ".[dev]"
	@echo "$(GREEN)✓ Dependencies updated$(NC)"

.PHONY: verify
verify: ## Verify project setup and dependencies
	@echo "$(BLUE)Verifying project setup...$(NC)"
	@echo "Python version: $$($(PYTHON) --version)"
	@echo "Pip version: $$($(PIP) --version)"
	@echo ""
	@echo "$(YELLOW)Checking required files...$(NC)"
	@for file in pyproject.toml README.md CLAUDE.md $(SRC_DIR) $(SRC_DIR)/gui/app.py; do \
		if [ -e "$$file" ]; then \
			echo "$(GREEN)✓$(NC) $$file exists"; \
		else \
			echo "$(RED)✗$(NC) $$file missing"; \
		fi \
	done
	@echo ""
	@echo "$(YELLOW)Checking Python packages...$(NC)"
	@$(PYTHON) -c "import yaml" 2>/dev/null && echo "$(GREEN)✓$(NC) PyYAML installed" || echo "$(RED)✗$(NC) PyYAML not installed"
	@$(PYTHON) -c "import black" 2>/dev/null && echo "$(GREEN)✓$(NC) Black installed" || echo "$(YELLOW)⚠$(NC) Black not installed (dev)"
	@$(PYTHON) -c "import mypy" 2>/dev/null && echo "$(GREEN)✓$(NC) MyPy installed" || echo "$(YELLOW)⚠$(NC) MyPy not installed (dev)"
	@$(PYTHON) -c "import ruff" 2>/dev/null && echo "$(GREEN)✓$(NC) Ruff installed" || echo "$(YELLOW)⚠$(NC) Ruff not installed (dev)"
	@echo "$(GREEN)✓ Verification complete$(NC)"