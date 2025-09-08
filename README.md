# Appnity Backend API

A comprehensive Django REST Framework backend for Appnity Software Private Limited's website and products.

## 🚀 Features

- **JWT Authentication** - Secure token-based authentication
- **Blog Management** - Full-featured blog system with Markdown support
- **Contact Forms** - Contact form submissions with email notifications
- **Newsletter** - Newsletter subscription management
- **Training Courses** - Course management system
- **Career Portal** - Job positions and application management
- **Portfolio** - Project showcase with detailed case studies
- **Testimonials** - Customer testimonial management
- **Admin Panel** - Comprehensive Django admin interface
- **API Documentation** - Auto-generated Swagger/OpenAPI docs

## 🛠 Tech Stack

- **Backend**: Django 4.2, Django REST Framework
- **Database**: PostgreSQL (production), SQLite (development)
- **Authentication**: JWT with djangorestframework-simplejwt
- **Documentation**: drf-spectacular (Swagger/OpenAPI)
- **Content**: Markdown support with django-markdownx
- **Deployment**: Docker, Gunicorn, Nginx

## 📋 Prerequisites

- Python 3.11+
- PostgreSQL 13+ (for production)
- Redis (for caching, optional)
- Docker & Docker Compose (for containerized deployment)

## 🚀 Quick Start

### 1. Clone and Setup

```bash
# Clone the repository
git clone <repository-url>
cd appnity_backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your settings
nano .env
```

### 3. Database Setup

```bash
# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Load sample data (optional)
python manage.py loaddata fixtures/sample_data.json
```

### 4. Run Development Server

```bash
# Start development server
python manage.py runserver

# API will be available at:
# http://localhost:8000/api/v1/
# Admin panel: http://localhost:8000/admin/
# API docs: http://localhost:8000/api/docs/
```

## 🐳 Docker Deployment

### Development with Docker

```bash
# Build and run with Docker Compose
docker-compose up --build

# Run migrations in container
docker-compose exec web python manage.py migrate

# Create superuser in container
docker-compose exec web python manage.py createsuperuser
```

### Production Deployment

```bash
# Build production image
docker build -t appnity-backend:latest .

# Run with production settings
docker run -d \
  --name appnity-backend \
  -p 8000:8000 \
  -e DEBUG=False \
  -e DATABASE_URL=postgresql://user:pass@host:5432/db \
  appnity-backend:latest
```

## 📚 API Documentation

### Authentication Endpoints

```bash
# Register new user
POST /api/v1/auth/register/
{
  "email": "user@example.com",
  "username": "username",
  "first_name": "John",
  "last_name": "Doe",
  "password": "securepassword",
  "password_confirm": "securepassword"
}

# Login
POST /api/v1/auth/login/
{
  "email": "user@example.com",
  "password": "securepassword"
}

# Get user profile
GET /api/v1/auth/profile/
Authorization: Bearer <access_token>

# Refresh token
POST /api/v1/auth/token/refresh/
{
  "refresh": "<refresh_token>"
}
```

### Blog Endpoints

```bash
# Get all blog posts
GET /api/v1/blogs/

# Get single blog post
GET /api/v1/blogs/<slug>/

# Get featured posts
GET /api/v1/blogs/featured/

# Get recent posts
GET /api/v1/blogs/recent/?limit=5

# Create blog post (admin only)
POST /api/v1/blogs/
Authorization: Bearer <access_token>
{
  "title": "My Blog Post",
  "excerpt": "Short description",
  "content": "# Markdown content here",
  "category": 1,
  "tags": [1, 2, 3],
  "status": "published"
}
```

### Contact Endpoints

```bash
# Submit contact form
POST /api/v1/contacts/
{
  "name": "John Doe",
  "email": "john@example.com",
  "inquiry_type": "general",
  "message": "Hello, I have a question..."
}

# Get contact submissions (admin only)
GET /api/v1/contacts/list/
Authorization: Bearer <access_token>
```

### Newsletter Endpoints

```bash
# Subscribe to newsletter
POST /api/v1/newsletter/subscribe/
{
  "email": "user@example.com"
}

# Unsubscribe from newsletter
POST /api/v1/newsletter/unsubscribe/
{
  "email": "user@example.com"
}
```

### Training Endpoints

```bash
# Get all courses
GET /api/v1/training/courses/

# Get single course
GET /api/v1/training/courses/<slug>/

# Get featured courses
GET /api/v1/training/courses/featured/

# Get instructors
GET /api/v1/training/instructors/
```

### Career Endpoints

```bash
# Get job positions
GET /api/v1/careers/positions/

# Get open positions
GET /api/v1/careers/positions/open/

# Get single position
GET /api/v1/careers/positions/<slug>/

# Submit job application
POST /api/v1/careers/positions/<slug>/apply/
Content-Type: multipart/form-data
{
  "first_name": "John",
  "last_name": "Doe",
  "email": "john@example.com",
  "phone": "+1234567890",
  "cover_letter": "I am interested in this position...",
  "resume": <file>,
  "portfolio_url": "https://johndoe.dev",
  "years_of_experience": 5
}
```

### Portfolio Endpoints

```bash
# Get portfolio projects
GET /api/v1/portfolio/

# Get single project
GET /api/v1/portfolio/<slug>/

# Get featured projects
GET /api/v1/portfolio/featured/
```

### Testimonial Endpoints

```bash
# Get testimonials
GET /api/v1/testimonials/

# Get featured testimonials
GET /api/v1/testimonials/featured/

# Submit testimonial
POST /api/v1/testimonials/submit/
{
  "name": "John Doe",
  "email": "john@example.com",
  "title": "Senior Developer",
  "company": "Tech Corp",
  "content": "Great experience with Appnity!",
  "rating": 5,
  "product_name": "CodeGram"
}
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Django secret key | Required |
| `DEBUG` | Debug mode | `False` |
| `ALLOWED_HOSTS` | Allowed hosts | `localhost,127.0.0.1` |
| `DATABASE_URL` | Database connection string | SQLite |
| `EMAIL_HOST` | SMTP host | `smtp.gmail.com` |
| `EMAIL_HOST_USER` | SMTP username | Required |
| `EMAIL_HOST_PASSWORD` | SMTP password | Required |

### Database Configuration

#### PostgreSQL (Recommended for Production)

```bash
# Install PostgreSQL
sudo apt-get install postgresql postgresql-contrib

# Create database and user
sudo -u postgres psql
CREATE DATABASE appnity_db;
CREATE USER appnity_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE appnity_db TO appnity_user;
\q

# Update .env file
DATABASE_URL=postgresql://appnity_user:your_password@localhost:5432/appnity_db
```

#### SQLite (Development Only)

SQLite is used automatically in development if no DATABASE_URL is provided.

### Email Configuration

#### Gmail SMTP

```bash
# Enable 2-factor authentication in Gmail
# Generate app-specific password
# Update .env file
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

## 🧪 Testing

```bash
# Run all tests
python manage.py test

# Run tests with coverage
pip install coverage
coverage run --source='.' manage.py test
coverage report
coverage html

# Run specific app tests
python manage.py test blogs
python manage.py test users
```

## 📊 Monitoring & Logging

### Logs

Logs are stored in the `logs/` directory:
- `django.log` - Application logs
- `error.log` - Error logs

### Health Check

```bash
# Check API health
curl http://localhost:8000/api/v1/health/
```

## 🔒 Security

### Production Security Checklist

- [ ] Set `DEBUG=False`
- [ ] Use strong `SECRET_KEY`
- [ ] Configure HTTPS with SSL certificates
- [ ] Set up proper CORS origins
- [ ] Enable security middleware
- [ ] Configure rate limiting
- [ ] Set up monitoring and alerting
- [ ] Regular security updates

### Security Headers

The application includes security headers:
- X-Frame-Options
- X-Content-Type-Options
- X-XSS-Protection
- Strict-Transport-Security
- Content-Security-Policy

## 📈 Performance

### Optimization Features

- Database query optimization with select_related/prefetch_related
- Pagination for large datasets
- Static file compression and caching
- Database indexing for frequently queried fields
- Redis caching (optional)

### Monitoring

- Health check endpoints
- Logging configuration
- Error tracking with Sentry (optional)
- Performance monitoring

## 🚀 Deployment

### Manual Deployment

```bash
# 1. Prepare server
sudo apt-get update
sudo apt-get install python3 python3-pip postgresql nginx

# 2. Clone and setup
git clone <repository-url>
cd appnity_backend
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env with production settings

# 4. Setup database
python manage.py migrate
python manage.py collectstatic

# 5. Setup Gunicorn service
sudo cp deploy/gunicorn.service /etc/systemd/system/
sudo systemctl enable gunicorn
sudo systemctl start gunicorn

# 6. Configure Nginx
sudo cp nginx.conf /etc/nginx/sites-available/appnity
sudo ln -s /etc/nginx/sites-available/appnity /etc/nginx/sites-enabled/
sudo systemctl restart nginx
```

### Docker Deployment

```bash
# Production deployment with Docker
docker-compose -f docker-compose.prod.yml up -d
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guide
- Write comprehensive tests
- Update documentation
- Use meaningful commit messages
- Add docstrings to all functions and classes

## 📝 API Response Format

### Success Response

```json
{
  "data": {...},
  "message": "Success message",
  "status": "success"
}
```

### Error Response

```json
{
  "error": "Error message",
  "details": {...},
  "status": "error"
}
```

### Pagination Response

```json
{
  "count": 100,
  "next": "http://api.example.com/items/?page=3",
  "previous": "http://api.example.com/items/?page=1",
  "results": [...]
}
```

## 🆘 Troubleshooting

### Common Issues

#### Database Connection Error
```bash
# Check PostgreSQL service
sudo systemctl status postgresql

# Check database credentials in .env
# Ensure database exists and user has permissions
```

#### Static Files Not Loading
```bash
# Collect static files
python manage.py collectstatic --clear

# Check STATIC_ROOT and STATIC_URL settings
# Ensure web server can serve static files
```

#### Email Not Sending
```bash
# Check email settings in .env
# Verify SMTP credentials
# Check firewall settings for SMTP ports
```

#### Permission Denied Errors
```bash
# Check file permissions
sudo chown -R www-data:www-data /path/to/app

# Check Django permissions
python manage.py shell
>>> from django.contrib.auth.models import User
>>> user = User.objects.get(username='admin')
>>> user.is_staff = True
>>> user.save()
```

## 📞 Support

- **Email**: hello@appnity.co.in
- **Documentation**: https://appnity.co.in/docs
- **Issues**: Create an issue in the repository

## 📄 License

This project is proprietary software owned by Appnity Software Private Limited.

---

**Appnity Software Private Limited** - Building developer-first digital products