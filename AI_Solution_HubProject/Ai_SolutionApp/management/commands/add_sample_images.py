from django.core.management.base import BaseCommand
from django.core.files import File
from Ai_SolutionApp.models import Gallery
import os
from django.conf import settings

class Command(BaseCommand):
    help = 'Add sample gallery images for testing'

    def handle(self, *args, **options):
        # Create sample gallery entries
        sample_images = [
            {
                'title': 'AI Brain Visualization',
                'description': 'Advanced AI neural network visualization showing complex data processing',
                'category': 'ai_solutions',
                'is_featured': True,
                'is_hero_image': True,
                'tags': ['ai', 'neural-network', 'visualization']
            },
            {
                'title': 'Team Collaboration',
                'description': 'Our AI team working together on innovative solutions',
                'category': 'team_events',
                'is_featured': True,
                'tags': ['team', 'collaboration', 'innovation']
            },
            {
                'title': 'AI Dashboard Interface',
                'description': 'Professional AI analytics dashboard for business intelligence',
                'category': 'ai_solutions',
                'is_featured': True,
                'tags': ['dashboard', 'analytics', 'business-intelligence']
            },
            {
                'title': 'Conference Presentation',
                'description': 'Presenting AI solutions at international tech conference',
                'category': 'conferences',
                'is_featured': True,
                'tags': ['conference', 'presentation', 'tech']
            },
            {
                'title': 'Data Science Workshop',
                'description': 'Hands-on machine learning workshop for professionals',
                'category': 'workshops',
                'is_featured': True,
                'tags': ['workshop', 'machine-learning', 'education']
            },
            {
                'title': 'Client Meeting',
                'description': 'Strategic AI consultation with enterprise clients',
                'category': 'client_meetings',
                'is_featured': True,
                'tags': ['client', 'consultation', 'enterprise']
            },
            {
                'title': 'AI Product Demo',
                'description': 'Demonstrating cutting-edge AI product capabilities',
                'category': 'product_demos',
                'is_featured': True,
                'tags': ['demo', 'product', 'innovation']
            },
            {
                'title': 'Research Laboratory',
                'description': 'State-of-the-art AI research and development facility',
                'category': 'research',
                'is_featured': True,
                'tags': ['research', 'laboratory', 'development']
            }
        ]

        # Check if we already have images
        if Gallery.objects.exists():
            self.stdout.write(
                self.style.WARNING('Gallery images already exist. Skipping...')
            )
            return

        # Create gallery entries
        for i, img_data in enumerate(sample_images):
            gallery = Gallery.objects.create(
                title=img_data['title'],
                description=img_data['description'],
                category=img_data['category'],
                is_featured=img_data['is_featured'],
                is_hero_image=img_data.get('is_hero_image', False),
                tags=img_data['tags'],
                order=i
            )
            
            # Use the existing k3-picaai.png as a placeholder
            existing_image_path = os.path.join(settings.MEDIA_ROOT, 'gallery', 'k3-picaai.png')
            if os.path.exists(existing_image_path):
                with open(existing_image_path, 'rb') as f:
                    gallery.image.save(f'gallery_image_{i+1}.png', File(f), save=True)
            
            self.stdout.write(
                self.style.SUCCESS(f'Created gallery image: {gallery.title}')
            )

        self.stdout.write(
            self.style.SUCCESS('Successfully created sample gallery images!')
        )
