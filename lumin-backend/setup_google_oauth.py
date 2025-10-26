#!/usr/bin/env python
"""
Script to setup Google OAuth provider in Django Allauth.
This creates the SocialApp record needed for Google login.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp
from django.conf import settings

# Get the current site
site = Site.objects.get_current()
print(f"[OK] Current site: {site.domain}")

# Create or update Google Social App
google_app, created = SocialApp.objects.get_or_create(
    provider='google',
    defaults={
        'name': 'Google OAuth',
        'client_id': settings.SOCIALACCOUNT_PROVIDERS['google']['APP']['client_id'],
        'secret': settings.SOCIALACCOUNT_PROVIDERS['google']['APP']['secret'],
    }
)

if not created:
    # Update existing app
    google_app.client_id = settings.SOCIALACCOUNT_PROVIDERS['google']['APP']['client_id']
    google_app.secret = settings.SOCIALACCOUNT_PROVIDERS['google']['APP']['secret']
    google_app.save()
    print(f"[OK] Updated existing Google OAuth app")
else:
    print(f"[OK] Created new Google OAuth app")

# Add site to the social app
if site not in google_app.sites.all():
    google_app.sites.add(site)
    print(f"[OK] Added site to Google OAuth app")

print("\n" + "="*60)
print("Google OAuth Setup Complete!")
print("="*60)
print(f"Provider: {google_app.provider}")
print(f"Client ID: {google_app.client_id[:20]}...")
print(f"Sites: {', '.join([s.domain for s in google_app.sites.all()])}")
print("="*60)
print("\nYou can now use Google OAuth at:")
print("  Login URL: http://localhost:8000/accounts/login/")
print("  Google Login: http://localhost:8000/accounts/google/login/")
print("="*60)
