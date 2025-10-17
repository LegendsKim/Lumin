"""
Production settings for Lumin SaaS (Render deployment).
"""
from .base import *

# Security
DEBUG = False

# Security settings
SECURE_SSL_REDIRECT = env.bool('SECURE_SSL_REDIRECT', default=True)
SECURE_HSTS_SECONDS = env.int('SECURE_HSTS_SECONDS', default=31536000)
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Cookie security
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Email backend (SendGrid)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'apikey'
EMAIL_HOST_PASSWORD = env('SENDGRID_API_KEY')

# Logging - Less verbose for production
LOGGING['root']['level'] = 'WARNING'
LOGGING['loggers']['django']['level'] = 'WARNING'
LOGGING['loggers']['apps'] = {
    'handlers': ['console'],
    'level': 'INFO',
    'propagate': False,
}

# Static files - Use S3 in production if configured
if USE_S3:
    STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
