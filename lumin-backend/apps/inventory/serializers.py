"""Serializers for Inventory app."""
from rest_framework import serializers
from .models import Product, Category, StockMovement


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for Category model."""

    products_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'products_count', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

    def get_products_count(self, obj):
        return obj.products.filter(is_active=True).count()


class ProductListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for product lists."""

    category_name = serializers.CharField(source='category.name', read_only=True, allow_null=True)
    stock_status = serializers.SerializerMethodField()
    profit_margin = serializers.ReadOnlyField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'sku', 'barcode', 'category', 'category_name',
            'price', 'cost', 'stock_quantity', 'min_stock_level', 'unit',
            'is_active', 'stock_status', 'profit_margin', 'image'
        ]

    def get_stock_status(self, obj):
        """Return stock status: 'low', 'medium', 'good'."""
        if obj.stock_quantity == 0:
            return 'out'
        elif obj.is_low_stock:
            return 'low'
        elif obj.stock_quantity < obj.min_stock_level * 2:
            return 'medium'
        return 'good'


class ProductDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for single product."""

    category_name = serializers.CharField(source='category.name', read_only=True, allow_null=True)
    stock_status = serializers.SerializerMethodField()
    profit_margin = serializers.ReadOnlyField()
    is_low_stock = serializers.ReadOnlyField()
    recent_movements = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'sku', 'barcode', 'category', 'category_name',
            'description', 'price', 'cost', 'stock_quantity', 'min_stock_level',
            'unit', 'image', 'is_active', 'stock_status', 'profit_margin',
            'is_low_stock', 'recent_movements', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_stock_status(self, obj):
        """Return stock status."""
        if obj.stock_quantity == 0:
            return 'out'
        elif obj.is_low_stock:
            return 'low'
        elif obj.stock_quantity < obj.min_stock_level * 2:
            return 'medium'
        return 'good'

    def get_recent_movements(self, obj):
        """Get last 5 stock movements."""
        movements = obj.stock_movements.all()[:5]
        return StockMovementSerializer(movements, many=True).data


class StockMovementSerializer(serializers.ModelSerializer):
    """Serializer for Stock Movement."""

    product_name = serializers.CharField(source='product.name', read_only=True)
    movement_type_display = serializers.CharField(source='get_movement_type_display', read_only=True)

    class Meta:
        model = StockMovement
        fields = [
            'id', 'product', 'product_name', 'movement_type', 'movement_type_display',
            'quantity', 'notes', 'reference', 'created_at'
        ]
        read_only_fields = ['created_at']
