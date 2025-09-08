#!/usr/bin/env python3
"""
Quick setup script for Appnity Backend
Run this after deployment to create sample data
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'appnity_backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from blogs.models import BlogPost, Category, Tag
from products.models import Product, ProductFeature
from testimonials.models import Testimonial
from portfolio.models import PortfolioProject
from training.models import Course, Instructor
from careers.models import JobPosition

User = get_user_model()

def create_admin_user():
    """Create admin user if it doesn't exist"""
    if not User.objects.filter(email='admin@appnity.co.in').exists():
        User.objects.create_superuser(
            email='admin@appnity.co.in',
            username='admin',
            first_name='Admin',
            last_name='User',
            password='admin123'
        )
        print("✅ Admin user created: admin@appnity.co.in / admin123")
    else:
        print("ℹ️ Admin user already exists")

def create_sample_data():
    """Create sample data for testing"""
    
    # Create blog category and post
    if not Category.objects.exists():
        category = Category.objects.create(
            name='Technology',
            description='Tech articles and insights'
        )
        
        admin_user = User.objects.get(email='admin@appnity.co.in')
        
        BlogPost.objects.create(
            title='Welcome to Appnity',
            excerpt='Building developer-first digital products',
            content='# Welcome to Appnity\n\nWe are building amazing developer tools and products.',
            author=admin_user,
            category=category,
            status='published',
            is_featured=True
        )
        print("✅ Sample blog post created")
    
    # Create sample product
    if not Product.objects.exists():
        product = Product.objects.create(
            name='CodeGram',
            tagline='Social media for developers',
            description='# CodeGram\n\nA platform for developers to share code and connect.',
            status='live',
            is_featured=True,
            user_count=2500,
            rating=4.9
        )
        
        ProductFeature.objects.create(
            product=product,
            title='Code Sharing',
            description='Share code snippets with syntax highlighting'
        )
        print("✅ Sample product created")
    
    # Create sample testimonial
    if not Testimonial.objects.exists():
        Testimonial.objects.create(
            name='John Doe',
            title='Senior Developer',
            company='Tech Corp',
            content='Great products and excellent support!',
            rating=5,
            is_featured=True
        )
        print("✅ Sample testimonial created")
    
    print("🎉 Sample data creation completed!")

def main():
    print("🚀 Setting up Appnity Backend...")
    
    try:
        create_admin_user()
        create_sample_data()
        
        print("\n✅ Setup completed successfully!")
        print("\n📍 Access your application:")
        print("   - Admin Panel: http://your-server/admin/")
        print("   - API Docs: http://your-server/api/docs/")
        print("   - Login: admin@appnity.co.in / admin123")
        print("\n⚠️  Remember to change the admin password!")
        
    except Exception as e:
        print(f"❌ Error during setup: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()