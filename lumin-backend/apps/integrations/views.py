"""
Views for integrations app.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import render
from django.db import transaction

from .models import (
    WooCommerceConnection,
    SyncJob,
    Coupon,
    WebhookEvent
)
from .serializers import (
    WooCommerceConnectionSerializer,
    SyncJobSerializer,
    SyncJobCreateSerializer,
    CouponSerializer,
    CouponListSerializer,
    WebhookEventSerializer,
    ConnectionTestSerializer,
)
from .tasks import (
    sync_customers_from_woocommerce,
    sync_coupons_from_woocommerce,
    export_coupon_to_woocommerce,
    test_woocommerce_connection,
)


def sync_page(request):
    """Render the sync page."""
    return render(request, 'sync.html')


def coupons_page(request):
    """Render the coupons management page."""
    return render(request, 'coupons.html')


class WooCommerceConnectionViewSet(viewsets.ModelViewSet):
    """ViewSet for managing WooCommerce connection settings."""

    serializer_class = WooCommerceConnectionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter by tenant."""
        return WooCommerceConnection.objects.filter(
            tenant=self.request.user.tenant
        )

    def perform_create(self, serializer):
        """Set tenant on creation."""
        serializer.save(tenant=self.request.user.tenant)

    @action(detail=False, methods=['post'])
    def test_connection(self, request):
        """Test WooCommerce connection without saving."""
        serializer = ConnectionTestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Test directly (synchronous)
        try:
            from woocommerce import API

            wcapi = API(
                url=serializer.validated_data['store_url'],
                consumer_key=serializer.validated_data['consumer_key'],
                consumer_secret=serializer.validated_data['consumer_secret'],
                version="wc/v3",
                timeout=10
            )

            # Try to fetch store info
            response = wcapi.get("system_status")

            if response.status_code == 200:
                return Response({
                    'status': 'success',
                    'message': 'החיבור ל-WooCommerce הצליח!'
                })
            else:
                return Response({
                    'status': 'error',
                    'message': f'שגיאה בחיבור: {response.status_code}'
                }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({
                'status': 'error',
                'message': f'החיבור נכשל: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Activate the connection."""
        connection = self.get_object()
        connection.is_active = True
        connection.save()
        return Response({'status': 'החיבור הופעל בהצלחה'})

    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """Deactivate the connection."""
        connection = self.get_object()
        connection.is_active = False
        connection.save()
        return Response({'status': 'החיבור הושבת'})


class SyncJobViewSet(viewsets.ModelViewSet):
    """ViewSet for managing sync jobs."""

    serializer_class = SyncJobSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'delete']

    def get_queryset(self):
        """Filter by tenant and order by creation date."""
        return SyncJob.objects.filter(
            tenant=self.request.user.tenant
        ).order_by('-created_at')

    @action(detail=False, methods=['post'])
    def start_sync(self, request):
        """Start a new sync job."""
        serializer = SyncJobCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        job_type = serializer.validated_data['job_type']
        direction = serializer.validated_data['direction']

        # Check if connection exists and is active
        try:
            connection = request.user.tenant.woocommerce_connection
            if not connection.is_active:
                return Response({
                    'error': 'החיבור ל-WooCommerce לא פעיל'
                }, status=status.HTTP_400_BAD_REQUEST)
        except WooCommerceConnection.DoesNotExist:
            return Response({
                'error': 'לא נמצא חיבור ל-WooCommerce'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Create sync job
        sync_job = SyncJob.objects.create(
            tenant=request.user.tenant,
            job_type=job_type,
            direction=direction,
            initiated_by=request.user
        )

        # Run sync directly (synchronous - for now, until Celery is set up)
        try:
            if job_type == 'customers' and direction == 'import':
                # Run customer sync synchronously
                self._sync_customers_direct(request.user.tenant, sync_job)
            elif job_type == 'coupons' and direction == 'import':
                # Run coupon sync synchronously
                self._sync_coupons_direct(request.user.tenant, sync_job)
            elif job_type == 'products' and direction == 'import':
                # Run product sync synchronously
                self._sync_products_direct(request.user.tenant, sync_job)
            else:
                sync_job.status = 'failed'
                sync_job.error_message = 'סוג סנכרון לא נתמך עדיין'
                sync_job.save()
                return Response({
                    'error': 'סוג סנכרון לא נתמך עדיין'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Refresh sync_job from DB
            sync_job.refresh_from_db()

            return Response({
                'status': 'הסנכרון הושלם!',
                'job_id': str(sync_job.id),
                'job': SyncJobSerializer(sync_job).data
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            sync_job.status = 'failed'
            sync_job.error_message = str(e)
            sync_job.save()
            return Response({
                'error': f'הסנכרון נכשל: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _sync_customers_direct(self, tenant, sync_job):
        """Direct customer sync without Celery."""
        from woocommerce import API
        from apps.customers.models import Customer
        from django.utils import timezone

        connection = tenant.woocommerce_connection

        # Update job status
        sync_job.status = 'running'
        sync_job.started_at = timezone.now()
        sync_job.save()

        # Get WooCommerce API
        wcapi = API(
            url=connection.store_url,
            consumer_key=connection.consumer_key,
            consumer_secret=connection.consumer_secret,
            version="wc/v3",
            timeout=30
        )

        # Fetch customers
        page = 1
        all_customers = []

        while True:
            response = wcapi.get("customers", params={"page": page, "per_page": 100})
            if response.status_code != 200:
                raise Exception(f"WooCommerce API error: {response.status_code}")

            customers = response.json()
            if not customers:
                break

            all_customers.extend(customers)
            page += 1

        sync_job.total_items = len(all_customers)
        sync_job.save()

        # Process each customer
        for wc_customer in all_customers:
            try:
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
                    for key, value in customer_data.items():
                        setattr(customer, key, value)
                    customer.save()
                else:
                    Customer.objects.create(tenant=tenant, **customer_data)

                sync_job.successful_items += 1

            except Exception as e:
                sync_job.failed_items += 1

            finally:
                sync_job.processed_items += 1
                sync_job.save()

        # Complete the job
        sync_job.status = 'completed'
        sync_job.completed_at = timezone.now()
        sync_job.save()

        connection.last_sync_at = timezone.now()
        connection.save()

    def _sync_coupons_direct(self, tenant, sync_job):
        """Direct coupon sync without Celery."""
        from woocommerce import API
        from django.utils import timezone

        connection = tenant.woocommerce_connection

        # Update job status
        sync_job.status = 'running'
        sync_job.started_at = timezone.now()
        sync_job.save()

        # Get WooCommerce API
        wcapi = API(
            url=connection.store_url,
            consumer_key=connection.consumer_key,
            consumer_secret=connection.consumer_secret,
            version="wc/v3",
            timeout=30
        )

        # Fetch coupons
        page = 1
        all_coupons = []

        while True:
            response = wcapi.get("coupons", params={"page": page, "per_page": 100})
            if response.status_code != 200:
                raise Exception(f"WooCommerce API error: {response.status_code}")

            coupons = response.json()
            if not coupons:
                break

            all_coupons.extend(coupons)
            page += 1

        sync_job.total_items = len(all_coupons)
        sync_job.save()

        # Process each coupon
        for wc_coupon in all_coupons:
            try:
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
                    for key, value in coupon_data.items():
                        setattr(coupon, key, value)
                    coupon.save()
                else:
                    Coupon.objects.create(tenant=tenant, **coupon_data)

                sync_job.successful_items += 1

            except Exception as e:
                sync_job.failed_items += 1

            finally:
                sync_job.processed_items += 1
                sync_job.save()

        # Complete the job
        sync_job.status = 'completed'
        sync_job.completed_at = timezone.now()
        sync_job.save()

        connection.last_sync_at = timezone.now()
        connection.save()

    def _sync_products_direct(self, tenant, sync_job):
        """Direct product sync without Celery."""
        from woocommerce import API
        from apps.inventory.models import Product, Category
        from django.utils import timezone

        connection = tenant.woocommerce_connection

        # Update job status
        sync_job.status = 'running'
        sync_job.started_at = timezone.now()
        sync_job.save()

        # Get WooCommerce API
        wcapi = API(
            url=connection.store_url,
            consumer_key=connection.consumer_key,
            consumer_secret=connection.consumer_secret,
            version="wc/v3",
            timeout=30
        )

        # Fetch products
        page = 1
        all_products = []

        while True:
            response = wcapi.get("products", params={"page": page, "per_page": 100})
            if response.status_code != 200:
                raise Exception(f"WooCommerce API error: {response.status_code}")

            products = response.json()
            if not products:
                break

            all_products.extend(products)
            page += 1

        sync_job.total_items = len(all_products)
        sync_job.save()

        # Process each product
        for wc_product in all_products:
            try:
                product = Product.objects.filter(
                    tenant=tenant,
                    woocommerce_product_id=wc_product['id']
                ).first()

                # Handle category mapping
                category = None
                if wc_product.get('categories') and len(wc_product['categories']) > 0:
                    wc_category = wc_product['categories'][0]
                    category, _ = Category.objects.get_or_create(
                        tenant=tenant,
                        name=wc_category.get('name', ''),
                        defaults={'description': ''}
                    )

                # Extract price (regular price or sale price)
                price = wc_product.get('price', 0) or wc_product.get('regular_price', 0)
                if not price:
                    price = 0

                product_data = {
                    'name': wc_product.get('name', ''),
                    'sku': wc_product.get('sku', f"WC-{wc_product['id']}"),
                    'description': wc_product.get('description', ''),
                    'price': price,
                    'stock_quantity': wc_product.get('stock_quantity', 0) or 0,
                    'category': category,
                    'is_active': wc_product.get('status') == 'publish',
                    'woocommerce_product_id': wc_product['id'],
                    'last_synced_at': timezone.now(),
                }

                if product:
                    for key, value in product_data.items():
                        setattr(product, key, value)
                    product.save()
                else:
                    Product.objects.create(tenant=tenant, **product_data)

                sync_job.successful_items += 1

            except Exception as e:
                sync_job.failed_items += 1

            finally:
                sync_job.processed_items += 1
                sync_job.save()

        # Complete the job
        sync_job.status = 'completed'
        sync_job.completed_at = timezone.now()
        sync_job.save()

        connection.last_sync_at = timezone.now()
        connection.save()

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel a running sync job."""
        sync_job = self.get_object()

        if sync_job.status not in ['pending', 'running']:
            return Response({
                'error': 'לא ניתן לבטל משימה שהושלמה או נכשלה'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Revoke Celery task
        if sync_job.celery_task_id:
            from celery.result import AsyncResult
            AsyncResult(sync_job.celery_task_id).revoke(terminate=True)

        sync_job.status = 'cancelled'
        sync_job.save()

        return Response({'status': 'הסנכרון בוטל'})


class CouponViewSet(viewsets.ModelViewSet):
    """ViewSet for managing coupons."""

    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'list':
            return CouponListSerializer
        return CouponSerializer

    def get_queryset(self):
        """Filter by tenant."""
        queryset = Coupon.objects.filter(tenant=self.request.user.tenant)

        # Filter by status
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')

        # Filter by sync status
        sync_status = self.request.query_params.get('sync_status')
        if sync_status:
            queryset = queryset.filter(sync_status=sync_status)

        # Search by code
        search = self.request.query_params.get('q')
        if search:
            queryset = queryset.filter(code__icontains=search)

        return queryset.order_by('-created_at')

    def perform_create(self, serializer):
        """Set tenant on creation and trigger sync."""
        coupon = serializer.save(tenant=self.request.user.tenant, sync_status='pending')

        # Check if WooCommerce sync is enabled
        try:
            connection = self.request.user.tenant.woocommerce_connection
            if connection.is_active and connection.sync_coupons:
                # Export to WooCommerce
                export_coupon_to_woocommerce.delay(str(coupon.id))
        except WooCommerceConnection.DoesNotExist:
            pass

    def perform_update(self, serializer):
        """Update coupon and trigger sync."""
        coupon = serializer.save(sync_status='pending')

        # Check if WooCommerce sync is enabled
        try:
            connection = self.request.user.tenant.woocommerce_connection
            if connection.is_active and connection.sync_coupons:
                # Export to WooCommerce
                export_coupon_to_woocommerce.delay(str(coupon.id))
        except WooCommerceConnection.DoesNotExist:
            pass

    @action(detail=True, methods=['post'])
    def sync_to_woocommerce(self, request, pk=None):
        """Manually sync a coupon to WooCommerce."""
        coupon = self.get_object()

        # Check connection
        try:
            connection = request.user.tenant.woocommerce_connection
            if not connection.is_active:
                return Response({
                    'error': 'החיבור ל-WooCommerce לא פעיל'
                }, status=status.HTTP_400_BAD_REQUEST)
        except WooCommerceConnection.DoesNotExist:
            return Response({
                'error': 'לא נמצא חיבור ל-WooCommerce'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Start sync task
        export_coupon_to_woocommerce.delay(str(coupon.id))

        return Response({
            'status': 'הסנכרון התחיל',
            'coupon_id': str(coupon.id)
        })

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get coupon statistics."""
        queryset = self.get_queryset()

        stats = {
            'total': queryset.count(),
            'active': queryset.filter(is_active=True).count(),
            'expired': queryset.filter(is_active=True).count() - sum(1 for c in queryset.filter(is_active=True) if c.is_valid),
            'synced': queryset.filter(sync_status='synced').count(),
            'pending_sync': queryset.filter(sync_status='pending').count(),
        }

        return Response(stats)


class WebhookEventViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing webhook events (read-only)."""

    serializer_class = WebhookEventSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter by tenant."""
        return WebhookEvent.objects.filter(
            tenant=self.request.user.tenant
        ).order_by('-created_at')
