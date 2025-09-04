from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType
from Ai_SolutionApp.models import UserRole, UserProfile

class Command(BaseCommand):
    help = 'Setup default admin roles and create super admin user'

    def handle(self, *args, **options):
        # Create default roles
        roles_data = [
            {
                'name': 'superadmin',
                'description': 'Full system access with all permissions'
            },
            {
                'name': 'admin',
                'description': 'Administrative access to all modules'
            },
            {
                'name': 'content_manager',
                'description': 'Manage content, articles, and testimonials'
            },
            {
                'name': 'events_manager',
                'description': 'Manage events and gallery'
            },
            {
                'name': 'support_agent',
                'description': 'Handle customer inquiries and support'
            },
            {
                'name': 'analyst',
                'description': 'View reports and analytics (read-only)'
            }
        ]
        
        for role_data in roles_data:
            role, created = UserRole.objects.get_or_create(
                name=role_data['name'],
                defaults={'description': role_data['description']}
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Created role: {role.get_name_display()}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Role already exists: {role.get_name_display()}')
                )
        
        # Create super admin user if it doesn't exist
        superadmin_username = 'admin'
        if not User.objects.filter(username=superadmin_username).exists():
            superadmin = User.objects.create_superuser(
                username=superadmin_username,
                email='admin@aisolutionhub.com',
                password='admin123',
                first_name='Super',
                last_name='Admin'
            )
            
            # Create profile for super admin
            superadmin_role = UserRole.objects.get(name='superadmin')
            UserProfile.objects.create(
                user=superadmin,
                role=superadmin_role,
                department='Administration',
                is_active=True
            )
            
            self.stdout.write(
                self.style.SUCCESS(f'Created super admin user: {superadmin_username}')
            )
            self.stdout.write(
                self.style.WARNING('Default password: admin123 - Please change this!')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'Super admin user already exists: {superadmin_username}')
            )
        
        self.stdout.write(
            self.style.SUCCESS('Admin roles setup completed successfully!')
        )
