# Load local development environment variables
-include .env

export DATABASE_URL POSTGRES_PASSWORD

.PHONY: install test test-integration lint format format-check check clean 
.PHONY: db-init db-backup db-create db-start db-stop
.PHONY: container-build container-run container-clean 
.PHONY: help

# Tooling configuration
PYTHON := python
RUFF := $(PYTHON) -m ruff
PYTEST := $(PYTHON) -m pytest
PODMAN := podman

# Ingestion layer configuration
IMAGE := etp-ingest:dev
STATE ?= 48
PARAMETER ?= 00060
LIMIT ?= 5

# Database configuration
DB_CONTAINER := etp-postgres
DB_IMAGE := docker.io/postgis/postgis:17-3.5
DB_VOLUME := etp-postgres-data
DB_NETWORK := kind
DB_NAME := telemetry
DB_USER := etp
DB_PORT := 5432
DB_MIGRATION := sql/001_create_observations.sql
BACKUP_DIR := backups

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

# Initialize the database schema (fresh database only)
db-init:
	$(PODMAN) exec -i $(DB_CONTAINER) \
		psql -v ON_ERROR_STOP=1 -U $(DB_USER) -d $(DB_NAME) \
		< $(DB_MIGRATION)

# Back up the PostgreSQL database
db-backup:
	@mkdir -p $(BACKUP_DIR)
	$(PODMAN) exec $(DB_CONTAINER) \
		pg_dump -U $(DB_USER) -d $(DB_NAME) -Fc \
		> $(BACKUP_DIR)/$(DB_NAME)-$$(date +%Y%m%d-%H%M%S).dump

# Create PostgreSQL using the persistent named volume
db-create:
	@test -n "$$POSTGRES_PASSWORD" || (echo "POSTGRES_PASSWORD is not configured" && exit 1)
	$(PODMAN) run -d \
		--name $(DB_CONTAINER) \
		--network $(DB_NETWORK) \
		-e POSTGRES_USER=$(DB_USER) \
		-e POSTGRES_PASSWORD \
		-e POSTGRES_DB=$(DB_NAME) \
		-p 127.0.0.1:$(DB_PORT):5432 \
		-v $(DB_VOLUME):/var/lib/postgresql/data \
		$(DB_IMAGE)

# Start the existing PostgreSQL container
db-start:
	$(PODMAN) start $(DB_CONTAINER)

# Stop the PostgreSQL container
db-stop:
	$(PODMAN) stop $(DB_CONTAINER)

# Build the ingestion container image
container-build:
	$(PODMAN) build -t $(IMAGE) -f Containerfile .

# Run the ingestion container against local PostgreSQL
container-run:
	@test -n "$$DATABASE_URL" || (echo "DATABASE_URL is not configured" && exit 1)
	$(PODMAN) run --rm \
		--network host \
		-e DATABASE_URL \
		$(IMAGE) \
		--state $(STATE) \
		--parameter $(PARAMETER) \
		--limit $(LIMIT)

# Remove the local ingestion container image
container-clean:
	$(PODMAN) rmi $(IMAGE)

# Show available commands
help:
	@echo "Development:"
	@echo "  make install             Install development dependencies"
	@echo "  make test                Run unit tests"
	@echo "  make test-integration    Run database integration tests"
	@echo "  make lint                Run Ruff linting"
	@echo "  make format              Fix lint issues and format code"
	@echo "  make format-check        Verify code formatting"
	@echo "  make check               Run lint, formatting checks, and tests"
	@echo "  make clean               Remove generated cache files"
	@echo ""
	@echo "Database:"
	@echo "  make db-init             Initialize a fresh database schema"
	@echo "  make db-backup           Create a timestamped PostgreSQL backup"
	@echo "  make db-create           Create PostgreSQL on the kind network"
	@echo "  make db-start            Start the existing PostgreSQL container"
	@echo "  make db-stop             Stop the PostgreSQL container"
	@echo ""
	@echo "Containers:"
	@echo "  make container-build     Build the ingestion container"
	@echo "  make container-run       Run containerized ingestion"
	@echo "  make container-clean     Remove the local container image"