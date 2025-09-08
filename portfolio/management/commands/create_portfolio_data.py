from django.core.management.base import BaseCommand
from portfolio.models import PortfolioProject, ProjectTechnology, ProjectChallenge, ProjectResult


class Command(BaseCommand):
    help = 'Create sample portfolio data for development and testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing portfolio data before creating sample data',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('🗑️ Clearing existing portfolio data...')
            PortfolioProject.objects.all().delete()

        self.stdout.write('📊 Creating sample portfolio data...')
        
        # Create portfolio projects
        self.create_portfolio_projects()

        self.stdout.write(
            self.style.SUCCESS('✅ Portfolio sample data created successfully!')
        )

    def create_portfolio_projects(self):
        """Create sample portfolio projects"""
        projects = [
            {
                'title': 'CodeGram',
                'subtitle': 'Social Media for Developers',
                'description': '''# CodeGram - Social Platform for Developers

A comprehensive social platform where developers share code snippets, discover solutions, and build meaningful connections within the global developer community.

## Project Overview

CodeGram was built to address the fragmented nature of developer code sharing. We created a unified platform that combines social media features with developer-specific functionality.

## Key Features

- **Real-time collaborative editing** with live cursor tracking
- **Syntax highlighting** for 25+ programming languages
- **Community voting and discussions** to surface quality content
- **Developer profile portfolios** to showcase work and skills
- **Advanced search and filtering** for easy content discovery

## Technical Implementation

The platform was built using modern web technologies with a focus on performance and scalability:

- Frontend built with React and TypeScript for type safety
- Real-time features implemented using WebSocket connections
- Database optimized for fast queries and concurrent access
- Responsive design ensuring great experience across all devices

## Challenges Overcome

- **Real-time Collaboration**: Implementing conflict resolution for simultaneous editing
- **Scalable Syntax Highlighting**: Optimizing performance for large code snippets
- **Community Moderation**: Building automated and manual moderation systems

## Results Achieved

- **2.5K+ active developers** using the platform monthly
- **15K+ code snippets** shared and discovered
- **4.9/5 user satisfaction** rating from community feedback
- **99.9% uptime** with robust infrastructure monitoring''',
                'category': 'web',
                'status': 'completed',
                'client_name': 'Appnity Internal',
                'duration': '6 months',
                'duration_weeks': 24,
                'team_size': 3,
                'user_count': '2.5K+',
                'performance_metric': '99.9% uptime',
                'business_impact': '15K+ snippets shared',
                'live_url': 'https://codegram.appnity.co.in',
                'github_url': 'https://github.com/appnity-software/codegram',
                'is_featured': True,
                'order': 1,
                'technologies': [
                    {'name': 'React', 'category': 'Frontend'},
                    {'name': 'TypeScript', 'category': 'Frontend'},
                    {'name': 'Prisma', 'category': 'Backend'},
                    {'name': 'Supabase', 'category': 'Backend'},
                    {'name': 'TailwindCSS', 'category': 'Styling'},
                    {'name': 'Framer Motion', 'category': 'Animation'},
                ],
                'challenges': [
                    {
                        'title': 'Real-time Collaboration Implementation',
                        'description': 'Building a robust real-time collaborative editing system that handles multiple users editing the same code snippet simultaneously.',
                        'solution': 'Implemented operational transformation algorithms with conflict resolution and implemented WebSocket-based real-time synchronization.'
                    },
                    {
                        'title': 'Scalable Syntax Highlighting',
                        'description': 'Ensuring syntax highlighting performs well with large code snippets and multiple languages.',
                        'solution': 'Used web workers for syntax highlighting processing and implemented lazy loading for large code blocks.'
                    },
                    {
                        'title': 'Community Moderation System',
                        'description': 'Creating an effective moderation system to maintain code quality and community standards.',
                        'solution': 'Built automated content filtering combined with community reporting and admin review workflows.'
                    }
                ],
                'results': [
                    {
                        'title': 'User Growth',
                        'description': 'Achieved rapid user adoption and engagement',
                        'metric': '2.5K+ active developers'
                    },
                    {
                        'title': 'Content Creation',
                        'description': 'High volume of quality content shared',
                        'metric': '15K+ code snippets'
                    },
                    {
                        'title': 'User Satisfaction',
                        'description': 'Exceptional user satisfaction and retention',
                        'metric': '4.9/5 rating'
                    }
                ]
            },
            {
                'title': 'TechFlow CRM',
                'subtitle': 'Customer Relationship Management Platform',
                'description': '''# TechFlow CRM - Modern CRM for Tech Companies

A comprehensive customer relationship management platform built specifically for technology companies, featuring advanced analytics, automated workflows, and seamless integrations.

## Project Overview

TechFlow CRM was developed for a growing tech company that needed a modern, scalable CRM solution tailored to their specific workflows and requirements.

## Key Features

- **Advanced lead management** with intelligent scoring and routing
- **Automated email sequences** for nurturing prospects
- **Sales pipeline visualization** with drag-and-drop functionality
- **Custom reporting dashboard** with real-time analytics
- **Third-party integrations** with popular tools and services

## Technical Architecture

- Built with Next.js for server-side rendering and optimal performance
- PostgreSQL database with optimized queries for large datasets
- Stripe integration for payment processing and subscription management
- Deployed on Vercel with automatic scaling and global CDN

## Business Impact

The CRM platform transformed the client's sales process, resulting in significant improvements in efficiency and revenue tracking.''',
                'category': 'saas',
                'status': 'completed',
                'client_name': 'TechFlow Solutions',
                'duration': '4 months',
                'duration_weeks': 16,
                'team_size': 4,
                'user_count': '500+',
                'performance_metric': '+40% efficiency',
                'business_impact': '$2M+ tracked deals',
                'live_url': 'https://crm.techflow.com',
                'is_featured': True,
                'order': 2,
                'technologies': [
                    {'name': 'Next.js', 'category': 'Frontend'},
                    {'name': 'TypeScript', 'category': 'Frontend'},
                    {'name': 'PostgreSQL', 'category': 'Database'},
                    {'name': 'Stripe', 'category': 'Payment'},
                    {'name': 'Vercel', 'category': 'Deployment'},
                ],
                'challenges': [
                    {
                        'title': 'Complex Data Migration',
                        'description': 'Migrating data from legacy CRM system without data loss or downtime.',
                        'solution': 'Developed incremental migration scripts with data validation and rollback capabilities.'
                    },
                    {
                        'title': 'Custom Reporting Engine',
                        'description': 'Building flexible reporting system for various business metrics.',
                        'solution': 'Created modular reporting framework with drag-and-drop report builder interface.'
                    }
                ],
                'results': [
                    {
                        'title': 'Sales Efficiency',
                        'description': 'Significant improvement in sales team productivity',
                        'metric': '40% increase'
                    },
                    {
                        'title': 'Deal Tracking',
                        'description': 'Total value of deals tracked in the system',
                        'metric': '$2M+ tracked'
                    }
                ]
            },
            {
                'title': 'FitTracker Pro',
                'subtitle': 'Fitness & Wellness Mobile Application',
                'description': '''# FitTracker Pro - Comprehensive Fitness App

A feature-rich fitness tracking application with workout planning, nutrition tracking, and social features for fitness enthusiasts.

## Project Overview

FitTracker Pro was developed for a fitness startup looking to create a comprehensive wellness platform that combines workout tracking, nutrition monitoring, and social engagement.

## Key Features

- **Workout planning and tracking** with exercise library and progress monitoring
- **Nutrition and calorie tracking** with barcode scanning and meal planning
- **Social challenges and leaderboards** to motivate users
- **Wearable device integration** with popular fitness trackers
- **Personal trainer matching** and virtual coaching features

## Technical Implementation

- Cross-platform mobile app built with React Native
- Firebase backend for real-time data synchronization
- HealthKit and Google Fit integration for device data
- Stripe integration for premium subscriptions
- Push notifications for workout reminders and achievements

## User Engagement

The app achieved excellent user engagement metrics with high retention rates and positive app store reviews.''',
                'category': 'mobile',
                'status': 'completed',
                'client_name': 'FitLife Startup',
                'duration': '5 months',
                'duration_weeks': 20,
                'team_size': 3,
                'user_count': '10K+',
                'performance_metric': '4.8/5 rating',
                'business_impact': '75% retention rate',
                'is_featured': True,
                'order': 3,
                'technologies': [
                    {'name': 'React Native', 'category': 'Mobile'},
                    {'name': 'TypeScript', 'category': 'Frontend'},
                    {'name': 'Firebase', 'category': 'Backend'},
                    {'name': 'Stripe', 'category': 'Payment'},
                    {'name': 'HealthKit', 'category': 'Integration'},
                ],
                'challenges': [
                    {
                        'title': 'HealthKit Integration Complexity',
                        'description': 'Integrating with various health and fitness APIs while maintaining data privacy.',
                        'solution': 'Implemented secure data handling with user consent management and HIPAA compliance measures.'
                    },
                    {
                        'title': 'Offline Functionality',
                        'description': 'Ensuring app works seamlessly without internet connection.',
                        'solution': 'Built robust offline storage with automatic sync when connection is restored.'
                    }
                ],
                'results': [
                    {
                        'title': 'App Downloads',
                        'description': 'Total number of app downloads across platforms',
                        'metric': '10K+ downloads'
                    },
                    {
                        'title': 'User Retention',
                        'description': 'Monthly active user retention rate',
                        'metric': '75% retention'
                    }
                ]
            },
            {
                'title': 'EduPlatform LMS',
                'subtitle': 'Online Learning Management System',
                'description': '''# EduPlatform - Modern Learning Management System

A comprehensive LMS platform for educational institutions with course management, student tracking, and interactive learning tools.

## Project Overview

EduPlatform was developed for a progressive educational institution looking to modernize their online learning infrastructure and provide better tools for both educators and students.

## Key Features

- **Course creation and management** with multimedia content support
- **Interactive video lessons** with progress tracking and bookmarks
- **Real-time chat and discussions** for student-teacher interaction
- **Progress tracking and analytics** for performance monitoring
- **Certificate generation** with blockchain verification

## Technical Architecture

- React-based frontend with responsive design for all devices
- Node.js backend with MongoDB for flexible content storage
- Socket.io for real-time communication features
- AWS infrastructure for scalable video streaming
- Automated testing and continuous deployment pipeline

## Educational Impact

The platform significantly improved learning outcomes and student engagement across the institution.''',
                'category': 'web',
                'status': 'completed',
                'client_name': 'Progressive Education Institute',
                'duration': '8 months',
                'duration_weeks': 32,
                'team_size': 5,
                'user_count': '5K+',
                'performance_metric': '85% completion rate',
                'business_impact': '200+ courses created',
                'is_featured': False,
                'order': 4,
                'technologies': [
                    {'name': 'React', 'category': 'Frontend'},
                    {'name': 'Node.js', 'category': 'Backend'},
                    {'name': 'MongoDB', 'category': 'Database'},
                    {'name': 'Socket.io', 'category': 'Real-time'},
                    {'name': 'AWS', 'category': 'Infrastructure'},
                ],
                'challenges': [
                    {
                        'title': 'Video Streaming Optimization',
                        'description': 'Delivering high-quality video content to users with varying internet speeds.',
                        'solution': 'Implemented adaptive bitrate streaming with CDN optimization and progressive download.'
                    },
                    {
                        'title': 'Scalable Assessment System',
                        'description': 'Creating flexible assessment tools for different types of courses and subjects.',
                        'solution': 'Built modular assessment framework supporting multiple question types and automated grading.'
                    }
                ],
                'results': [
                    {
                        'title': 'Student Engagement',
                        'description': 'Active students using the platform',
                        'metric': '5K+ students'
                    },
                    {
                        'title': 'Course Completion',
                        'description': 'Average course completion rate',
                        'metric': '85% completion'
                    }
                ]
            }
        ]

        for project_data in projects:
            technologies = project_data.pop('technologies', [])
            challenges = project_data.pop('challenges', [])
            results = project_data.pop('results', [])
            
            project, created = PortfolioProject.objects.get_or_create(
                title=project_data['title'],
                defaults=project_data
            )
            
            if created:
                self.stdout.write(f'✅ Created project: {project.title}')
                
                # Add technologies
                for i, tech_data in enumerate(technologies):
                    ProjectTechnology.objects.create(
                        project=project,
                        order=i,
                        **tech_data
                    )
                
                # Add challenges
                for i, challenge_data in enumerate(challenges):
                    ProjectChallenge.objects.create(
                        project=project,
                        order=i,
                        **challenge_data
                    )
                
                # Add results
                for i, result_data in enumerate(results):
                    ProjectResult.objects.create(
                        project=project,
                        order=i,
                        **result_data
                    )
            else:
                self.stdout.write(f'⚠️ Project already exists: {project.title}')

        self.stdout.write('🎯 Created portfolio projects with technologies, challenges, and results')