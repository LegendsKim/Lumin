"""
Celery tasks for WooCommerce sync operations.
"""
import logging
from typing import Dict, Any, List
from celery import shared_task
from django.utils import timezone
from django.db import transaction
from woocommerce import API

from .models import (
    WooCommerceConnection,
    SyncJob,
    SyncLog,
    Coupon,
)
from apps.customers.models import Customer
from apps.accounts.models import Tenant

logger = logging.getLogger(__name__)


def get_woocommerce_api(connection: WooCommerceConnection) -> API:
    """Create WooCommerce API instance from connection settings."""
    return API(
        url=connection.store_url,
        consumer_key=connection.consumer_key,
        consumer_secret=connection.consumer_secret,
        version="wc/v3",
        timeout=30
    )


def log_sync_event(sync_job: SyncJob, level: str, message: str, item_id: str = '', details: Dict = None):
    """Create a sync log entry."""
    SyncLog.objects.create(
        sync_job=sync_job,
        level=level,
        message=message,
        item_id=item_id,
        details=details or {}
    )


@shared_task(bind=True, max_retries=3)
def sync_customers_from_woocommerce(self, tenant_id: str, sync_job_id: str):
    """Import customers from WooCommerce."""
    try:
        tenant = Tenant.objects.get(id=tenant_id)
        sync_job = SyncJob.objects.get(id=sync_job_id)
        connection = tenant.woocommerce_connection

        # Update job status
        sync_job.status = 'running'
        sync_job.started_at = timezone.now()
        sync_job.celery_task_id = self.request.id
        sync_job.save()

        # Get WooCommerce API
        wcapi = get_woocommerce_api(connection)

        # Fetch customers from WooCommerce (paginated)
        page = 1
        per_page = 100
        all_customers = []

        while True:
            response = wcapi.get("customers", params={"page": page, "per_page": per_page})
            if response.status_code != 200:
                raise Exception(f"WooCommerce API error: {response.status_code} - {response.text}")

            customers = response.json()
            if not customers:
                break

            all_customers.extend(customers)
            page += 1

        sync_job.total_items = len(all_customers)
        sync_job.save()

        log_sync_event(sync_job, 'info', f'נמצאו {len(all_customers)} לקוחות ב-WooCommerce')

        # Process each customer
        for wc_customer in all_customers:
            try:
                # Check if customer already exists
                customer = Customer.objects.filter(
                    tenant=tenant,
                    woocommerce_customer_id=wc_customer['id']
                ).first()

                customer_data = {
                    'first_name': wc_customer.get('first_name', ''),
                    'last_name': wc_customer.get('last_name', ''),
                    'email': wc_customer.get('email', ''),
                    'phone': wc_customer.get('billing', {}).get('phone', ''),
                    'woocommerce_customer_id': wc_customer['id'],
                    'last_synced_at': timezone.now(),
                }

                if customer:
                    # Update existing customer
                    for key, value in customer_data.items():
                        setattr(customer, key, value)
                    customer.save()
                    log_sync_event(sync_job, 'info', f'עודכן לקוח: {customer.full_name}', str(wc_customer['id']))
                else:
                    # Create new customer
                    customer = Customer.objects.create(
                        tenant=tenant,
                        **customer_data
                    )
                    log_sync_event(sync_job, 'info', f'נוצר לקוח חדש: {customer.full_name}', str(wc_customer['id']))

                sync_job.successful_items += 1

            except Exception as e:
                sync_job.failed_items += 1
                log_sync_event(
                    sync_job,
                    'error',
                    f'שגיאה בעיבוד לקוח {wc_customer.get("email", "")}: {str(e)}',
                    str(wc_customer.get('id', '')),
                    {'error': str(e)}
                )
                logger.error(f"Error processing customer {wc_customer.get('id')}: {e}")

            finally:
                sync_job.processed_items += 1
                sync_job.save()

        # Complete the job
        sync_job.status = 'completed'
        sync_job.completed_at = timezone.now()
        sync_job.save()

        connection.last_sync_at = timezone.now()
        connection.save()

        log_sync_event(sync_job, 'info', f'סנכרון הושלם בהצלחה. {sync_job.successful_items}/{sync_job.total_items} לקוחות')

        return {
            'status': 'completed',
            'total': sync_job.total_items,
            'successful': sync_job.successful_items,
            'failed': sync_job.failed_items
        }

    except Exception as e:
        logger.error(f"Sync customers task failed: {e}")
        sync_job.status = 'failed'
        sync_job.error_message = str(e)
        sync_job.completed_at = timezone.now()
        sync_job.save()

        log_sync_event(sync_job, 'error', f'הסנכרון נכשל: {str(e)}')

        raise self.retry(exc=e, countdown=60)


@shared_task(bind=True, max_retries=3)
def sync_coupons_from_woocommerce(self, tenant_id: str, sync_job_id: str):
    """Import coupons from WooCommerce."""
    try:
        tenant = Tenant.objects.get(id=tenant_id)
        sync_job = SyncJob.objects.get(id=sync_job_id)
        connection = tenant.woocommerce_connection

        # Update job status
        sync_job.status = 'running'
        sync_job.started_at = timezone.now()
        sync_job.celery_task_id = self.request.id
        sync_job.save()

        # Get WooCommerce API
        wcapi = get_woocommerce_api(connection)

        # Fetch coupons from WooCommerce
        page = 1
        per_page = 100
        all_coupons = []

        while True:
            response = wcapi.get("coupons", params={"page": page, "per_page": per_page})
            if response.status_code != 200:
                raise Exception(f"WooCommerce API error: {response.status_code} - {response.text}")

            coupons = response.json()
            if not coupons:
                break

            all_coupons.extend(coupons)
            page += 1

        sync_job.total_items = len(all_coupons)
        sync_job.save()

        log_sync_event(sync_job, 'info', f'נמצאו {len(all_coupons)} קופונים ב-WooCommerce')

        # Process each coupon
        for wc_coupon in all_coupons:
            try:
                # Check if coupon already exists
                coupon = Coupon.objects.filter(
                    tenant=tenant,
                    woocommerce_coupon_id=wc_coupon['id']
                ).first()

                # Parse expiry date
                date_expires = None
                if wc_coupon.get('date_expires'):
                    from django.utils.dateparse import parse_datetime
                    date_expires = parse_datetime(wc_coupon['date_expires'])

                coupon_data = {
                    'code': wc_coupon.get('code', '').upper(),
                    'description': wc_coupon.get('description', ''),
                    'discount_type': wc_coupon.get('discount_type', 'percent'),
                    'amount': wc_coupon.get('amount', 0),
                    'minimum_amount': wc_coupon.get('minimum_amount') or None,
                    'maximum_amount': wc_coupon.get('maximum_amount') or None,
                    'individual_use': wc_coupon.get('individual_use', False),
                    'exclude_sale_items': wc_coupon.get('exclude_sale_items', False),
                    'usage_limit': wc_coupon.get('usage_limit') or None,
                    'usage_limit_per_user': wc_coupon.get('usage_limit_per_user') or None,
                    'usage_count': wc_coupon.get('usage_count', 0),
                    'date_expires': date_expires,
                    'product_ids': wc_coupon.get('product_ids', []),
                    'excluded_product_ids': wc_coupon.get('excluded_product_ids', []),
                    'product_categories': wc_coupon.get('product_categories', []),
                    'excluded_product_categories': wc_coupon.get('excluded_product_categories', []),
                    'email_restrictions': wc_coupon.get('email_restrictions', []),
                    'woocommerce_coupon_id': wc_coupon['id'],
                    'last_synced_at': timezone.now(),
                    'sync_status': 'synced',
                }

                if coupon:
                    # Update existing coupon
                    for key, value in coupon_data.items():
                        setattr(coupon, key, value)
                    coupon.save()
                    log_sync_event(sync_job, 'info', f'עודכן קופון: {coupon.code}', str(wc_coupon['id']))
                else:
                    # Create new coupon
                    coupon = Coupon.objects.create(
                        tenant=tenant,
                        **coupon_data
                    )
                    log_sync_event(sync_job, 'info', f'נוצר קופון חדש: {coupon.code}', str(wc_coupon['id']))

                sync_job.successful_items += 1

            except Exception as e:
                sync_job.failed_items += 1
                log_sync_event(
                    sync_job,
                    'error',
                    f'שגיאה בעיבוד קופון {wc_coupon.get("code", "")}: {str(e)}',
                    str(wc_coupon.get('id', '')),
                    {'error': str(e)}
                )
                logger.error(f"Error processing coupon {wc_coupon.get('id')}: {e}")

            finally:
                sync_job.processed_items += 1
                sync_job.save()

        # Complete the job
        sync_job.status = 'completed'
        sync_job.completed_at = timezone.now()
        sync_job.save()

        connection.last_sync_at = timezone.now()
        connection.save()

        log_sync_event(sync_job, 'info', f'סנכרון הושלם בהצלחה. {sync_job.successful_items}/{sync_job.total_items} קופונים')

        return {
            'status': 'completed',
            'total': sync_job.total_items,
            'successful': sync_job.successful_items,
            'failed': sync_job.failed_items
        }

    except Exception as e:
        logger.error(f"Sync coupons task failed: {e}")
        sync_job.status = 'failed'
        sync_job.error_message = str(e)
        sync_job.completed_at = timezone.now()
        sync_job.save()

        log_sync_event(sync_job, 'error', f'הסנכרון נכשל: {str(e)}')

        raise self.retry(exc=e, countdown=60)


@shared_task(bind=True, max_retries=3)
def export_coupon_to_woocommerce(self, coupon_id: str):
    """Export a single coupon to WooCommerce."""
    try:
        coupon = Coupon.objects.get(id=coupon_id)
        tenant = coupon.tenant
        connection = tenant.woocommerce_connection

        if not connection or not connection.is_active:
            raise Exception('אין חיבור פעיל ל-WooCommerce')

        # Get WooCommerce API
        wcapi = get_woocommerce_api(connection)

        # Prepare coupon data for WooCommerce
        wc_data = {
            'code': coupon.code,
            'description': coupon.description,
            'discount_type': coupon.discount_type,
            'amount': str(coupon.amount),
            'individual_use': coupon.individual_use,
            'exclude_sale_items': coupon.exclude_sale_items,
            'minimum_amount': str(coupon.minimum_amount) if coupon.minimum_amount else '',
            'maximum_amount': str(coupon.maximum_amount) if coupon.maximum_amount else '',
            'usage_limit': coupon.usage_limit,
            'usage_limit_per_user': coupon.usage_limit_per_user,
            'product_ids': coupon.product_ids,
            'excluded_product_ids': coupon.excluded_product_ids,
            'product_categories': coupon.product_categories,
            'excluded_product_categories': coupon.excluded_product_categories,
            'email_restrictions': coupon.email_restrictions,
        }

        if coupon.date_expires:
            wc_data['date_expires'] = coupon.date_expires.isoformat()

        if coupon.woocommerce_coupon_id:
            # Update existing coupon
            response = wcapi.put(f"coupons/{coupon.woocommerce_coupon_id}", wc_data)
        else:
            # Create new coupon
            response = wcapi.post("coupons", wc_data)

        if response.status_code not in [200, 201]:
            raise Exception(f"WooCommerce API error: {response.status_code} - {response.text}")

        wc_coupon = response.json()

        # Update local coupon
        coupon.woocommerce_coupon_id = wc_coupon['id']
        coupon.last_synced_at = timezone.now()
        coupon.sync_status = 'synced'
        coupon.save()

        logger.info(f"Successfully exported coupon {coupon.code} to WooCommerce")

        return {
            'status': 'success',
            'coupon_id': str(coupon.id),
            'woocommerce_id': wc_coupon['id']
        }

    except Exception as e:
        logger.error(f"Export coupon task failed: {e}")
        if 'coupon' in locals():
            coupon.sync_status = 'error'
            coupon.save()
        raise self.retry(exc=e, countdown=60)


@shared_task
def test_woocommerce_connection(tenant_id: str, store_url: str, consumer_key: str, consumer_secret: str):
    """Test WooCommerce connection."""
    try:
        wcapi = API(
            url=store_url,
            consumer_key=consumer_key,
            consumer_secret=consumer_secret,
            version="wc/v3",
            timeout=10
        )

        # Try to fetch store data
        response = wcapi.get("system_status")

        if response.status_code == 200:
            return {
                'status': 'success',
                'message': 'החיבור ל-WooCommerce הצליח!'
            }
        else:
            return {
                'status': 'error',
                'message': f'שגיאה בחיבור: {response.status_code}'
            }

    except Exception as e:
        logger.error(f"Connection test failed: {e}")
        return {
            'status': 'error',
            'message': f'שגיאה: {str(e)}'
        }
