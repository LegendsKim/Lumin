from django.contrib import admin
from .models import WooCommerceConnection, SyncJob, SyncLog, Coupon, WebhookEvent


@admin.register(WooCommerceConnection)
class WooCommerceConnectionAdmin(admin.ModelAdmin):
    list_display = ['tenant', 'store_url', 'is_active', 'last_sync_at']
    list_filter = ['is_active', 'auto_sync_enabled']
    search_fields = ['tenant__business_name', 'store_url']


@admin.register(SyncJob)
class SyncJobAdmin(admin.ModelAdmin):
    list_display = ['tenant', 'job_type', 'direction', 'status', 'progress_percentage', 'created_at']
    list_filter = ['job_type', 'direction', 'status']
    search_fields = ['tenant__business_name', 'celery_task_id']
    readonly_fields = ['progress_percentage', 'duration_seconds']


@admin.register(SyncLog)
class SyncLogAdmin(admin.ModelAdmin):
    list_display = ['sync_job', 'level', 'message', 'created_at']
    list_filter = ['level']
    search_fields = ['message', 'item_id']


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ['code', 'tenant', 'discount_type', 'amount', 'usage_count', 'is_active', 'is_valid']
    list_filter = ['discount_type', 'is_active', 'sync_status']
    search_fields = ['code', 'description', 'tenant__business_name']
    readonly_fields = ['is_expired', 'is_valid']


@admin.register(WebhookEvent)
class WebhookEventAdmin(admin.ModelAdmin):
    list_display = ['tenant', 'event_type', 'resource_type', 'status', 'signature_verified', 'created_at']
    list_filter = ['event_type', 'resource_type', 'status', 'signature_verified']
    search_fields = ['tenant__business_name', 'resource_id']
