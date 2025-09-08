# Simple EC2 Deployment Guide

This guide will help you deploy the Appnity Backend to an AWS EC2 free tier instance without Docker.

## Prerequisites

1. AWS EC2 instance (Ubuntu 20.04 LTS recommended)
2. Security group allowing HTTP (port 80) and SSH (port 22)
3. SSH access to your EC2 instance

## Quick Deployment

### Step 1: Connect to your EC2 instance

```bash
ssh -i your-key.pem ubuntu@your-ec2-public-ip
```

### Step 2: Upload your code

You can either:

**Option A: Upload files directly**
```bash
# On your local machine
scp -i your-key.pem -r . ubuntu@your-ec2-public-ip:/home/ubuntu/appnity_backend
```

**Option B: Use Git (if your code is in a repository)**
```bash
# On EC2 instance
git clone your-repository-url /home/ubuntu/appnity_backend
```

### Step 3: Run the deployment script

```bash
cd /home/ubuntu/appnity_backend
chmod +x deploy.sh
./deploy.sh
```

The script will automatically:
- Install Python, Nginx, and dependencies
- Set up virtual environment
- Install Python packages
- Configure Django settings
- Create database and admin user
- Set up Gunicorn service
- Configure Nginx
- Start all services

### Step 4: Access your application

- **API Documentation**: `http://your-ec2-public-ip/api/docs/`
- **Admin Panel**: `http://your-ec2-public-ip/admin/`
- **Admin Login**: `admin` / `admin123`

## API Endpoints

Your backend will provide these endpoints:

### Blog Posts
- `GET /api/v1/blogs/` - List all blog posts
- `GET /api/v1/blogs/{slug}/` - Get specific blog post
- `GET /api/v1/blogs/featured/` - Get featured posts
- `GET /api/v1/blogs/categories/` - List categories
- `GET /api/v1/blogs/tags/` - List tags

### Products
- `GET /api/v1/products/` - List all products
- `GET /api/v1/products/{slug}/` - Get specific product
- `GET /api/v1/products/featured/` - Get featured products

### Portfolio
- `GET /api/v1/portfolio/` - List portfolio projects
- `GET /api/v1/portfolio/{slug}/` - Get specific project
- `GET /api/v1/portfolio/featured/` - Get featured projects

### Training
- `GET /api/v1/training/courses/` - List courses
- `GET /api/v1/training/courses/{slug}/` - Get specific course
- `GET /api/v1/training/instructors/` - List instructors

### Careers
- `GET /api/v1/careers/positions/` - List job positions
- `GET /api/v1/careers/positions/{slug}/` - Get specific position
- `POST /api/v1/careers/positions/{slug}/apply/` - Submit application

### Testimonials
- `GET /api/v1/testimonials/` - List testimonials
- `GET /api/v1/testimonials/featured/` - Get featured testimonials
- `POST /api/v1/testimonials/submit/` - Submit testimonial

### Contact
- `POST /api/v1/contacts/` - Submit contact form

## Frontend Integration

### Example API calls for your frontend:

```javascript
// Fetch blog posts
const response = await fetch('http://your-ec2-ip/api/v1/blogs/');
const blogs = await response.json();

// Fetch featured products
const response = await fetch('http://your-ec2-ip/api/v1/products/featured/');
const products = await response.json();

// Submit contact form
const response = await fetch('http://your-ec2-ip/api/v1/contacts/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    name: 'John Doe',
    email: 'john@example.com',
    inquiry_type: 'general',
    message: 'Hello, I have a question...'
  })
});
```

## Managing Content

Use the Django Admin Panel at `http://your-ec2-ip/admin/` to:

1. **Create and manage blog posts**
2. **Add products and features**
3. **Manage portfolio projects**
4. **Create training courses**
5. **Post job positions**
6. **Review testimonials and contact forms**

## Troubleshooting

### Check service status
```bash
sudo systemctl status appnity
sudo systemctl status nginx
```

### View logs
```bash
sudo journalctl -u appnity -f
sudo tail -f /var/log/nginx/error.log
```

### Restart services
```bash
sudo systemctl restart appnity
sudo systemctl restart nginx
```

### Update code
```bash
cd /var/www/appnity
git pull  # if using git
source venv/bin/activate
pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate
sudo systemctl restart appnity
```

## Security Notes

1. **Change default admin password** after first login
2. **Update SECRET_KEY** in `.env` file
3. **Configure proper ALLOWED_HOSTS** for your domain
4. **Set up SSL certificate** for production use
5. **Regular security updates**: `sudo apt update && sudo apt upgrade`

## Cost Optimization

- Uses SQLite database (no additional database costs)
- Runs on single EC2 instance
- Uses Nginx for static file serving
- Optimized for AWS free tier limits

Your backend is now ready for production use! 🚀