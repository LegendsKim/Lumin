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
        Token.objects.create(user=instance)
