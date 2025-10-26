"""
URL routing for integrations app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    WooCommerceConnectionViewSet,
    SyncJobViewSet,
    CouponViewSet,
    WebhookEventViewSet,
    sync_page,
    coupons_page,
)
from .webhooks import woocommerce_webhook

# Create router
router = DefaultRouter()
router.register(r'connections', WooCommerceConnectionViewSet, basename='woocommerce-connection')
router.register(r'sync-jobs', SyncJobViewSet, basename='sync-job')
router.register(r'coupons', CouponViewSet, basename='coupon')
router.register(r'webhooks', WebhookEventViewSet, basename='webhook')

urlpatterns = [
    # Page views
    path('sync/', sync_page, name='sync_page'),
    path('coupons/', coupons_page, name='coupons_page'),

    # Webhook endpoint
    path('webhook/woocommerce/', woocommerce_webhook, name='woocommerce_webhook'),

    # API endpoints
    path('api/', include(router.urls)),
]
