.PHONY: help install migrate start-api start-worker start-inference start-all test clean format lint

help:
	@echo "Meeting Summarizer Backend - Available Commands:"
	@echo "  make install          - Install dependencies"
	@echo "  make migrate          - Run database migrations"
	@echo "  make start-api        - Start FastAPI server"
	@echo "  make start-worker     - Start background worker"
	@echo "  make start-inference  - Start local inference service"
	@echo "  make start-all        - Start all services"
	@echo "  make test             - Run all tests"
	@echo "  make test-unit        - Run unit tests only"
	@echo "  make test-integration - Run integration tests only"
	@echo "  make format           - Format code with black"
	@echo "  make lint             - Lint code with ruff"
	@echo "  make clean            - Clean cache and temp files"

install:
	pip install -r requirements.txt

migrate:
	python -m db.migrate

start-api:
	uvicorn app.main:app --host $(shell grep API_HOST .env 2>/dev/null | cut -d '=' -f2 || echo "127.0.0.1") --port $(shell grep API_PORT .env 2>/dev/null | cut -d '=' -f2 || echo "8000") --reload

start-worker:
	python -m workers.worker

start-inference:
	python -m inference.serve

start-all:
	@echo "Starting all services..."
	@trap 'kill 0' EXIT; \
	python -m inference.serve & \
	sleep 5; \
	python -m workers.worker & \
	uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload & \
	wait

test:
	pytest tests/ -v --cov=. --cov-report=term-missing --cov-report=html

test-unit:
	pytest tests/unit/ -v --cov=. --cov-report=term-missing

test-integration:
	pytest tests/integration/ -v

format:
	black app/ workers/ models/ db/ inference/ tests/

lint:
	ruff check app/ workers/ models/ db/ inference/ tests/

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name ".coverage" -delete
