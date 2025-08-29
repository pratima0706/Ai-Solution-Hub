from django.core.management.base import BaseCommand
from django.utils import timezone
from Ai_SolutionApp.models import (
    Service, PastSolution, Event, Gallery, Testimonial, 
    Article, SiteSettings, AdminDashboard
)
from django.contrib.auth.models import User
import uuid


class Command(BaseCommand):
    help = 'Seed the database with initial sample data'

    def handle(self, *args, **options):
        self.stdout.write('Seeding database with sample data...')
        
        # Create SiteSettings
        if not SiteSettings.objects.exists():
            site_settings = SiteSettings.objects.create(
                site_name="AI Solution Hub",
                site_description="Leading provider of innovative AI solutions for businesses",
                contact_email="info@aisolutionhub.com",
                contact_phone="+1 (555) 123-4567",
                address="123 AI Street, Tech City, TC 12345",
                maintenance_mode=False,
                analytics_code="GA-123456789",
                social_links={
                    'facebook': 'https://facebook.com/aisolutionhub',
                    'twitter': 'https://twitter.com/aisolutionhub',
                    'linkedin': 'https://linkedin.com/company/aisolutionhub'
                }
            )
            self.stdout.write(f'✓ Created SiteSettings: {site_settings.site_name}')
        
        # Create Services
        services_data = [
            {
                'title': 'AI-Powered Analytics',
                'description': 'Transform your data into actionable insights with our advanced AI analytics platform.',
                'icon': 'fas fa-chart-line',
                'features': ['Real-time data processing', 'Predictive analytics', 'Custom dashboards', 'API integration'],
                'pricing_tier': 'enterprise',
                'is_featured': True,
                'order': 1
            },
            {
                'title': 'Machine Learning Solutions',
                'description': 'Custom ML models tailored to your business needs and industry requirements.',
                'icon': 'fas fa-brain',
                'features': ['Custom model development', 'Training data preparation', 'Model optimization', 'Ongoing support'],
                'pricing_tier': 'enterprise',
                'is_featured': True,
                'order': 2
            },
            {
                'title': 'Natural Language Processing',
                'description': 'Build intelligent chatbots and language understanding systems.',
                'icon': 'fas fa-comments',
                'features': ['Chatbot development', 'Text analysis', 'Language translation', 'Sentiment analysis'],
                'pricing_tier': 'professional',
                'is_featured': False,
                'order': 3
            },
            {
                'title': 'Computer Vision',
                'description': 'Image and video analysis solutions for automation and quality control.',
                'icon': 'fas fa-eye',
                'features': ['Object detection', 'Image classification', 'Video analysis', 'Quality control'],
                'pricing_tier': 'enterprise',
                'is_featured': False,
                'order': 4
            },
            {
                'title': 'AI Consulting',
                'description': 'Strategic guidance for AI implementation and digital transformation.',
                'icon': 'fas fa-lightbulb',
                'features': ['Strategy development', 'Technology assessment', 'Implementation planning', 'Team training'],
                'pricing_tier': 'professional',
                'is_featured': False,
                'order': 5
            },
            {
                'title': 'Data Engineering',
                'description': 'Build robust data pipelines and infrastructure for AI applications.',
                'icon': 'fas fa-database',
                'features': ['Data pipeline design', 'ETL development', 'Data warehousing', 'Performance optimization'],
                'pricing_tier': 'professional',
                'is_featured': False,
                'order': 6
            }
        ]
        
        for service_data in services_data:
            service, created = Service.objects.get_or_create(
                title=service_data['title'],
                defaults=service_data
            )
            if created:
                self.stdout.write(f'✓ Created Service: {service.title}')
        
        # Create Past Solutions
        solutions_data = [
            {
                'title': 'E-commerce AI Recommendation Engine',
                'client_name': 'TechRetail Inc.',
                'industry': 'E-commerce',
                'description': 'AI-powered recommendation system for e-commerce platform',
                'challenge': 'Low conversion rates due to poor product recommendations',
                'solution': 'Implemented a collaborative filtering algorithm with real-time user behavior analysis',
                'results': '35% increase in conversion rates, 28% improvement in average order value',
                'technologies_used': ['Python', 'TensorFlow', 'Redis', 'PostgreSQL'],
                'completion_date': timezone.now().date() - timezone.timedelta(days=60),
                'is_featured': True
            },
            {
                'title': 'Healthcare Predictive Analytics',
                'client_name': 'MediCare Systems',
                'industry': 'Healthcare',
                'description': 'Predictive analytics solution for healthcare outcomes',
                'challenge': 'Inefficient patient risk assessment and resource allocation',
                'solution': 'Developed ML models for early disease detection and patient outcome prediction',
                'results': '40% reduction in readmission rates, 25% improvement in resource utilization',
                'technologies_used': ['Python', 'Scikit-learn', 'Apache Spark', 'MongoDB'],
                'completion_date': timezone.now().date() - timezone.timedelta(days=90),
                'is_featured': True
            },
            {
                'title': 'Financial Fraud Detection',
                'client_name': 'SecureBank',
                'industry': 'Finance',
                'description': 'Real-time fraud detection system for banking',
                'challenge': 'Increasing sophisticated fraud attempts requiring real-time detection',
                'solution': 'Built an ensemble model combining multiple ML algorithms for fraud detection',
                'results': '95% fraud detection accuracy, 60% reduction in false positives',
                'technologies_used': ['Python', 'XGBoost', 'Kafka', 'Elasticsearch'],
                'completion_date': timezone.now().date() - timezone.timedelta(days=120),
                'is_featured': False
            }
        ]
        
        for solution_data in solutions_data:
            solution, created = PastSolution.objects.get_or_create(
                title=solution_data['title'],
                defaults=solution_data
            )
            if created:
                self.stdout.write(f'✓ Created Past Solution: {solution.title}')
        
        # Create Events
        events_data = [
            {
                'title': 'AI in Business Summit 2024',
                'description': 'Join industry leaders to explore the latest AI trends and business applications.',
                'event_type': 'conference',
                'start_date': timezone.now() + timezone.timedelta(days=30),
                'end_date': timezone.now() + timezone.timedelta(days=32),
                'location': 'Tech Convention Center, Downtown',
                'max_participants': 500,
                'is_featured': True
            },
            {
                'title': 'Machine Learning Workshop',
                'description': 'Hands-on workshop covering practical ML implementation strategies.',
                'event_type': 'workshop',
                'start_date': timezone.now() + timezone.timedelta(days=14),
                'end_date': timezone.now() + timezone.timedelta(days=14),
                'location': 'AI Solution Hub Office',
                'max_participants': 25,
                'is_featured': False
            },
            {
                'title': 'AI Ethics Roundtable',
                'description': 'Discussion on responsible AI development and ethical considerations.',
                'event_type': 'meetup',
                'start_date': timezone.now() + timezone.timedelta(days=7),
                'end_date': timezone.now() + timezone.timedelta(days=7),
                'location': 'Virtual Event',
                'max_participants': 100,
                'is_featured': False
            }
        ]
        
        for event_data in events_data:
            event, created = Event.objects.get_or_create(
                title=event_data['title'],
                defaults=event_data
            )
            if created:
                self.stdout.write(f'✓ Created Event: {event.title}')
        
        # Create Testimonials
        testimonials_data = [
            {
                'customer_name': 'Sarah Johnson',
                'company': 'TechRetail Inc.',
                'job_title': 'CTO',
                'rating': 5,
                'review': 'The AI recommendation engine transformed our business. Our conversion rates increased dramatically, and customers love the personalized experience.',
                'is_featured': True
            },
            {
                'customer_name': 'Dr. Michael Chen',
                'company': 'MediCare Systems',
                'job_title': 'Chief Medical Officer',
                'rating': 5,
                'review': 'The predictive analytics solution has revolutionized our patient care. We can now identify high-risk patients early and provide proactive care.',
                'is_featured': True
            },
            {
                'customer_name': 'Lisa Rodriguez',
                'company': 'SecureBank',
                'job_title': 'Head of Risk Management',
                'rating': 5,
                'review': 'The fraud detection system is incredibly accurate and has saved us millions in potential losses. The team was professional and delivered on time.',
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
                self.stdout.write(f'✓ Created Testimonial: {testimonial.customer_name}')
        
        # Create Articles
        articles_data = [
            {
                'title': 'The Future of AI in Business: 2024 Trends',
                'content': 'Artificial Intelligence continues to reshape the business landscape...',
                'excerpt': 'Explore the key AI trends that will dominate business in 2024 and beyond.',
                'slug': 'future-ai-business-2024-trends',
                'author': User.objects.first(),
                'category': 'ai_insights',
                'tags': ['AI', 'Business', 'Trends', '2024'],
                'is_featured': True,
                'is_published': True
            },
            {
                'title': 'Implementing Machine Learning: A Practical Guide',
                'content': 'Machine Learning implementation can seem daunting...',
                'excerpt': 'Step-by-step guide to successfully implementing ML in your organization.',
                'slug': 'implementing-machine-learning-practical-guide',
                'author': User.objects.first(),
                'category': 'implementation',
                'tags': ['Machine Learning', 'Implementation', 'Guide'],
                'is_featured': False,
                'is_published': True
            },
            {
                'title': 'AI Ethics: Building Responsible Technology',
                'content': 'As AI becomes more prevalent...',
                'excerpt': 'Understanding the importance of ethical AI development and implementation.',
                'slug': 'ai-ethics-building-responsible-technology',
                'author': User.objects.first(),
                'category': 'ethics',
                'tags': ['AI Ethics', 'Responsible AI', 'Technology'],
                'is_featured': False,
                'is_published': True
            }
        ]
        
        for article_data in articles_data:
            article, created = Article.objects.get_or_create(
                title=article_data['title'],
                defaults=article_data
            )
            if created:
                self.stdout.write(f'✓ Created Article: {article.title}')
        
        # Create Admin Dashboard
        if not AdminDashboard.objects.exists():
            dashboard = AdminDashboard.objects.create(
                dashboard_title="AI Solution Hub Dashboard",
                welcome_message="Welcome to your AI Solution Hub administration panel",
                quick_actions=[
                    'Add new contact inquiry',
                    'View performance analytics',
                    'Manage website content'
                ],
                chart_config={
                    'type': 'bar',
                    'data': {'labels': ['Jan', 'Feb', 'Mar'], 'datasets': [{'data': [65, 59, 80]}]}
                }
            )
            self.stdout.write(f'✓ Created Admin Dashboard: {dashboard.dashboard_title}')
        
        self.stdout.write(self.style.SUCCESS('Database seeding completed successfully!'))
