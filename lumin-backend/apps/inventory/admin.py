"""Admin configuration for Inventory app."""
from django.contrib import admin
from .models import Category, Product, StockMovement


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'tenant', 'created_at']
    list_filter = ['tenant', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['name']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'sku', 'category', 'price', 'stock_quantity', 'is_low_stock', 'is_active', 'tenant']
    list_filter = ['tenant', 'category', 'is_active', 'created_at']
    search_fields = ['name', 'sku', 'barcode', 'description']
    ordering = ['name']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('מידע בסיסי', {
            'fields': ('tenant', 'name', 'sku', 'barcode', 'category', 'description')
        }),
        ('תמחור ומלאי', {
            'fields': ('price', 'cost', 'stock_quantity', 'min_stock_level', 'unit')
        }),
        ('נוסף', {
            'fields': ('image', 'is_active', 'created_at', 'updated_at')
        }),
    )

    def is_low_stock(self, obj):
        return obj.is_low_stock
    is_low_stock.boolean = True
    is_low_stock.short_description = 'מלאי נמוך'


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ['product', 'movement_type', 'quantity', 'reference', 'created_at', 'tenant']
    list_filter = ['tenant', 'movement_type', 'created_at']
    search_fields = ['product__name', 'reference', 'notes']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('פרטי תנועה', {
            'fields': ('tenant', 'product', 'movement_type', 'quantity')
        }),
        ('מידע נוסף', {
            'fields': ('reference', 'notes', 'created_at', 'updated_at')
        }),
    )
