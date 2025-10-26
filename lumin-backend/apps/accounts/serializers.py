# -*- coding: utf-8 -*-
"""
Serializers for accounts app.
"""
from rest_framework import serializers
from .models import Tenant, User


class PlanFeaturesSerializer(serializers.Serializer):
    """
    Serializer for plan features and limits.

    Returns all information needed by frontend to:
    1. Show/hide features based on plan
    2. Display current usage vs limits
    3. Show locked status and upgrade prompts
    """

    # Plan info
    plan = serializers.CharField(source='tenant.plan')
    account_status = serializers.CharField(source='tenant.account_status')
    is_locked = serializers.SerializerMethodField()

    # Limits
    limits = serializers.SerializerMethodField()

    # Current counts
    current = serializers.SerializerMethodField()

    # Features availability
    features = serializers.SerializerMethodField()

    # Can add more resources
    can_add = serializers.SerializerMethodField()

    def get_is_locked(self, obj):
        """Check if account is locked."""
        return obj.tenant.is_locked()

    def get_limits(self, obj):
        """Get all plan limits."""
        tenant = obj.tenant
        return {
            'max_customers': tenant.max_customers if tenant.max_customers != float('inf') else None,
            'max_products': tenant.max_products if tenant.max_products != float('inf') else None,
            'max_staff_members': tenant.max_staff_members if tenant.max_staff_members != float('inf') else None,
            'max_s3_storage_mb': tenant.max_s3_storage_mb if tenant.max_s3_storage_mb != float('inf') else None,
        }

    def get_current(self, obj):
        """Get current resource counts."""
        return obj.tenant.get_current_counts()

    def get_features(self, obj):
        """Get feature availability."""
        tenant = obj.tenant
        return {
            'woocommerce_full_sync': tenant.can_use_woocommerce_full_sync(),
            'woocommerce_basic_import': True,  # Available to all
            'sms_marketing': tenant.can_send_sms_marketing(),
            'sms_verification': True,  # Available to all
            's3_uploads': True,  # Available to all (with size limits)
            'unlimited_customers': tenant.plan == 'PRO',
            'unlimited_products': tenant.plan == 'PRO',
            'unlimited_staff': tenant.plan == 'PRO',
            'unlimited_storage': tenant.plan == 'PRO',
        }

    def get_can_add(self, obj):
        """Check if can add more resources."""
        tenant = obj.tenant
        return {
            'customer': tenant.can_add_customer() and not tenant.is_locked(),
            'product': tenant.can_add_product() and not tenant.is_locked(),
            'staff_member': tenant.can_add_staff_member() and not tenant.is_locked(),
        }


class TenantSerializer(serializers.ModelSerializer):
    """Serializer for Tenant model."""

    class Meta:
        model = Tenant
        fields = [
            'id', 'business_name', 'owner_email', 'owner_phone',
            'phone_verified', 'logo', 'plan', 'account_status',
            'subscription_expires_at', 'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'account_status']


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model."""

    tenant = TenantSerializer(read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'phone',
            'phone_verified', 'role', 'tenant', 'is_active',
            'onboarding_completed', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
