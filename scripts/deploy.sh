#!/bin/bash

# Appnity Backend Deployment Script
# This script deploys the Django backend to production

set -e

echo "🚀 Deploying Appnity Backend to Production..."

# Check if we're in the right directory
if [ ! -f "manage.py" ]; then
    echo "❌ Error: manage.py not found. Please run this script from the project root."
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ Error: .env file not found. Please create it from .env.example"
    exit 1
fi

# Load environment variables
export $(cat .env | grep -v '^#' | xargs)

# Check if DEBUG is set to False
if [ "$DEBUG" = "True" ]; then
    echo "⚠️ Warning: DEBUG is set to True. This should be False in production."
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Activate virtual environment
if [ -d "venv" ]; then
    echo "🔧 Activating virtual environment..."
    source venv/bin/activate
else
    echo "❌ Error: Virtual environment not found. Please run setup.sh first."
    exit 1
fi

# Install/update dependencies
echo "📚 Installing production dependencies..."
pip install -r requirements.txt

# Run database migrations
echo "🗄️ Running database migrations..."
python manage.py migrate --noinput

# Collect static files
echo "📦 Collecting static files..."
python manage.py collectstatic --noinput --clear

# Run Django system checks
echo "🔍 Running system checks..."
python manage.py check --deploy

# Test database connection
echo "🔗 Testing database connection..."
python manage.py dbshell --command="\q" 2>/dev/null || {
    echo "❌ Database connection failed"
    exit 1
}

# Restart services
echo "🔄 Restarting services..."
if systemctl is-active --quiet gunicorn; then
    sudo systemctl restart gunicorn
    echo "✅ Gunicorn restarted"
fi

if systemctl is-active --quiet nginx; then
    sudo systemctl reload nginx
    echo "✅ Nginx reloaded"
fi

# Health check
echo "🏥 Performing health check..."
sleep 5
if curl -f http://localhost:8000/api/v1/health/ >/dev/null 2>&1; then
    echo "✅ Health check passed"
else
    echo "❌ Health check failed"
    exit 1
fi

echo ""
echo "🎉 Deployment completed successfully!"
echo ""
echo "Your API is now live at:"
echo "  🌐 Production: https://appnity.co.in/api/v1/"
echo "  👨‍💼 Admin: https://appnity.co.in/admin/"
echo "  📚 Docs: https://appnity.co.in/api/docs/"
echo ""
echo "Monitor logs with:"
echo "  sudo journalctl -u gunicorn -f"
echo "  sudo tail -f /var/log/nginx/error.log"