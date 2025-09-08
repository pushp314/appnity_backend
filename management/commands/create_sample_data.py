from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from blogs.models import BlogPost, Category, Tag
from products.models import Product, ProductFeature, ProductTechnology
from testimonials.models import Testimonial
from training.models import Course, Instructor
from careers.models import JobPosition, JobSkill

User = get_user_model()


class Command(BaseCommand):
    help = 'Create sample data for development and testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before creating sample data',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('🗑️ Clearing existing data...')
            self.clear_data()

        self.stdout.write('📊 Creating sample data...')
        
        # Create users
        admin_user = self.create_users()
        
        # Create blog data
        self.create_blog_data(admin_user)
        
        # Create products
        self.create_products()
        
        # Create testimonials
        self.create_testimonials()
        
        # Create training courses
        self.create_courses()
        
        # Create job positions
        self.create_jobs()

        self.stdout.write(
            self.style.SUCCESS('✅ Sample data created successfully!')
        )

    def clear_data(self):
        """Clear existing data"""
        BlogPost.objects.all().delete()
        Category.objects.all().delete()
        Tag.objects.all().delete()
        Product.objects.all().delete()
        Testimonial.objects.all().delete()
        Course.objects.all().delete()
        JobPosition.objects.all().delete()

    def create_users(self):
        """Create sample users"""
        admin_user, created = User.objects.get_or_create(
            email='admin@appnity.co.in',
            defaults={
                'username': 'admin',
                'first_name': 'Alex',
                'last_name': 'Chen',
                'role': 'admin',
                'is_staff': True,
                'is_superuser': True,
                'bio': 'Founder & CEO of Appnity Software Private Limited'
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write('👤 Created admin user')

        return admin_user

    def create_blog_data(self, author):
        """Create sample blog data"""
        # Categories
        categories = [
            {'name': 'Product Development', 'color': '#3b82f6'},
            {'name': 'Technology', 'color': '#10b981'},
            {'name': 'Company Culture', 'color': '#8b5cf6'},
        ]
        
        for cat_data in categories:
            Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={'color': cat_data['color']}
            )

        # Tags
        tag_names = ['React', 'TypeScript', 'Django', 'Startup', 'Remote Work', 'Developer Tools']
        for tag_name in tag_names:
            Tag.objects.get_or_create(name=tag_name)

        # Blog posts
        posts = [
            {
                'title': 'Building CodeGram: From Idea to 2.5K Users',
                'excerpt': 'The complete story behind our flagship product and the lessons we learned.',
                'content': '''# Building CodeGram: From Idea to 2.5K Users

When we started Appnity, we had a simple vision: build tools that developers actually want to use. CodeGram was our first attempt at making that vision a reality.

## The Problem

Developers were scattered across multiple platforms to share code, get feedback, and collaborate. We saw an opportunity to create a dedicated space for the developer community.

## The Solution

CodeGram combines the best of social media with developer-specific features:

- **Syntax highlighting** for 25+ programming languages
- **Real-time collaboration** on code snippets
- **Community voting** to surface the best content
- **Developer portfolios** to showcase work

## The Results

In just 8 months, we've achieved:
- 2.5K+ active developers
- 15K+ code snippets shared
- 4.9/5 user satisfaction rating

The journey continues as we build more tools for the developer community.''',
                'category': 'Product Development',
                'tags': ['Startup', 'Developer Tools'],
                'is_featured': True
            },
            {
                'title': 'The Future of Developer Tools: AI-Powered Workflows',
                'excerpt': 'How AI is reshaping developer workflows and what it means for the future.',
                'content': '''# The Future of Developer Tools: AI-Powered Workflows

Artificial Intelligence is transforming how developers work, and we're at the forefront of this revolution.

## Current State

Today's developers juggle multiple tools and contexts. AI can help streamline these workflows.

## Our Vision

We're building AI-powered features into our tools:
- Intelligent code suggestions
- Automated documentation
- Smart error detection
- Context-aware assistance

## What's Next

The future of development is collaborative intelligence between humans and AI.''',
                'category': 'Technology',
                'tags': ['React', 'TypeScript'],
                'is_featured': False
            }
        ]

        for post_data in posts:
            category = Category.objects.get(name=post_data['category'])
            tags = Tag.objects.filter(name__in=post_data['tags'])
            
            post, created = BlogPost.objects.get_or_create(
                title=post_data['title'],
                defaults={
                    'excerpt': post_data['excerpt'],
                    'content': post_data['content'],
                    'author': author,
                    'category': category,
                    'status': 'published',
                    'is_featured': post_data['is_featured'],
                    'read_time': 8
                }
            )
            if created:
                post.tags.set(tags)

        self.stdout.write('📝 Created blog data')

    def create_products(self):
        """Create sample products"""
        products = [
            {
                'name': 'CodeGram',
                'tagline': 'Social media platform for developers',
                'description': '''# CodeGram

A comprehensive social platform where developers share code snippets, discover solutions, and build meaningful connections.

## Key Features

- **Code Sharing**: Share snippets with syntax highlighting
- **Community**: Vote, comment, and discuss code
- **Profiles**: Showcase your work and skills
- **Real-time**: Collaborate in real-time
- **Search**: Advanced filtering and discovery''',
                'status': 'live',
                'website_url': 'https://codegram.appnity.co.in',
                'github_url': 'https://github.com/appnity-software/codegram',
                'is_featured': True,
                'user_count': 2500,
                'rating': 4.9,
                'features': [
                    {'title': 'Syntax Highlighting', 'description': 'Support for 25+ programming languages'},
                    {'title': 'Real-time Collaboration', 'description': 'Edit code together in real-time'},
                    {'title': 'Community Voting', 'description': 'Upvote the best snippets'},
                ],
                'technologies': [
                    {'name': 'React', 'category': 'Frontend'},
                    {'name': 'TypeScript', 'category': 'Frontend'},
                    {'name': 'Supabase', 'category': 'Backend'},
                    {'name': 'TailwindCSS', 'category': 'Styling'},
                ]
            }
        ]

        for product_data in products:
            features = product_data.pop('features', [])
            technologies = product_data.pop('technologies', [])
            
            product, created = Product.objects.get_or_create(
                name=product_data['name'],
                defaults=product_data
            )
            
            if created:
                # Add features
                for i, feature_data in enumerate(features):
                    ProductFeature.objects.create(
                        product=product,
                        order=i,
                        **feature_data
                    )
                
                # Add technologies
                for i, tech_data in enumerate(technologies):
                    ProductTechnology.objects.create(
                        product=product,
                        order=i,
                        **tech_data
                    )

        self.stdout.write('🛠️ Created products')

    def create_testimonials(self):
        """Create sample testimonials"""
        testimonials = [
            {
                'name': 'Sarah Chen',
                'title': 'Senior Developer',
                'company': 'TechCorp',
                'content': 'CodeGram has completely changed how I share and discover code snippets. The community is incredibly supportive and the platform is beautifully designed.',
                'rating': 5,
                'testimonial_type': 'user',
                'product_name': 'CodeGram',
                'is_featured': True
            },
            {
                'name': 'Marcus Rodriguez',
                'title': 'Full-Stack Developer',
                'company': 'Freelancer',
                'content': 'Appnity builds exactly what developers need. Their attention to detail and understanding of developer workflows is unmatched.',
                'rating': 5,
                'testimonial_type': 'customer',
                'is_featured': True
            }
        ]

        for testimonial_data in testimonials:
            Testimonial.objects.get_or_create(
                name=testimonial_data['name'],
                defaults=testimonial_data
            )

        self.stdout.write('💬 Created testimonials')

    def create_courses(self):
        """Create sample courses"""
        # Create instructor
        instructor, created = Instructor.objects.get_or_create(
            name='Alex Chen',
            defaults={
                'bio': 'Full-stack developer with 8+ years of experience building developer tools.',
                'title': 'Senior Developer & Instructor',
                'experience_years': 8
            }
        )

        # Create course
        course, created = Course.objects.get_or_create(
            title='Web Development Mastery',
            defaults={
                'subtitle': 'Complete full-stack web development course',
                'description': '''# Web Development Mastery

Learn to build modern web applications from scratch using the latest technologies and best practices.

## What You'll Learn

- HTML5, CSS3, and JavaScript fundamentals
- React and TypeScript development
- Node.js and Express backend
- Database design with PostgreSQL
- API development and integration
- Deployment with modern platforms

## Course Structure

This comprehensive course is designed to take you from beginner to professional web developer.''',
                'level': 'beginner',
                'duration': '12 weeks',
                'price': 299.00,
                'student_count': 2500,
                'rating': 4.9,
                'is_featured': True
            }
        )

        self.stdout.write('🎓 Created courses')

    def create_jobs(self):
        """Create sample job positions"""
        positions = [
            {
                'title': 'Senior Full-Stack Developer',
                'department': 'Engineering',
                'job_type': 'full_time',
                'level': 'senior',
                'location': 'Remote',
                'description': '''# Senior Full-Stack Developer

Join our core team to build and scale our product portfolio. You'll work across the entire stack and have significant impact on product direction.

## What You'll Do

- Build and maintain our product suite
- Collaborate with design and product teams
- Mentor junior developers
- Drive technical decisions

## What We Offer

- Competitive salary and equity
- Remote-first culture
- Latest equipment and tools
- Learning and conference budget''',
                'requirements': '''## Requirements

- 5+ years of React/TypeScript experience
- Strong backend development skills (Node.js, Python, or similar)
- Experience with cloud platforms (AWS, Vercel, etc.)
- Passion for developer tools and platforms
- Excellent communication skills''',
                'responsibilities': '''## Responsibilities

- Develop new features and maintain existing codebase
- Participate in code reviews and technical discussions
- Collaborate with cross-functional teams
- Contribute to technical documentation
- Help scale our infrastructure''',
                'salary_min': 80000,
                'salary_max': 120000,
                'equity_offered': True,
                'is_featured': True,
                'skills': [
                    {'name': 'React', 'skill_type': 'required', 'experience_years': 5},
                    {'name': 'TypeScript', 'skill_type': 'required', 'experience_years': 3},
                    {'name': 'Node.js', 'skill_type': 'required', 'experience_years': 3},
                    {'name': 'PostgreSQL', 'skill_type': 'preferred', 'experience_years': 2},
                ]
            }
        ]

        for position_data in positions:
            skills = position_data.pop('skills', [])
            
            position, created = JobPosition.objects.get_or_create(
                title=position_data['title'],
                defaults=position_data
            )
            
            if created:
                # Add skills
                for i, skill_data in enumerate(skills):
                    JobSkill.objects.create(
                        position=position,
                        order=i,
                        **skill_data
                    )

        self.stdout.write('💼 Created job positions')