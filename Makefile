.PHONY: help dev test build up down clean install lint format

# Default target
help:
	@echo "Art & Technology Knowledge Miner - Available Commands:"
	@echo ""
	@echo "Development:"
	@echo "  dev          - Start development environment"
	@echo "  install      - Install all dependencies"
	@echo "  test         - Run all tests"
	@echo "  lint         - Run linting"
	@echo "  format       - Format code"
	@echo ""
	@echo "Docker:"
	@echo "  up           - Start all services with Docker Compose"
	@echo "  down         - Stop all services"
	@echo "  build        - Build all Docker images"
	@echo "  clean        - Clean up Docker resources"
	@echo ""
	@echo "Pipeline:"
	@echo "  ingest       - Run ingestion pipeline"
	@echo "  search       - Run search CLI"
	@echo "  trends       - Run trends analysis"

# Development environment
dev:
	@echo "Starting development environment..."
	@echo "Backend: http://localhost:8000"
	@echo "Frontend: http://localhost:5173"
	@echo "ChromaDB: http://localhost:8001"
	@echo ""
	@echo "Run 'make up' to start with Docker Compose"

# Install dependencies
install:
	@echo "Installing Python dependencies..."
	cd pipeline && pip install -r requirements.txt
	cd backend && pip install -r requirements.txt
	@echo "Installing Node.js dependencies..."
	cd frontend && npm install

# Run tests
test:
	@echo "Running Python tests..."
	cd pipeline && python -m pytest tests/ -v
	cd backend && python -m pytest tests/ -v
	@echo "Running frontend tests..."
	cd frontend && npm test

# Linting
lint:
	@echo "Running Python linting..."
	cd pipeline && ruff check . && black --check .
	cd backend && ruff check . && black --check .
	@echo "Running frontend linting..."
	cd frontend && npm run lint

# Format code
format:
	@echo "Formatting Python code..."
	cd pipeline && black . && ruff check --fix .
	cd backend && black . && ruff check --fix .
	@echo "Formatting frontend code..."
	cd frontend && npm run format

# Docker commands
up:
	@echo "Starting services with Docker Compose..."
	docker-compose up -d
	@echo "Services started! Visit http://localhost:5173"

down:
	@echo "Stopping services..."
	docker-compose down

build:
	@echo "Building Docker images..."
	docker-compose build

clean:
	@echo "Cleaning up Docker resources..."
	docker-compose down -v --remove-orphans
	docker system prune -f

# Pipeline commands
ingest:
	@echo "Running ingestion pipeline..."
	cd pipeline && python -m pipeline.cli crawl --queries "artificial intelligence art" "computer vision museums" --max-pages 20

search:
	@echo "Running search CLI..."
	cd pipeline && python -m pipeline.cli search "artificial intelligence in art"

trends:
	@echo "Running trends analysis..."
	cd pipeline && python -m pipeline.cli trends --facet all --granularity year

# Demo commands
demo:
	@echo "Running demo..."
	cd pipeline && python -m pipeline.cli demo

# Development server commands
dev-backend:
	@echo "Starting backend development server..."
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-frontend:
	@echo "Starting frontend development server..."
	cd frontend && npm run dev

# Database commands
db-reset:
	@echo "Resetting database..."
	docker-compose down
	docker volume rm art-tech-knowledge-miner_chroma_data || true
	docker-compose up -d chromadb
	@echo "Database reset complete"

# Logs
logs:
	docker-compose logs -f

logs-backend:
	docker-compose logs -f backend

logs-frontend:
	docker-compose logs -f frontend

logs-chromadb:
	docker-compose logs -f chromadb
