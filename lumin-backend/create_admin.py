#!/usr/bin/env python
"""
Script to create admin user and tenant.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.accounts.models import Tenant, User
from django.contrib.auth.hashers import make_password

# Create tenant first
print("Creating tenant...")
tenant, created = Tenant.objects.get_or_create(
    owner_email='owner@lumin.com',
    defaults={
        'business_name': 'Demo Company',
        'owner_phone': '+972501234567',
        'is_active': True,
        'plan': 'PRO'
    }
)
if created:
    print(f"[OK] Tenant created: {tenant.business_name}")
else:
    print(f"[OK] Tenant already exists: {tenant.business_name}")

# Create admin user
print("Creating admin user...")
user, created = User.objects.get_or_create(
    email='admin@lumin.com',
    defaults={
        'password': make_password('admin123'),
        'tenant': tenant,
        'first_name': 'Admin',
        'last_name': 'User',
        'is_staff': True,
        'is_superuser': True,
        'is_active': True,
        'role': 'ADMIN'
    }
)
if created:
    print(f"[OK] Admin user created: {user.email}")
else:
    print(f"[OK] Admin user already exists: {user.email}")

print("\n" + "="*50)
print("Login credentials:")
print("  Email: admin@lumin.com")
print("  Password: admin123")
print("="*50)
