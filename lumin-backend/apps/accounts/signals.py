"""
Signals for account-related events.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token

User = get_user_model()


@receiver(post_save, sender=User)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    """
    Automatically create authentication token when user is created.

    Args:
        sender: User model class
        instance: User instance
        created: Whether this is a new user
        kwargs: Additional arguments
    """
    if created:
        # Create auth token
        Token.objects.create(user=instance)

        # Create Tenant if not exists (handling generic signups)
        # This replaces the logic that was previously in TenantMiddleware
        if not instance.tenant:
            from .models import Tenant
            
            # Extract basic info
            email = instance.email
            name = f"{instance.first_name} {instance.last_name}".strip()
            if not name:
                name = email.split('@')[0]
            
            business_name = f"{name}'s Business"
            
            # Create tenant
            try:
                tenant = Tenant.objects.create(
                    business_name=business_name,
                    owner_email=email,
                    owner_phone=instance.phone or '+972500000000',
                    plan='BASIC',
                    is_active=True
                )
                
                # Assign to user and set as ADMIN
                instance.tenant = tenant
                instance.role = 'ADMIN'
                instance.save(update_fields=['tenant', 'role'])
                
                print(f"[Signal] Created tenant '{tenant.business_name}' for user {email}")
            except Exception as e:
                print(f"Error creating tenant for user {email}: {e}")
