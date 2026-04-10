"""Views for Inventory app."""
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import render
from django.db import models
from apps.core.exceptions import PlanLimitExceeded
from apps.accounts.services import TenantService
from .models import Product, Category, StockMovement
from .serializers import (
    ProductListSerializer,
    ProductDetailSerializer,
    CategorySerializer,
    StockMovementSerializer
)


from django.contrib.auth.decorators import login_required
from rest_framework.permissions import IsAuthenticated

@login_required
def products_page(request):
    """Render the products management page."""
    return render(request, 'products.html')


class ProductViewSet(viewsets.ModelViewSet):
    """ViewSet for Product management."""
    permission_classes = [IsAuthenticated]

    queryset = Product.objects.select_related('category').all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'is_active']
    search_fields = ['name', 'sku', 'barcode', 'description']
    ordering_fields = ['name', 'price', 'stock_quantity', 'created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        """Filter by tenant."""
        return super().get_queryset().filter(tenant=self.request.user.tenant)

    def get_serializer_class(self):
        """Return appropriate serializer."""
        if self.action == 'retrieve':
            return ProductDetailSerializer
        return ProductListSerializer

    def perform_create(self, serializer):
        """Set tenant on create and check plan limits."""
        tenant = self.request.user.tenant

        # Check plan limits before creating
        if not TenantService(tenant).can_add_product():
            raise PlanLimitExceeded(
                resource_type='products',
                max_allowed=tenant.max_products
            )

        serializer.save(tenant=tenant)

    @action(detail=True, methods=['post'])
    def adjust_stock(self, request, pk=None):
        """Adjust product stock quantity."""
        product = self.get_object()
        quantity = request.data.get('quantity', 0)
        movement_type = request.data.get('type', 'ADJUSTMENT')
        notes = request.data.get('notes', '')

        try:
            quantity = int(quantity)
        except ValueError:
            return Response(
                {'error': 'Invalid quantity'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create stock movement
        StockMovement.objects.create(
            tenant=request.user.tenant,
            product=product,
            movement_type=movement_type,
            quantity=quantity,
            notes=notes
        )

        # Update product stock
        if movement_type in ['IN', 'RETURN']:
            product.stock_quantity += quantity
        elif movement_type in ['OUT', 'ADJUSTMENT']:
            product.stock_quantity = max(0, product.stock_quantity - quantity)

        product.save()

        serializer = self.get_serializer(product)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        """Get products with low stock."""
        products = self.get_queryset().filter(
            stock_quantity__lt=models.F('min_stock_level')
        )
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)


class CategoryViewSet(viewsets.ModelViewSet):
    """ViewSet for Category management."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering = ['name']

    def get_queryset(self):
        """Filter by tenant."""
        return super().get_queryset().filter(tenant=self.request.user.tenant)

    def perform_create(self, serializer):
        """Set tenant on create."""
        serializer.save(tenant=self.request.user.tenant)


class StockMovementViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Stock Movement (read-only)."""

    queryset = StockMovement.objects.select_related('product').all()
    serializer_class = StockMovementSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['product', 'movement_type']
    ordering = ['-created_at']

    def get_queryset(self):
        """Filter by tenant."""
        return super().get_queryset().filter(tenant=self.request.user.tenant)
