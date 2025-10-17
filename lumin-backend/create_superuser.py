#!/usr/bin/env python
"""
Script to create a Django superuser non-interactively.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.accounts.models import User

# Create superuser if it doesn't exist
email = 'admin@lumin.app'
password = 'admin123'

if not User.objects.filter(email=email).exists():
    user = User(
        email=email,
        is_staff=True,
        is_superuser=True,
        is_active=True,
        role='ADMIN',
        first_name='Admin',
        last_name='User'
    )
    user.set_password(password)
    user.save()
    print(f'✅ Superuser created successfully!')
    print(f'   Email: {email}')
    print(f'   Password: {password}')
    print(f'   You can login at: http://localhost:8000/admin')
else:
    print(f'⚠️  Superuser with email {email} already exists')
