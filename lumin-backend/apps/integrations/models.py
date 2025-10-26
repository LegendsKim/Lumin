"""
Integration models for WooCommerce sync and coupons management.
"""
import uuid
from django.db import models
from django.utils import timezone
from apps.core.models import BaseModel
from apps.accounts.models import Tenant, User


class WooCommerceConnection(BaseModel):
    """
    Stores WooCommerce connection settings per tenant.
    Each tenant can have one WooCommerce store connection.
    """
    tenant = models.OneToOneField(
        Tenant,
        on_delete=models.CASCADE,
        related_name='woocommerce_connection'
    )

    store_url = models.URLField(
        max_length=500,
        help_text='WooCommerce store URL (e.g., https://example.com)'
    )

    consumer_key = models.CharField(
        max_length=255,
        help_text='WooCommerce REST API Consumer Key'
    )

    consumer_secret = models.CharField(
        max_length=255,
        help_text='WooCommerce REST API Consumer Secret'
    )

    webhook_secret = models.CharField(
        max_length=255,
        blank=True,
        help_text='Secret for verifying webhook signatures'
    )

    is_active = models.BooleanField(
        default=False,
        help_text='Whether this connection is active'
    )

    last_sync_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Last successful sync timestamp'
    )

    sync_customers = models.BooleanField(default=True)
    sync_orders = models.BooleanField(default=True)
    sync_products = models.BooleanField(default=True)
    sync_coupons = models.BooleanField(default=True)

    # Auto-sync settings
    auto_sync_enabled = models.BooleanField(
        default=False,
        help_text='Enable automatic periodic sync'
    )

    sync_interval_minutes = models.IntegerField(
        default=60,
        help_text='Sync interval in minutes (if auto-sync enabled)'
    )

    class Meta:
        db_table = 'integrations_woocommerce_connection'
        verbose_name = 'WooCommerce Connection'
        verbose_name_plural = 'WooCommerce Connections'

    def __str__(self):
        return f'{self.tenant.business_name} - {self.store_url}'


class SyncJob(BaseModel):
    """
    Tracks individual sync jobs.
    Used for monitoring, queue management, and history.
    """

    JOB_TYPE_CHOICES = [
        ('customers', 'Customers'),
        ('orders', 'Orders'),
        ('products', 'Products'),
        ('coupons', 'Coupons'),
    ]

    DIRECTION_CHOICES = [
        ('import', 'Import from WooCommerce'),
        ('export', 'Export to WooCommerce'),
        ('bidirectional', 'Bi-directional Sync'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]

    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name='sync_jobs'
    )

    job_type = models.CharField(
        max_length=50,
        choices=JOB_TYPE_CHOICES
    )

    direction = models.CharField(
        max_length=20,
        choices=DIRECTION_CHOICES,
        default='import'
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    total_items = models.IntegerField(default=0)
    processed_items = models.IntegerField(default=0)
    successful_items = models.IntegerField(default=0)
    failed_items = models.IntegerField(default=0)

    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    error_message = models.TextField(blank=True)
    error_details = models.JSONField(default=dict, blank=True)

    # Celery task ID for tracking
    celery_task_id = models.CharField(max_length=255, blank=True)

    # User who initiated the sync
    initiated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='initiated_sync_jobs'
    )

    class Meta:
        db_table = 'integrations_sync_job'
        verbose_name = 'Sync Job'
        verbose_name_plural = 'Sync Jobs'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.job_type} - {self.status} ({self.tenant.business_name})'

    @property
    def progress_percentage(self):
        """Calculate progress percentage."""
        if self.total_items == 0:
            return 0
        return int((self.processed_items / self.total_items) * 100)

    @property
    def duration_seconds(self):
        """Calculate job duration in seconds."""
        if not self.started_at:
            return None
        end_time = self.completed_at or timezone.now()
        return (end_time - self.started_at).total_seconds()


class SyncLog(BaseModel):
    """
    Detailed log entries for sync operations.
    Stores individual item sync results.
    """

    LEVEL_CHOICES = [
        ('info', 'Info'),
        ('warning', 'Warning'),
        ('error', 'Error'),
    ]

    sync_job = models.ForeignKey(
        SyncJob,
        on_delete=models.CASCADE,
        related_name='logs'
    )

    level = models.CharField(
        max_length=20,
        choices=LEVEL_CHOICES,
        default='info'
    )

    message = models.TextField()

    item_id = models.CharField(
        max_length=255,
        blank=True,
        help_text='WooCommerce or local item ID'
    )

    details = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = 'integrations_sync_log'
        verbose_name = 'Sync Log'
        verbose_name_plural = 'Sync Logs'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.level.upper()}: {self.message[:50]}'


class Coupon(BaseModel):
    """
    Coupon model with WooCommerce integration.
    Supports bi-directional sync with WooCommerce.
    """

    DISCOUNT_TYPE_CHOICES = [
        ('percent', 'Percentage Discount'),
        ('fixed_cart', 'Fixed Cart Discount'),
        ('fixed_product', 'Fixed Product Discount'),
    ]

    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name='coupons'
    )

    # Basic coupon info
    code = models.CharField(
        max_length=100,
        help_text='Coupon code (unique per tenant)'
    )

    description = models.TextField(
        blank=True,
        help_text='Internal description of the coupon'
    )

    discount_type = models.CharField(
        max_length=20,
        choices=DISCOUNT_TYPE_CHOICES,
        default='percent'
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text='Discount amount (percentage or fixed)'
    )

    # Restrictions
    minimum_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Minimum cart amount required'
    )

    maximum_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Maximum cart amount allowed'
    )

    individual_use = models.BooleanField(
        default=False,
        help_text='Cannot be used with other coupons'
    )

    exclude_sale_items = models.BooleanField(
        default=False,
        help_text='Exclude items on sale'
    )

    # Usage limits
    usage_limit = models.IntegerField(
        null=True,
        blank=True,
        help_text='Maximum number of times coupon can be used'
    )

    usage_limit_per_user = models.IntegerField(
        null=True,
        blank=True,
        help_text='Maximum uses per customer'
    )

    usage_count = models.IntegerField(
        default=0,
        help_text='Number of times used'
    )

    # Date restrictions
    date_expires = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Coupon expiration date'
    )

    # Product/category restrictions
    product_ids = models.JSONField(
        default=list,
        blank=True,
        help_text='WooCommerce product IDs this coupon applies to'
    )

    excluded_product_ids = models.JSONField(
        default=list,
        blank=True,
        help_text='WooCommerce product IDs excluded from coupon'
    )

    product_categories = models.JSONField(
        default=list,
        blank=True,
        help_text='Category IDs this coupon applies to'
    )

    excluded_product_categories = models.JSONField(
        default=list,
        blank=True,
        help_text='Category IDs excluded from coupon'
    )

    # Email restrictions
    email_restrictions = models.JSONField(
        default=list,
        blank=True,
        help_text='Email addresses that can use this coupon'
    )

    # WooCommerce sync
    woocommerce_coupon_id = models.IntegerField(
        null=True,
        blank=True,
        help_text='WooCommerce coupon ID'
    )

    last_synced_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Last sync with WooCommerce'
    )

    sync_status = models.CharField(
        max_length=20,
        choices=[
            ('synced', 'Synced'),
            ('pending', 'Pending Sync'),
            ('error', 'Sync Error'),
            ('not_synced', 'Not Synced'),
        ],
        default='not_synced'
    )

    is_active = models.BooleanField(
        default=True,
        help_text='Whether coupon is active'
    )

    class Meta:
        db_table = 'integrations_coupon'
        verbose_name = 'Coupon'
        verbose_name_plural = 'Coupons'
        unique_together = [['tenant', 'code']]
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.code} ({self.discount_type})'

    @property
    def is_expired(self):
        """Check if coupon is expired."""
        if not self.date_expires:
            return False
        return timezone.now() > self.date_expires

    @property
    def is_valid(self):
        """Check if coupon is valid for use."""
        if not self.is_active:
            return False
        if self.is_expired:
            return False
        if self.usage_limit and self.usage_count >= self.usage_limit:
            return False
        return True


class WebhookEvent(BaseModel):
    """
    Stores incoming webhook events from WooCommerce.
    Used for real-time sync and audit trail.
    """

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('processed', 'Processed'),
        ('failed', 'Failed'),
        ('ignored', 'Ignored'),
    ]

    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name='webhook_events'
    )

    event_type = models.CharField(
        max_length=100,
        help_text='WooCommerce event type (e.g., customer.created)'
    )

    resource_type = models.CharField(
        max_length=50,
        help_text='Resource type (customer, order, product, coupon)'
    )

    resource_id = models.CharField(
        max_length=100,
        help_text='WooCommerce resource ID'
    )

    payload = models.JSONField(
        default=dict,
        help_text='Full webhook payload'
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    processed_at = models.DateTimeField(null=True, blank=True)

    error_message = models.TextField(blank=True)

    # Signature verification
    signature = models.CharField(max_length=255, blank=True)
    signature_verified = models.BooleanField(default=False)

    class Meta:
        db_table = 'integrations_webhook_event'
        verbose_name = 'Webhook Event'
        verbose_name_plural = 'Webhook Events'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.event_type} - {self.status}'
