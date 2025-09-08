#!/bin/bash

# Deployment script for EC2 Ubuntu server
# Run this script on your EC2 instance

echo "🚀 Starting Appnity Backend Deployment..."

# Update system packages
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install Python and pip
echo "🐍 Installing Python and dependencies..."
sudo apt install -y python3 python3-pip python3-venv nginx

# Create application directory
echo "📁 Setting up application directory..."
sudo mkdir -p /var/www/appnity
sudo chown $USER:$USER /var/www/appnity
cd /var/www/appnity

# Clone or copy your code here
# git clone your-repo-url .
# Or if you're uploading files manually, skip this step

# Create virtual environment
echo "🔧 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo "📚 Installing Python packages..."
pip install -r requirements.txt

# Create environment file
echo "⚙️ Creating environment configuration..."
cat > .env << EOL
SECRET_KEY=your-super-secret-key-change-this-in-production
DEBUG=False
ALLOWED_HOSTS=*
DATABASE_URL=sqlite:///db.sqlite3
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EOL

# Run Django setup
echo "🗄️ Setting up Django..."
python manage.py collectstatic --noinput
python manage.py migrate
echo "from users.models import User; User.objects.create_superuser('admin', 'admin@appnity.co.in', 'admin123')" | python manage.py shell

# Create systemd service for Gunicorn
echo "🔧 Setting up Gunicorn service..."
sudo tee /etc/systemd/system/appnity.service > /dev/null << EOL
[Unit]
Description=Appnity Backend
After=network.target

[Service]
User=$USER
Group=www-data
WorkingDirectory=/var/www/appnity
Environment="PATH=/var/www/appnity/venv/bin"
ExecStart=/var/www/appnity/venv/bin/gunicorn --workers 3 --bind unix:/var/www/appnity/appnity.sock appnity_backend.wsgi:application
Restart=always

[Install]
WantedBy=multi-user.target
EOL

# Start and enable Gunicorn service
sudo systemctl start appnity
sudo systemctl enable appnity

# Configure Nginx
echo "🌐 Configuring Nginx..."
sudo tee /etc/nginx/sites-available/appnity > /dev/null << EOL
server {
    listen 80;
    server_name _;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        root /var/www/appnity;
    }
    
    location /media/ {
        root /var/www/appnity;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/appnity/appnity.sock;
    }
}
EOL

# Enable Nginx site
sudo ln -sf /etc/nginx/sites-available/appnity /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Test and restart Nginx
sudo nginx -t
sudo systemctl restart nginx

# Set up log rotation
echo "📝 Setting up log rotation..."
sudo tee /etc/logrotate.d/appnity > /dev/null << EOL
/var/www/appnity/logs/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 $USER $USER
}
EOL

# Create logs directory
mkdir -p /var/www/appnity/logs

# Set proper permissions
sudo chown -R $USER:www-data /var/www/appnity
sudo chmod -R 755 /var/www/appnity

echo "✅ Deployment completed!"
echo ""
echo "🎉 Your Appnity Backend is now running!"
echo "📍 API Documentation: http://your-server-ip/api/docs/"
echo "🔧 Admin Panel: http://your-server-ip/admin/"
echo "👤 Admin Login: admin / admin123"
echo ""
echo "🔧 Useful commands:"
echo "  - Check service status: sudo systemctl status appnity"
echo "  - View logs: sudo journalctl -u appnity -f"
echo "  - Restart service: sudo systemctl restart appnity"
echo "  - Restart Nginx: sudo systemctl restart nginx"
echo ""
echo "⚠️  Remember to:"
echo "  1. Change the SECRET_KEY in .env file"
echo "  2. Change admin password after first login"
echo "  3. Configure your domain name in ALLOWED_HOSTS"
echo "  4. Set up SSL certificate for production"