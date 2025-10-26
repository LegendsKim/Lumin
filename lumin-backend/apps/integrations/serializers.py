"""
Serializers for integrations app.
"""
from rest_framework import serializers
from django.utils import timezone
from .models import (
    WooCommerceConnection,
    SyncJob,
    SyncLog,
    Coupon,
    WebhookEvent
)


class WooCommerceConnectionSerializer(serializers.ModelSerializer):
    """Serializer for WooCommerce connection settings."""

    class Meta:
        model = WooCommerceConnection
        fields = [
            'id',
            'store_url',
            'consumer_key',
            'consumer_secret',
            'webhook_secret',
            'is_active',
            'last_sync_at',
            'sync_customers',
            'sync_orders',
            'sync_products',
            'sync_coupons',
            'auto_sync_enabled',
            'sync_interval_minutes',
            'created_at',
            'updated_at',
        ]
        extra_kwargs = {
            'consumer_secret': {'write_only': True},
            'webhook_secret': {'write_only': True},
        }

    def validate_store_url(self, value):
        """Validate store URL format."""
        if not value.startswith(('http://', 'https://')):
            raise serializers.ValidationError('כתובת האתר חייבת להתחיל ב-http:// או https://')
        return value.rstrip('/')


class SyncLogSerializer(serializers.ModelSerializer):
    """Serializer for sync log entries."""

    class Meta:
        model = SyncLog
        fields = [
            'id',
            'level',
            'message',
            'item_id',
            'details',
            'created_at',
        ]


class SyncJobSerializer(serializers.ModelSerializer):
    """Serializer for sync jobs."""

    progress_percentage = serializers.IntegerField(read_only=True)
    duration_seconds = serializers.FloatField(read_only=True)
    logs = SyncLogSerializer(many=True, read_only=True)

    class Meta:
        model = SyncJob
        fields = [
            'id',
            'job_type',
            'direction',
            'status',
            'total_items',
            'processed_items',
            'successful_items',
            'failed_items',
            'progress_percentage',
            'duration_seconds',
            'started_at',
            'completed_at',
            'error_message',
            'error_details',
            'celery_task_id',
            'logs',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'status',
            'total_items',
            'processed_items',
            'successful_items',
            'failed_items',
            'started_at',
            'completed_at',
            'error_message',
            'error_details',
            'celery_task_id',
        ]


class SyncJobCreateSerializer(serializers.Serializer):
    """Serializer for creating sync jobs."""

    job_type = serializers.ChoiceField(
        choices=['customers', 'orders', 'products', 'coupons']
    )
    direction = serializers.ChoiceField(
        choices=['import', 'export', 'bidirectional'],
        default='import'
    )


class CouponSerializer(serializers.ModelSerializer):
    """Serializer for coupons."""

    is_expired = serializers.BooleanField(read_only=True)
    is_valid = serializers.BooleanField(read_only=True)

    class Meta:
        model = Coupon
        fields = [
            'id',
            'code',
            'description',
            'discount_type',
            'amount',
            'minimum_amount',
            'maximum_amount',
            'individual_use',
            'exclude_sale_items',
            'usage_limit',
            'usage_limit_per_user',
            'usage_count',
            'date_expires',
            'product_ids',
            'excluded_product_ids',
            'product_categories',
            'excluded_product_categories',
            'email_restrictions',
            'woocommerce_coupon_id',
            'last_synced_at',
            'sync_status',
            'is_active',
            'is_expired',
            'is_valid',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'usage_count',
            'woocommerce_coupon_id',
            'last_synced_at',
            'sync_status',
        ]

    def validate_code(self, value):
        """Validate coupon code."""
        # Convert to uppercase and remove spaces
        value = value.upper().replace(' ', '')

        # Check if code already exists for this tenant
        tenant = self.context['request'].user.tenant
        if self.instance:
            # Updating existing coupon
            if Coupon.objects.filter(
                tenant=tenant,
                code=value
            ).exclude(id=self.instance.id).exists():
                raise serializers.ValidationError('קוד קופון זה כבר קיים')
        else:
            # Creating new coupon
            if Coupon.objects.filter(tenant=tenant, code=value).exists():
                raise serializers.ValidationError('קוד קופון זה כבר קיים')

        return value

    def validate_amount(self, value):
        """Validate discount amount."""
        if value <= 0:
            raise serializers.ValidationError('סכום ההנחה חייב להיות חיובי')
        return value

    def validate(self, data):
        """Cross-field validation."""
        # If percentage discount, amount should not exceed 100
        if data.get('discount_type') == 'percent' and data.get('amount', 0) > 100:
            raise serializers.ValidationError({
                'amount': 'אחוז הנחה לא יכול לעבור 100%'
            })

        # Minimum amount should be less than maximum amount
        min_amount = data.get('minimum_amount')
        max_amount = data.get('maximum_amount')
        if min_amount and max_amount and min_amount > max_amount:
            raise serializers.ValidationError({
                'minimum_amount': 'סכום מינימום חייב להיות קטן מסכום מקסימום'
            })

        return data


class CouponListSerializer(serializers.ModelSerializer):
    """Simplified serializer for coupon list view."""

    is_expired = serializers.BooleanField(read_only=True)
    is_valid = serializers.BooleanField(read_only=True)

    class Meta:
        model = Coupon
        fields = [
            'id',
            'code',
            'description',
            'discount_type',
            'amount',
            'usage_count',
            'usage_limit',
            'date_expires',
            'is_active',
            'is_expired',
            'is_valid',
            'sync_status',
            'created_at',
        ]


class WebhookEventSerializer(serializers.ModelSerializer):
    """Serializer for webhook events."""

    class Meta:
        model = WebhookEvent
        fields = [
            'id',
            'event_type',
            'resource_type',
            'resource_id',
            'payload',
            'status',
            'processed_at',
            'error_message',
            'signature_verified',
            'created_at',
        ]
        read_only_fields = [
            'status',
            'processed_at',
            'error_message',
            'signature_verified',
        ]


class ConnectionTestSerializer(serializers.Serializer):
    """Serializer for testing WooCommerce connection."""

    store_url = serializers.URLField()
    consumer_key = serializers.CharField()
    consumer_secret = serializers.CharField()
