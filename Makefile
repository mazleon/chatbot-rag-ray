.PHONY: help install dev backend frontend test lint format docker-build docker-up docker-down clean

help:
	@echo "Life Insurance Agent - Available Commands"
	@echo ""
	@echo "  make install       Install dependencies (backend + frontend)"
	@echo "  make dev          Run backend in development mode"
	@echo "  make backend      Start backend server only"
	@echo "  make frontend     Start frontend dev server"
	@echo "  make test         Run all tests"
	@echo "  make lint         Lint code (ruff + eslint)"
	@echo "  make format       Format code (black + prettier)"
	@echo "  make docker-build Build Docker images"
	@echo "  make docker-up    Start all services with Docker"
	@echo "  make docker-down  Stop all Docker services"
	@echo "  make clean        Remove generated files"

install:
	uv sync
	cd frontend && npm install

dev:
	uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000

backend:
	uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000

frontend:
	cd frontend && npm run dev

test:
	pytest
	cd frontend && npm test

lint:
	ruff check .
	cd frontend && npm run lint

format:
	black .
	cd frontend && npx prettier --write .

docker-build:
	docker-compose build

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

clean:
	rm -rf __pycache__ .pytest_cache .coverage htmlcov
	rm -rf frontend/node_modules frontend/dist
	rm -rf .venv
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true