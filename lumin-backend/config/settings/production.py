"""
Production settings for Lumin SaaS (Render deployment).
"""
import os
from .base import *

# Database: MUST use PostgreSQL in production (Supabase / Render)
# No SQLite fallback — if DATABASE_URL is missing, Django will fail on startup.
# This is intentional to prevent accidental data loss.
if not os.environ.get('DATABASE_URL'):
    raise ValueError(
        'DATABASE_URL environment variable is required in production. '
        'Set it to your Supabase/PostgreSQL connection string.'
    )

# Cache - Use in-memory cache instead of Redis (free tier compatible)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'lumin-production-cache',
    }
}

# Sessions - Use database instead of Redis
SESSION_ENGINE = 'django.contrib.sessions.backends.db'

# Celery - Use database broker instead of Redis (free tier compatible)
REDIS_URL = env('REDIS_URL', default=None)
if REDIS_URL:
    # Use Redis for Celery if available
    CELERY_BROKER_URL = REDIS_URL
    CELERY_RESULT_BACKEND = REDIS_URL
else:
    # Fallback to database (slower but works without Redis)
    CELERY_BROKER_URL = 'django-db'
    CELERY_RESULT_BACKEND = 'django-db'

# Security
DEBUG = False

# Allowed Hosts - Support Render domains
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=[
    '.onrender.com',
    'localhost',
    '127.0.0.1',
])

# CSRF Trusted Origins
CSRF_TRUSTED_ORIGINS = env.list('CSRF_TRUSTED_ORIGINS', default=[
    'https://*.onrender.com',
])

# Security settings
SECURE_SSL_REDIRECT = env.bool('SECURE_SSL_REDIRECT', default=True)
SECURE_HSTS_SECONDS = env.int('SECURE_HSTS_SECONDS', default=31536000)
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Cookie security
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Email backend (SendGrid) - Optional
SENDGRID_API_KEY = env('SENDGRID_API_KEY', default=None)
if SENDGRID_API_KEY:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = 'smtp.sendgrid.net'
    EMAIL_PORT = 587
    EMAIL_USE_TLS = True
    EMAIL_HOST_USER = 'apikey'
    EMAIL_HOST_PASSWORD = SENDGRID_API_KEY
else:
    # Fallback to console backend for testing
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Logging - Less verbose for production
LOGGING['root']['level'] = 'WARNING'
LOGGING['loggers']['django']['level'] = 'WARNING'
LOGGING['loggers']['apps'] = {
    'handlers': ['console'],
    'level': 'INFO',
    'propagate': False,
}

# Static files
# S3 configuration is already handled in base.py based on USE_S3
# If USE_S3=False in production, Whitenoise will serve static files

# Force S3 usage in production (recommended)
if not USE_S3:
    # Fallback to Whitenoise if S3 is not configured
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ========== SECURITY HARDENING ==========

# Force a real SECRET_KEY in production
if SECRET_KEY == 'django-insecure-temp-key-change-in-production':
    raise ValueError(
        'You MUST set a unique SECRET_KEY environment variable in production. '
        'Generate one with: python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"'
    )

# Rate Limiting via DRF Throttling
REST_FRAMEWORK['DEFAULT_THROTTLE_CLASSES'] = [
    'rest_framework.throttling.AnonRateThrottle',
    'rest_framework.throttling.UserRateThrottle',
]
REST_FRAMEWORK['DEFAULT_THROTTLE_RATES'] = {
    'anon': '20/minute',     # Unauthenticated users
    'user': '200/minute',    # Authenticated users
}

# Content Security Policy
CSP_HEADER = (
    "default-src 'self'; "
    "script-src 'self' 'unsafe-inline'; "
    "style-src 'self' 'unsafe-inline'; "
    "img-src 'self' data: https:; "
    "font-src 'self'; "
    "connect-src 'self'; "
    "frame-ancestors 'none'; "
)

# Security headers
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'

# Prevent session fixation
SESSION_COOKIE_AGE = 1200  # 20 minutes
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# File upload limits (5MB max to prevent abuse)
DATA_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024  # 5MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024   # 5MB

