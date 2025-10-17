#!/bin/bash
# Lumin Development Setup Script for Linux/Mac
# This script automates the setup of Docker containers and Django backend

set -e  # Exit on error

echo ""
echo "========================================"
echo "  Lumin Development Setup (Unix)"
echo "  Setting up Docker + Django"
echo "========================================"
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "[ERROR] Docker is not running!"
    echo "Please start Docker and try again."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "[ERROR] Docker Compose is not installed!"
    echo "Please install Docker Compose and try again."
    exit 1
fi

echo "[1/6] Starting Docker containers..."
docker-compose up -d

echo "[2/6] Waiting for services to be ready..."
sleep 10

echo "[3/6] Checking PostgreSQL health..."
until docker exec lumin-postgres pg_isready -U lumin_user > /dev/null 2>&1; do
    echo "[WARNING] PostgreSQL not ready yet, waiting..."
    sleep 2
done
echo "PostgreSQL is ready!"

echo "[4/6] Creating database (if not exists)..."
if docker exec lumin-postgres psql -U lumin_user -lqt | cut -d \| -f 1 | grep -qw lumin_db; then
    echo "Database 'lumin_db' already exists."
else
    docker exec lumin-postgres psql -U lumin_user -c "CREATE DATABASE lumin_db;"
    echo "Database 'lumin_db' created successfully!"
fi

echo "[5/6] Running Django migrations..."
cd lumin-backend

if [ -d "venv" ]; then
    source venv/bin/activate
    python manage.py migrate
    if [ $? -ne 0 ]; then
        echo "[ERROR] Migrations failed"
        exit 1
    fi
else
    echo "[WARNING] Virtual environment not found at lumin-backend/venv"
    echo "Please create it with: python -m venv venv"
    echo "Then run: source venv/bin/activate"
    echo "And: pip install -r requirements.txt"
fi

cd ..

echo ""
echo "[6/6] Setup complete!"
echo ""
echo "========================================"
echo "  Services Status:"
echo "========================================"
docker-compose ps

echo ""
echo "========================================"
echo "  Next Steps:"
echo "========================================"
echo "1. Create superuser: python manage.py createsuperuser"
echo "2. Start backend: python manage.py runserver"
echo "3. Start frontend: cd lumin-frontend && npm run dev"
echo "4. Start Celery (optional): celery -A config worker -l info"
echo ""
echo "========================================"
echo "  Useful Commands:"
echo "========================================"
echo "- Stop containers: docker-compose stop"
echo "- View logs: docker-compose logs -f"
echo "- Restart: docker-compose restart"
echo ""
