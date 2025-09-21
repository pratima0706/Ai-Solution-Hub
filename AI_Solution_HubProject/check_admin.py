#!/usr/bin/env python
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AI_Solution_HubProject.settings')
django.setup()

from django.contrib.auth.models import User

print("=== Admin Users ===")
admin_users = User.objects.filter(is_superuser=True)
if admin_users:
    for user in admin_users:
        print(f"Username: {user.username}")
        print(f"Email: {user.email}")
        print(f"Is superuser: {user.is_superuser}")
        print("---")
else:
    print("No admin users found!")
    print("You need to create a superuser using:")
    print("python manage.py createsuperuser")
