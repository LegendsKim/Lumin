"""
Development settings for Lumin SaaS.
"""
from .base import *

# Debug mode
DEBUG = True

# Allowed hosts for development
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']

# CORS for development
CORS_ALLOWED_ORIGINS = [
    'http://localhost:5173',
    'http://localhost:3000',
    'http://127.0.0.1:5173',
    'http://127.0.0.1:3000',
]

# Django Debug Toolbar
INSTALLED_APPS += ['debug_toolbar']
MIDDLEWARE.insert(0, 'debug_toolbar.middleware.DebugToolbarMiddleware')
INTERNAL_IPS = ['127.0.0.1']

# Disable HTTPS requirements
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_SSL_REDIRECT = False

# Email backend (console for development)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Disable Redis for development - use memory cache instead
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# Use database sessions instead of Redis
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_CACHE_ALIAS = 'default'

# Logging - More verbose for development
LOGGING['root']['level'] = 'DEBUG'
LOGGING['loggers']['django']['level'] = 'DEBUG'
