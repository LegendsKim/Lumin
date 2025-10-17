# Lumin SaaS - Makefile for common development tasks
# Usage: make <target>

.PHONY: help setup docker-up docker-down docker-restart docker-logs clean migrate superuser dev-backend dev-frontend dev-celery

# Default target - show help
help:
	@echo "Lumin SaaS - Available Commands:"
	@echo ""
	@echo "Docker Commands:"
	@echo "  make docker-up       - Start Docker containers"
	@echo "  make docker-down     - Stop Docker containers"
	@echo "  make docker-restart  - Restart Docker containers"
	@echo "  make docker-logs     - View Docker logs"
	@echo "  make docker-clean    - Stop and remove containers + volumes"
	@echo ""
	@echo "Setup Commands:"
	@echo "  make setup           - Full project setup (Docker + DB + migrations)"
	@echo "  make db-create       - Create database"
	@echo "  make migrate         - Run Django migrations"
	@echo "  make superuser       - Create Django superuser"
	@echo ""
	@echo "Development Commands:"
	@echo "  make dev-backend     - Run Django development server"
	@echo "  make dev-frontend    - Run React development server"
	@echo "  make dev-celery      - Run Celery worker"
	@echo "  make dev-all         - Run all dev servers (requires tmux)"
	@echo ""
	@echo "Utility Commands:"
	@echo "  make clean           - Remove Python cache files"
	@echo "  make test            - Run backend tests"
	@echo "  make lint            - Run linters"
	@echo ""

# Docker commands
docker-up:
	@echo "Starting Docker containers..."
	docker-compose up -d
	@echo "Waiting for services..."
	@sleep 5
	@docker-compose ps

docker-down:
	@echo "Stopping Docker containers..."
	docker-compose stop

docker-restart:
	@echo "Restarting Docker containers..."
	docker-compose restart

docker-logs:
	@echo "Showing Docker logs (Ctrl+C to exit)..."
	docker-compose logs -f

docker-clean:
	@echo "WARNING: This will delete all data!"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		docker-compose down -v; \
		echo "\nContainers and volumes removed."; \
	else \
		echo "\nCancelled."; \
	fi

# Database commands
db-create:
	@echo "Creating database..."
	docker exec -it lumin-postgres psql -U lumin_user -tc "SELECT 1 FROM pg_database WHERE datname = 'lumin_db'" | grep -q 1 || \
	docker exec -it lumin-postgres psql -U lumin_user -c "CREATE DATABASE lumin_db;"
	@echo "Database ready!"

migrate:
	@echo "Running migrations..."
	cd lumin-backend && python manage.py migrate

superuser:
	@echo "Creating superuser..."
	cd lumin-backend && python manage.py createsuperuser

# Setup command
setup: docker-up db-create migrate
	@echo ""
	@echo "=========================================="
	@echo "  Setup Complete!"
	@echo "=========================================="
	@echo ""
	@echo "Next steps:"
	@echo "1. Create superuser: make superuser"
	@echo "2. Start backend: make dev-backend"
	@echo "3. Start frontend: make dev-frontend"
	@echo ""

# Development commands
dev-backend:
	@echo "Starting Django development server..."
	cd lumin-backend && python manage.py runserver

dev-frontend:
	@echo "Starting React development server..."
	cd lumin-frontend && npm run dev

dev-celery:
	@echo "Starting Celery worker..."
	cd lumin-backend && celery -A config worker -l info

dev-all:
	@echo "Starting all development servers (requires tmux)..."
	tmux new-session -d -s lumin 'cd lumin-backend && python manage.py runserver' \; \
		split-window -h 'cd lumin-frontend && npm run dev' \; \
		split-window -v 'cd lumin-backend && celery -A config worker -l info' \; \
		attach

# Utility commands
clean:
	@echo "Cleaning Python cache files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	@echo "Clean complete!"

test:
	@echo "Running backend tests..."
	cd lumin-backend && pytest --cov=apps

lint:
	@echo "Running linters..."
	@echo "Backend (Black + Flake8)..."
	cd lumin-backend && black . --check && flake8
	@echo "Frontend (ESLint)..."
	cd lumin-frontend && npm run lint
