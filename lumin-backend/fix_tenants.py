"""Script to assign tenants to users without one."""
import os
import sys
import django

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.accounts.models import User, Tenant

# Find users without tenant
users_without_tenant = User.objects.filter(tenant__isnull=True)

print(f'Found {users_without_tenant.count()} users without tenant')

for user in users_without_tenant:
    # Create a tenant for this user
    tenant = Tenant.objects.create(
        business_name=f"{user.first_name} {user.last_name}'s Business",
        owner_email=user.email,
        owner_phone=user.phone if hasattr(user, 'phone') and user.phone else '+972500000000',
        plan='BASIC'
    )

    # Assign tenant to user
    user.tenant = tenant
    user.save()

    print(f'✅ Created tenant "{tenant.business_name}" for user {user.email}')

print(f'\n✅ Successfully assigned tenants to {users_without_tenant.count()} users')
