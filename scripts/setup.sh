#!/bin/bash

# Appnity Backend Setup Script
# This script sets up the Django backend for development

set -e

echo "🚀 Setting up Appnity Backend..."

# Check if Python 3.11+ is installed
python_version=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
required_version="3.11"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python 3.11+ is required. Current version: $python_version"
    exit 1
fi

echo "✅ Python version check passed"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Copy environment file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating environment file..."
    cp .env.example .env
    echo "⚠️ Please edit .env file with your settings before continuing"
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p logs media staticfiles

# Run migrations
echo "🗄️ Running database migrations..."
python manage.py migrate

# Collect static files
echo "📦 Collecting static files..."
python manage.py collectstatic --noinput

# Load sample data
echo "📊 Loading sample data..."
if [ -f "fixtures/sample_data.json" ]; then
    python manage.py loaddata fixtures/sample_data.json
fi

# Create superuser prompt
echo "👤 Create a superuser account:"
python manage.py createsuperuser

echo "✅ Setup complete!"
echo ""
echo "🎉 Your Appnity backend is ready!"
echo ""
echo "To start the development server:"
echo "  source venv/bin/activate"
echo "  python manage.py runserver"
echo ""
echo "Then visit:"
echo "  🌐 API: http://localhost:8000/api/v1/"
echo "  👨‍💼 Admin: http://localhost:8000/admin/"
echo "  📚 Docs: http://localhost:8000/api/docs/"
echo ""
echo "Happy coding! 🚀"