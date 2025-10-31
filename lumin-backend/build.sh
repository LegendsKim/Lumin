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

# Skip collect static and migrations for initial deployment test
echo "⚠️  Skipping collectstatic and migrations for initial deployment test"
echo "💡 These will be added back after successful deployment"

echo "✅ Build completed successfully!"
