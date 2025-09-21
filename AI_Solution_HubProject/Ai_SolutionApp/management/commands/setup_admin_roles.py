from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Permission, Group
from django.contrib.contenttypes.models import ContentType
from Ai_SolutionApp.models import UserRole, UserProfile, Contact, NewsletterSubscriber

class Command(BaseCommand):
    help = 'Setup default admin roles and create super admin user'

    def handle(self, *args, **options):
        # Create Django Groups with least-privilege permissions
        groups = {
            'Owner': [],
            'StaffAdmin': [],
            'ContentEditor': [],
            'Analyst': [],
            'Sales': [],
            'AccessManager': [],
        }
        for name in groups.keys():
            Group.objects.get_or_create(name=name)

        # Ensure custom export permission exists (from Contact.Meta.permissions)
        ct_contact = ContentType.objects.get_for_model(Contact)
        export_perm, _ = Permission.objects.get_or_create(
            codename='export_contact',
            name='Can export contact inquiries',
            content_type=ct_contact,
        )

        # Assemble perms
        perms = {
            'view_contact': Permission.objects.get(codename='view_contact', content_type=ct_contact),
            'change_contact': Permission.objects.get(codename='change_contact', content_type=ct_contact),
            'delete_contact': Permission.objects.get(codename='delete_contact', content_type=ct_contact),
            'export_contact': export_perm,
        }
        ct_sub = ContentType.objects.get_for_model(NewsletterSubscriber)
        sub_perms = {
            'view_subscriber': Permission.objects.get(codename='view_newslettersubscriber', content_type=ct_sub),
            'change_subscriber': Permission.objects.get(codename='change_newslettersubscriber', content_type=ct_sub),
        }

        # Assign least privilege
        def add_perms(group_name, perm_list):
            g = Group.objects.get(name=group_name)
            for p in perm_list:
                g.permissions.add(p)

        # Owner: view/export inquiries, manage content; no superuser
        add_perms('Owner', [perms['view_contact'], perms['export_contact'], sub_perms['view_subscriber']])
        # StaffAdmin: full inquiry workflow + export
        add_perms('StaffAdmin', [perms['view_contact'], perms['change_contact'], perms['delete_contact'], perms['export_contact']])
        # Analyst: read-only + export
        add_perms('Analyst', [perms['view_contact'], perms['export_contact'], sub_perms['view_subscriber']])
        # Sales: read-only inquiries
        add_perms('Sales', [perms['view_contact']])
        # ContentEditor: content perms would be added for content models later
        # AccessManager: will manage invitations via custom views (no broad perms here)

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
