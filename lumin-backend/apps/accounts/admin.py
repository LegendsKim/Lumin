"""
Django admin configuration for Accounts app.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import Tenant, User


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    """Admin interface for Tenant model."""

    list_display = [
        'business_name',
        'owner_email',
        'owner_phone',
        'plan',
        'phone_verified',
        'is_active',
        'created_at',
    ]

    list_filter = [
        'plan',
        'is_active',
        'phone_verified',
        'created_at',
    ]

    search_fields = [
        'business_name',
        'owner_email',
        'owner_phone',
    ]

    readonly_fields = [
        'id',
        'created_at',
        'updated_at',
        'stripe_customer_id',
    ]

    fieldsets = (
        (_('Business Information'), {
            'fields': ('business_name', 'logo', 'owner_email', 'owner_phone')
        }),
        (_('Verification'), {
            'fields': ('phone_verified',)
        }),
        (_('Subscription'), {
            'fields': ('plan', 'stripe_customer_id', 'subscription_expires_at')
        }),
        (_('Status'), {
            'fields': ('is_active',)
        }),
        (_('Metadata'), {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        qs = super().get_queryset(request)
        return qs.select_related()


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin interface for User model."""

    list_display = [
        'email',
        'first_name',
        'last_name',
        'tenant',
        'role',
        'is_active',
        'phone_verified',
        'last_login',
    ]

    list_filter = [
        'role',
        'is_active',
        'is_staff',
        'phone_verified',
        'created_at',
    ]

    search_fields = [
        'email',
        'first_name',
        'last_name',
        'phone',
        'tenant__business_name',
    ]

    readonly_fields = [
        'id',
        'created_at',
        'updated_at',
        'last_login',
        'date_joined',
        'google_sub',
    ]

    fieldsets = (
        (_('Login Information'), {
            'fields': ('email', 'password')
        }),
        (_('Personal Information'), {
            'fields': ('first_name', 'last_name', 'phone', 'phone_verified')
        }),
        (_('Tenant & Role'), {
            'fields': ('tenant', 'role')
        }),
        (_('OAuth'), {
            'fields': ('google_sub',),
            'classes': ('collapse',)
        }),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'classes': ('collapse',)
        }),
        (_('Important Dates'), {
            'fields': ('last_login', 'date_joined', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
        (_('Metadata'), {
            'fields': ('id',),
            'classes': ('collapse',)
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'tenant', 'role'),
        }),
    )

    ordering = ['-created_at']
    filter_horizontal = ('groups', 'user_permissions')

    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        qs = super().get_queryset(request)
        return qs.select_related('tenant')
