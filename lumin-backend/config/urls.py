"""
Lumin SaaS URL Configuration
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from apps.core.views import (
    home, api_root, splash_screen, dashboard, settings as settings_view,
    phone_verification, verify_code, business_basics, business_details, business_branding, onboarding_complete
)

urlpatterns = [
    # Home page
    path('', home, name='home'),

    # Splash screen and Dashboard
    path('splash/', splash_screen, name='splash'),
    path('dashboard/', dashboard, name='dashboard'),
    path('settings/', settings_view, name='settings'),

    # Onboarding flow (4 steps)
    path('onboarding/phone/', phone_verification, name='phone_verification'),
    path('onboarding/verify/', verify_code, name='verify_code'),
    path('onboarding/basics/', business_basics, name='business_basics'),
    path('onboarding/details/', business_details, name='business_details'),
    path('onboarding/branding/', business_branding, name='business_branding'),
    path('onboarding/complete/', onboarding_complete, name='onboarding_complete'),

    # Django Admin
    path('admin/', admin.site.urls),

    # Django Allauth (Google OAuth)
    path('accounts/', include('allauth.urls')),

    # API Root
    path('api/', api_root, name='api-root'),

    # API Routes
    path('api/auth/', include('apps.accounts.urls')),
    path('api/users/', include('apps.accounts.urls')),
    path('api/products/', include('apps.inventory.urls')),
    path('api/orders/', include('apps.sales.urls')),
    path('api/customers/', include('apps.customers.urls')),
    path('api/analytics/', include('apps.analytics.urls')),
    path('api/integrations/', include('apps.integrations.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

    # Django Debug Toolbar
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar
        urlpatterns = [path('__debug__/', include(debug_toolbar.urls))] + urlpatterns

# Admin site customization
admin.site.site_header = 'Lumin - האור של העסק שלך'
admin.site.site_title = 'Lumin Admin'
admin.site.index_title = 'ניהול מערכת'
