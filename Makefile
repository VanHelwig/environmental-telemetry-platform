.PHONY: install test test-integration lint format format-check check clean help

PYTHON := python
RUFF := $(PYTHON) -m ruff
PYTEST := $(PYTHON) -m pytest

# Install development dependencies
install:
	$(PYTHON) -m pip install -e '.[dev]'

# Run unit tests without database integration tests
test:
	$(PYTEST) tests -m "not integration" --maxfail=1 --disable-warnings -q

# Run database integration tests
test-integration:
	$(PYTEST) tests -m integration -v

# Check Python code for linting issues
lint:
	$(RUFF) check src tests

# Automatically fix supported lint issues and format code
format:
	$(RUFF) check --fix src tests
	$(RUFF) format src tests

# Verify formatting without modifying files
format-check:
	$(RUFF) format --check src tests

# Run all code-quality checks and tests
check: lint format-check test

# Remove generated Python cache files
clean:
	find src tests -type d -name '__pycache__' -prune -exec rm -rf {} +
	rm -rf .pytest_cache .ruff_cache

# Show available commands
help:
	@echo "Available commands:"
	@echo "  make install       	Install development dependencies"
	@echo "  make test          	Run unit tests"
	@echo "  make test-integration  Run database integration tests"
	@echo "  make lint          	Run Ruff linting"
	@echo "  make format        	Fix lint issues and format code"
	@echo "  make format-check  	Verify code formatting"
	@echo "  make check         	Run lint, formatting checks, and tests"
	@echo "  make clean         	Remove generated cache files"