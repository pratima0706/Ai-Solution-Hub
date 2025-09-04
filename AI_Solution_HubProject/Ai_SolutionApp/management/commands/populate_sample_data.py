from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from Ai_SolutionApp.models import (
    Contact, Service, PastSolution, Event, Gallery, 
    Testimonial, Article, SiteSettings
)

class Command(BaseCommand):
    help = 'Populate database with sample data for testing'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample data...')
        
        # Get or create admin user for articles
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@aisolutionshub.com',
                'first_name': 'Admin',
                'last_name': 'User',
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write('Created admin user')
        
        # Create sample services
        services_data = [
            {
                'title': 'AI-Powered Customer Service',
                'description': 'Transform your customer support with intelligent chatbots and automated response systems.',
                'icon': 'fas fa-robot',
                'features': ['24/7 Availability', 'Multi-language Support', 'Sentiment Analysis'],
                'pricing_tier': 'professional',
                'is_featured': True,
                'order': 1
            },
            {
                'title': 'Predictive Analytics Dashboard',
                'description': 'Make data-driven decisions with advanced predictive analytics and business intelligence.',
                'icon': 'fas fa-chart-line',
                'features': ['Real-time Analytics', 'Custom Reports', 'Trend Forecasting'],
                'pricing_tier': 'enterprise',
                'is_featured': True,
                'order': 2
            },
            {
                'title': 'Automated Content Generation',
                'description': 'Create engaging content automatically using advanced AI writing tools.',
                'icon': 'fas fa-pen-fancy',
                'features': ['SEO Optimization', 'Multiple Formats', 'Brand Voice Matching'],
                'pricing_tier': 'basic',
                'is_featured': False,
                'order': 3
            }
        ]
        
        for service_data in services_data:
            service, created = Service.objects.get_or_create(
                title=service_data['title'],
                defaults=service_data
            )
            if created:
                self.stdout.write(f'Created service: {service.title}')
        
        # Create sample past solutions
        solutions_data = [
            {
                'title': 'E-commerce AI Optimization',
                'client_name': 'TechMart Inc.',
                'industry': 'E-commerce',
                'description': 'Implemented AI-powered recommendation engine that increased sales by 35%.',
                'challenge': 'Low conversion rates and poor product recommendations.',
                'solution': 'Developed machine learning algorithms for personalized product suggestions.',
                'results': '35% increase in sales, 50% improvement in user engagement.',
                'technologies_used': ['Python', 'TensorFlow', 'React', 'PostgreSQL'],
                'completion_date': timezone.now().date() - timedelta(days=30),
                'is_featured': True
            },
            {
                'title': 'Healthcare Data Analytics',
                'client_name': 'MediCare Solutions',
                'industry': 'Healthcare',
                'description': 'Built comprehensive analytics platform for patient data management.',
                'challenge': 'Fragmented patient data across multiple systems.',
                'solution': 'Created unified data platform with AI-powered insights.',
                'results': '40% reduction in data processing time, improved patient outcomes.',
                'technologies_used': ['Python', 'Apache Spark', 'Docker', 'MongoDB'],
                'completion_date': timezone.now().date() - timedelta(days=60),
                'is_featured': True
            }
        ]
        
        for solution_data in solutions_data:
            solution, created = PastSolution.objects.get_or_create(
                title=solution_data['title'],
                defaults=solution_data
            )
            if created:
                self.stdout.write(f'Created solution: {solution.title}')
        
        # Create sample events
        events_data = [
            {
                'title': 'AI Innovation Summit 2024',
                'description': 'Join industry leaders for a comprehensive look at the future of AI in business.',
                'event_type': 'conference',
                'start_date': timezone.now() + timedelta(days=30),
                'end_date': timezone.now() + timedelta(days=30, hours=8),
                'location': 'San Francisco Convention Center',
                'is_virtual': False,
                'max_participants': 500,
                'current_participants': 150,
                'is_featured': True
            },
            {
                'title': 'Machine Learning Workshop',
                'description': 'Hands-on workshop covering the fundamentals of machine learning.',
                'event_type': 'workshop',
                'start_date': timezone.now() + timedelta(days=15),
                'end_date': timezone.now() + timedelta(days=15, hours=4),
                'location': 'Virtual Event',
                'is_virtual': True,
                'max_participants': 50,
                'current_participants': 25,
                'is_featured': False
            }
        ]
        
        for event_data in events_data:
            event, created = Event.objects.get_or_create(
                title=event_data['title'],
                defaults=event_data
            )
            if created:
                self.stdout.write(f'Created event: {event.title}')
        
        # Create sample articles
        articles_data = [
            {
                'title': 'The Future of AI in Business',
                'slug': 'future-ai-business',
                'excerpt': 'Exploring how artificial intelligence is transforming modern business operations.',
                'content': 'Artificial intelligence is revolutionizing the way businesses operate...',
                'author': admin_user,
                'category': 'ai_insights',
                'is_published': True,
                'is_featured': True
            },
            {
                'title': 'Getting Started with Machine Learning',
                'slug': 'getting-started-ml',
                'excerpt': 'A beginner\'s guide to understanding and implementing machine learning solutions.',
                'content': 'Machine learning can seem intimidating at first, but with the right approach...',
                'author': admin_user,
                'category': 'technology',
                'is_published': True,
                'is_featured': False
            }
        ]
        
        for article_data in articles_data:
            article, created = Article.objects.get_or_create(
                slug=article_data['slug'],
                defaults=article_data
            )
            if created:
                self.stdout.write(f'Created article: {article.title}')
        
        # Create sample testimonials
        testimonials_data = [
            {
                'customer_name': 'Sarah Johnson',
                'company': 'TechStart Inc.',
                'job_title': 'CEO',
                'rating': 5,
                'review': 'AI Solution Hub transformed our business operations. The AI-powered analytics dashboard gave us insights we never had before.',
                'is_verified': True,
                'is_featured': True
            },
            {
                'customer_name': 'Michael Chen',
                'company': 'RetailMax',
                'job_title': 'Operations Manager',
                'rating': 5,
                'review': 'Outstanding service and results. Our customer satisfaction increased by 40% after implementing their AI chatbot.',
                'is_verified': True,
                'is_featured': True
            },
            {
                'customer_name': 'Emily Rodriguez',
                'company': 'HealthCare Plus',
                'job_title': 'IT Director',
                'rating': 4,
                'review': 'Professional team with excellent technical expertise. The data analytics solution exceeded our expectations.',
                'is_verified': False,
                'is_featured': False
            }
        ]
        
        for testimonial_data in testimonials_data:
            testimonial, created = Testimonial.objects.get_or_create(
                customer_name=testimonial_data['customer_name'],
                company=testimonial_data['company'],
                defaults=testimonial_data
            )
            if created:
                self.stdout.write(f'Created testimonial: {testimonial.customer_name}')
        
        # Create sample contacts
        contacts_data = [
            {
                'name': 'John Smith',
                'email': 'john.smith@example.com',
                'phone': '+15550123',
                'company': 'Innovation Corp',
                'job_title': 'CTO',
                'job_details': 'Interested in AI solutions for our manufacturing process.',
                'status': 'new',
                'country': 'United States'
            },
            {
                'name': 'Maria Garcia',
                'email': 'maria.garcia@techco.com',
                'phone': '+15550456',
                'company': 'TechCo Solutions',
                'job_title': 'Product Manager',
                'job_details': 'Looking for predictive analytics for our e-commerce platform.',
                'status': 'contacted',
                'country': 'United States'
            },
            {
                'name': 'David Kim',
                'email': 'david.kim@startup.io',
                'phone': '+82212345678',
                'company': 'StartupIO',
                'job_title': 'Founder',
                'job_details': 'Need help with AI implementation for our mobile app.',
                'status': 'in_progress',
                'country': 'South Korea'
            }
        ]
        
        for contact_data in contacts_data:
            contact, created = Contact.objects.get_or_create(
                email=contact_data['email'],
                defaults=contact_data
            )
            if created:
                self.stdout.write(f'Created contact: {contact.name}')
        
        # Create site settings
        site_settings, created = SiteSettings.objects.get_or_create(
            id='00000000-0000-0000-0000-000000000001',
            defaults={
                'site_name': 'AI Solution Hub',
                'site_description': 'Leading provider of AI solutions for businesses',
                'contact_email': 'info@aisolutionshub.com',
                'contact_phone': '+1-555-0123',
                'address': '123 AI Street, Tech City, TC 12345',
                'social_links': {
                    'facebook': 'https://facebook.com/aisolutionshub',
                    'twitter': 'https://twitter.com/aisolutionshub',
                    'linkedin': 'https://linkedin.com/company/aisolutionshub'
                }
            }
        )
        
        if created:
            self.stdout.write('Created site settings')
        
        self.stdout.write(
            self.style.SUCCESS('Successfully created sample data!')
        )
