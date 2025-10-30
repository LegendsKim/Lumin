#!/usr/bin/env bash
# Render build script for Lumin SaaS
# Exit on error
set -o errexit

echo "🚀 Starting Lumin build process..."

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --no-input

# Run database migrations
echo "🗄️  Running database migrations..."
python manage.py migrate --no-input

# Create cache table (if using database cache)
echo "💾 Setting up cache..."
python manage.py createcachetable || echo "Cache table already exists or not needed"

echo "✅ Build completed successfully!"
