"""
Production settings for Lumin SaaS (Render deployment).
"""
from .base import *

# Force SQLite for initial deployment test
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

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
