"""Views for Customers app."""
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.parsers import MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import render
from django.db.models import Q
from django.db.models.functions import Greatest
from django.utils import timezone
from apps.core.permissions import (
    CanAddCustomerPermission,
    CanAddStaffMemberPermission,
    CanUploadToS3Permission
)
from apps.core.exceptions import PlanLimitExceeded
from .models import (
    Customer, PlatformIntegration, ImportedCustomer,
    TreatmentType, StaffMember, Treatment
)
from .serializers import (
    CustomerListSerializer,
    CustomerDetailSerializer,
    CustomerCreateUpdateSerializer,
    PlatformIntegrationSerializer,
    ImportedCustomerSerializer,
    TreatmentTypeSerializer,
    StaffMemberSerializer,
    TreatmentSerializer
)


def customers_page(request):
    """Render the customers management page."""
    return render(request, 'customers.html')


def customer_profile_page(request, customer_id):
    """Render the customer profile page."""
    return render(request, 'customer_profile.html', {'customer_id': customer_id})


class CustomerViewSet(viewsets.ModelViewSet):
    """ViewSet for Customer management with profile image upload."""

    queryset = Customer.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['customer_type', 'is_active', 'city']
    search_fields = ['first_name', 'last_name', 'email', 'phone', 'company']
    ordering_fields = ['first_name', 'last_name', 'total_spent', 'total_orders', 'created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        """Filter by tenant and optionally by search query."""
        queryset = super().get_queryset().filter(tenant=self.request.user.tenant)

        # Search
        search = self.request.query_params.get('q')
        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(email__icontains=search) |
                Q(phone__icontains=search)
            )

        # Order by last interaction (treatment or purchase)
        queryset = queryset.annotate(
            last_interaction=Greatest('last_purchase_date', 'last_treatment_date')
        ).order_by('-last_interaction', '-created_at')

        return queryset

    def get_serializer_class(self):
        """Return appropriate serializer."""
        if self.action == 'retrieve':
            return CustomerDetailSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return CustomerCreateUpdateSerializer
        return CustomerListSerializer

    def perform_create(self, serializer):
        """Set tenant on create and check plan limits."""
        user = self.request.user

        if not user.is_authenticated:
            raise PermissionDenied("User must be authenticated")

        if not hasattr(user, 'tenant') or user.tenant is None:
            raise ValidationError("User must have a tenant")

        # Check plan limits before creating
        tenant = user.tenant
        if not tenant.can_add_customer():
            raise PlanLimitExceeded(
                resource_type='customers',
                max_allowed=tenant.max_customers
            )

        serializer.save(tenant=tenant)

    @action(detail=False, methods=['get'])
    def vip_customers(self, request):
        """Get VIP customers."""
        customers = self.get_queryset().filter(customer_type='VIP')
        serializer = self.get_serializer(customers, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def top_spenders(self, request):
        """Get top spending customers."""
        limit = int(request.query_params.get('limit', 10))
        customers = self.get_queryset().order_by('-total_spent')[:limit]
        serializer = self.get_serializer(customers, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def inactive(self, request):
        """Get inactive customers."""
        customers = self.get_queryset().filter(is_active=False)
        serializer = self.get_serializer(customers, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def upload_profile_image(self, request, pk=None):
        """
        POST /api/customers/{id}/upload-profile-image/
        Upload customer profile picture (size limits apply)
        """
        customer = self.get_object()

        if 'image' not in request.FILES:
            return Response({'error': 'לא סופקה תמונה'}, status=status.HTTP_400_BAD_REQUEST)

        image_file = request.FILES['image']
        file_size_mb = image_file.size / (1024 * 1024)

        # Validate file type
        allowed_types = ['image/jpeg', 'image/png', 'image/webp', 'image/jpg']
        if image_file.content_type not in allowed_types:
            return Response({'error': 'סוג קובץ לא תקין. מותרים: JPEG, PNG, WebP'}, status=status.HTTP_400_BAD_REQUEST)

        # Check plan limits for file size
        tenant = request.user.tenant
        if not tenant.can_upload_to_s3(file_size_mb):
            return Response({
                'error': 'PLAN_LIMIT_EXCEEDED',
                'message': f'קובץ גדול מדי. במסלול {tenant.plan} ניתן להעלות קבצים עד {tenant.max_s3_storage_mb}MB',
                'upgrade_message': 'שדרג ל-Pro להעלאה ללא הגבלה'
            }, status=status.HTTP_403_FORBIDDEN)

        # Save image (will upload to S3 if configured)
        customer.profile_image = image_file
        customer.save()

        return Response({
            'message': 'תמונה הועלתה בהצלחה',
            'image_url': customer.profile_image.url
        })

    @action(detail=False, methods=['get'])
    def birthdays_this_month(self, request):
        """
        GET /api/customers/birthdays-this-month/
        Get customers with birthdays this month (for marketing)
        """
        current_month = timezone.now().month

        customers = self.get_queryset().filter(
            birth_date__month=current_month
        ).order_by('birth_date__day')

        serializer = CustomerListSerializer(customers, many=True, context={'request': request})
        return Response(serializer.data)


class PlatformIntegrationViewSet(viewsets.ModelViewSet):
    """ViewSet for Platform Integration management."""

    queryset = PlatformIntegration.objects.all()
    serializer_class = PlatformIntegrationSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['platform', 'is_active']
    ordering = ['-created_at']

    def get_queryset(self):
        """Filter by tenant."""
        return super().get_queryset().filter(tenant=self.request.user.tenant)

    def perform_create(self, serializer):
        """Set tenant on create."""
        serializer.save(tenant=self.request.user.tenant)

    @action(detail=True, methods=['post'])
    def import_customers(self, request, pk=None):
        """Import customers from the platform."""
        integration = self.get_object()

        # This is a placeholder - will implement actual API calls later
        # For now, just update last_sync_at
        integration.last_sync_at = timezone.now()
        integration.save()

        return Response({
            'message': 'Customer import initiated',
            'integration_id': integration.id,
            'platform': integration.get_platform_display(),
            'last_sync_at': integration.last_sync_at
        })

    @action(detail=True, methods=['post'])
    def test_connection(self, request, pk=None):
        """Test the API connection."""
        integration = self.get_object()

        # Placeholder for testing connection
        # Will implement actual API ping later
        return Response({
            'success': True,
            'message': f'Connection to {integration.get_platform_display()} established',
            'store_url': integration.store_url
        })


class ImportedCustomerViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Imported Customer (read-only)."""

    queryset = ImportedCustomer.objects.select_related('integration', 'customer').all()
    serializer_class = ImportedCustomerSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['integration', 'customer']
    ordering = ['-imported_at']

    def get_queryset(self):
        """Filter by tenant."""
        return super().get_queryset().filter(integration__tenant=self.request.user.tenant)


# ==================== TREATMENT VIEWSETS ====================

class TreatmentTypeViewSet(viewsets.ModelViewSet):
    """ViewSet for managing treatment types (Settings)."""

    queryset = TreatmentType.objects.filter(is_active=True)
    serializer_class = TreatmentTypeSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['is_active']
    ordering = ['name']

    def get_queryset(self):
        """Filter by tenant."""
        return super().get_queryset().filter(tenant=self.request.user.tenant)

    def perform_destroy(self, instance):
        """Soft delete - mark as inactive instead of deleting."""
        instance.is_active = False
        instance.save()


class StaffMemberViewSet(viewsets.ModelViewSet):
    """ViewSet for managing staff members (Settings)."""

    queryset = StaffMember.objects.filter(is_active=True)
    serializer_class = StaffMemberSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['is_active']
    ordering = ['full_name']

    def get_queryset(self):
        """Filter by tenant."""
        return super().get_queryset().filter(tenant=self.request.user.tenant)

    def perform_create(self, serializer):
        """Set tenant on create and check plan limits."""
        tenant = self.request.user.tenant

        # Check plan limits before creating
        if not tenant.can_add_staff_member():
            raise PlanLimitExceeded(
                resource_type='staff_members',
                max_allowed=tenant.max_staff_members
            )

        serializer.save(tenant=tenant)

    def perform_destroy(self, instance):
        """Soft delete - mark as inactive instead of deleting."""
        instance.is_active = False
        instance.save()


class TreatmentViewSet(viewsets.ModelViewSet):
    """ViewSet for managing customer treatment history."""

    queryset = Treatment.objects.all()
    serializer_class = TreatmentSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['customer', 'treatment_type', 'staff_member']
    ordering = ['-treatment_date', '-created_at']

    def get_queryset(self):
        """Filter by tenant and optional customer."""
        queryset = super().get_queryset().filter(tenant=self.request.user.tenant)

        # Filter by customer
        customer_id = self.request.query_params.get('customer_id')
        if customer_id:
            queryset = queryset.filter(customer_id=customer_id)

        # Filter by date range
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')

        if date_from:
            queryset = queryset.filter(treatment_date__gte=date_from)
        if date_to:
            queryset = queryset.filter(treatment_date__lte=date_to)

        return queryset.order_by('-treatment_date')
