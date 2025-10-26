"""
Webhook handlers for WooCommerce events.
"""
import logging
import hashlib
import hmac
import json
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone

from .models import WebhookEvent, WooCommerceConnection, Coupon
from apps.customers.models import Customer

logger = logging.getLogger(__name__)


def verify_webhook_signature(request, webhook_secret):
    """Verify WooCommerce webhook signature."""
    signature = request.headers.get('X-WC-Webhook-Signature', '')

    if not signature or not webhook_secret:
        return False

    # Calculate expected signature
    body = request.body
    expected_signature = hmac.new(
        webhook_secret.encode('utf-8'),
        body,
        hashlib.sha256
    ).digest().hex()

    return hmac.compare_digest(signature, expected_signature)


@csrf_exempt
@require_http_methods(["POST"])
def woocommerce_webhook(request):
    """
    Universal webhook endpoint for all WooCommerce events.
    WooCommerce will send events to this endpoint.
    """
    try:
        # Parse payload
        payload = json.loads(request.body.decode('utf-8'))

        # Get event details from headers
        event_type = request.headers.get('X-WC-Webhook-Topic', '')
        resource_id = request.headers.get('X-WC-Webhook-Resource', '')

        # Extract tenant from store URL or webhook secret
        # For now, we'll match by store URL in the payload
        # You may need to adjust this based on your setup
        store_url = payload.get('_links', {}).get('self', [{}])[0].get('href', '')

        # Find connection by store URL
        connection = None
        for conn in WooCommerceConnection.objects.filter(is_active=True):
            if conn.store_url in store_url:
                connection = conn
                break

        if not connection:
            logger.warning(f"No active connection found for webhook from {store_url}")
            return HttpResponse(status=404)

        # Verify signature
        signature_verified = verify_webhook_signature(request, connection.webhook_secret)

        # Determine resource type
        resource_type = event_type.split('.')[0] if '.' in event_type else 'unknown'

        # Create webhook event record
        webhook_event = WebhookEvent.objects.create(
            tenant=connection.tenant,
            event_type=event_type,
            resource_type=resource_type,
            resource_id=str(resource_id),
            payload=payload,
            signature=request.headers.get('X-WC-Webhook-Signature', ''),
            signature_verified=signature_verified,
            status='pending'
        )

        # Process webhook based on event type
        if signature_verified:
            process_webhook_event(webhook_event)
        else:
            webhook_event.status = 'ignored'
            webhook_event.error_message = 'Signature verification failed'
            webhook_event.save()
            logger.warning(f"Webhook signature verification failed for event {event_type}")

        return JsonResponse({'status': 'received'}, status=200)

    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        return JsonResponse({'error': str(e)}, status=500)


def process_webhook_event(webhook_event: WebhookEvent):
    """Process a webhook event based on its type."""
    try:
        webhook_event.status = 'processing'
        webhook_event.save()

        event_type = webhook_event.event_type
        payload = webhook_event.payload
        tenant = webhook_event.tenant

        # Customer events
        if event_type in ['customer.created', 'customer.updated']:
            process_customer_webhook(tenant, payload)

        # Coupon events
        elif event_type in ['coupon.created', 'coupon.updated']:
            process_coupon_webhook(tenant, payload)

        # Order events (future implementation)
        elif event_type in ['order.created', 'order.updated']:
            # TODO: Implement order sync
            pass

        # Product events (future implementation)
        elif event_type in ['product.created', 'product.updated']:
            # TODO: Implement product sync
            pass

        # Mark as processed
        webhook_event.status = 'processed'
        webhook_event.processed_at = timezone.now()
        webhook_event.save()

    except Exception as e:
        webhook_event.status = 'failed'
        webhook_event.error_message = str(e)
        webhook_event.save()
        logger.error(f"Failed to process webhook event {webhook_event.id}: {e}")


def process_customer_webhook(tenant, payload):
    """Process customer webhook data."""
    wc_customer_id = payload.get('id')

    if not wc_customer_id:
        raise ValueError('Missing customer ID in payload')

    # Check if customer exists
    customer = Customer.objects.filter(
        tenant=tenant,
        woocommerce_customer_id=wc_customer_id
    ).first()

    customer_data = {
        'first_name': payload.get('first_name', ''),
        'last_name': payload.get('last_name', ''),
        'email': payload.get('email', ''),
        'phone': payload.get('billing', {}).get('phone', ''),
        'woocommerce_customer_id': wc_customer_id,
        'last_synced_at': timezone.now(),
    }

    if customer:
        # Update existing customer
        for key, value in customer_data.items():
            setattr(customer, key, value)
        customer.save()
        logger.info(f"Updated customer {customer.full_name} from webhook")
    else:
        # Create new customer
        customer = Customer.objects.create(tenant=tenant, **customer_data)
        logger.info(f"Created customer {customer.full_name} from webhook")


def process_coupon_webhook(tenant, payload):
    """Process coupon webhook data."""
    wc_coupon_id = payload.get('id')

    if not wc_coupon_id:
        raise ValueError('Missing coupon ID in payload')

    # Check if coupon exists
    coupon = Coupon.objects.filter(
        tenant=tenant,
        woocommerce_coupon_id=wc_coupon_id
    ).first()

    # Parse expiry date
    date_expires = None
    if payload.get('date_expires'):
        from django.utils.dateparse import parse_datetime
        date_expires = parse_datetime(payload['date_expires'])

    coupon_data = {
        'code': payload.get('code', '').upper(),
        'description': payload.get('description', ''),
        'discount_type': payload.get('discount_type', 'percent'),
        'amount': payload.get('amount', 0),
        'minimum_amount': payload.get('minimum_amount') or None,
        'maximum_amount': payload.get('maximum_amount') or None,
        'individual_use': payload.get('individual_use', False),
        'exclude_sale_items': payload.get('exclude_sale_items', False),
        'usage_limit': payload.get('usage_limit') or None,
        'usage_limit_per_user': payload.get('usage_limit_per_user') or None,
        'usage_count': payload.get('usage_count', 0),
        'date_expires': date_expires,
        'product_ids': payload.get('product_ids', []),
        'excluded_product_ids': payload.get('excluded_product_ids', []),
        'product_categories': payload.get('product_categories', []),
        'excluded_product_categories': payload.get('excluded_product_categories', []),
        'email_restrictions': payload.get('email_restrictions', []),
        'woocommerce_coupon_id': wc_coupon_id,
        'last_synced_at': timezone.now(),
        'sync_status': 'synced',
    }

    if coupon:
        # Update existing coupon
        for key, value in coupon_data.items():
            setattr(coupon, key, value)
        coupon.save()
        logger.info(f"Updated coupon {coupon.code} from webhook")
    else:
        # Create new coupon
        coupon = Coupon.objects.create(tenant=tenant, **coupon_data)
        logger.info(f"Created coupon {coupon.code} from webhook")
