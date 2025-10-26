"""
Social account signals for Google OAuth integration.
"""
from django.dispatch import receiver
from allauth.socialaccount.signals import social_account_added
from .models import Tenant


@receiver(social_account_added)
def create_tenant_for_social_user(request, sociallogin, **kwargs):
    """
    Automatically create a Tenant when user signs up via Google OAuth.

    This ensures every Google OAuth user gets their own tenant/business
    and is set as the ADMIN of that business.

    Args:
        request: The HTTP request
        sociallogin: The social login instance containing user and social account info
        kwargs: Additional arguments
    """
    user = sociallogin.user

    # Only create tenant if user doesn't have one
    if not user.tenant:
        # Extract business name from email (e.g., john@example.com -> "John Business")
        email_parts = user.email.split('@')
        business_name = email_parts[0].capitalize() + ' Business'

        # Create tenant for the new user
        tenant = Tenant.objects.create(
            business_name=business_name,
            owner_email=user.email,
            owner_phone='+972500000000',  # Default, user can update later
            plan='BASIC',  # Start with basic plan
            is_active=True
        )

        # Assign tenant to user and make them admin
        user.tenant = tenant
        user.role = 'ADMIN'  # Google OAuth users become admins of their business
        user.save()

        print(f"[OAuth] Created tenant '{tenant.business_name}' for user {user.email}")
