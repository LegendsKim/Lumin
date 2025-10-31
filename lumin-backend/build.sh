#!/usr/bin/env bash
# Render build script for Lumin SaaS
# Exit on error
set -o errexit

echo "🚀 Starting Lumin build process..."

# Upgrade pip and setuptools
echo "📦 Upgrading pip, setuptools, and wheel..."
pip install --upgrade pip setuptools wheel

# Install dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput --clear

# Run database migrations
echo "🗄️  Running database migrations..."
python manage.py migrate --noinput

echo "✅ Build completed successfully!"
