"""
Inventory models - Products and Stock Management.
"""
from django.db import models
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _
from apps.core.models import BaseModel
from apps.accounts.models import Tenant


class Category(BaseModel):
    """
    Product categories.
    """
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name='categories',
        verbose_name=_('Tenant')
    )
    name = models.CharField(
        max_length=100,
        verbose_name=_('Category Name')
    )
    description = models.TextField(
        blank=True,
        verbose_name=_('Description')
    )

    class Meta:
        verbose_name = _('קטגוריה')
        verbose_name_plural = _('קטגוריות')
        ordering = ['name']
        indexes = [
            models.Index(fields=['tenant', 'name']),
        ]

    def __str__(self):
        return self.name


class Product(BaseModel):
    """
    Product model for inventory management.
    """
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name=_('Tenant')
    )
    name = models.CharField(
        max_length=255,
        verbose_name=_('Product Name')
    )
    sku = models.CharField(
        max_length=100,
        verbose_name=_('SKU'),
        help_text=_('Stock Keeping Unit - unique product code')
    )
    barcode = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_('Barcode')
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products',
        verbose_name=_('Category')
    )
    description = models.TextField(
        blank=True,
        verbose_name=_('Description')
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name=_('Price')
    )
    cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        default=0,
        verbose_name=_('Cost'),
        help_text=_('Product cost for profit calculation')
    )
    stock_quantity = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name=_('Stock Quantity')
    )
    min_stock_level = models.IntegerField(
        default=10,
        validators=[MinValueValidator(0)],
        verbose_name=_('Minimum Stock Level'),
        help_text=_('Alert when stock falls below this level')
    )
    unit = models.CharField(
        max_length=20,
        default='יחידה',
        verbose_name=_('Unit'),
        help_text=_('e.g., יחידה, קילו, ליטר')
    )
    image = models.ImageField(
        upload_to='products/',
        blank=True,
        null=True,
        verbose_name=_('Product Image')
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Active')
    )

    # WooCommerce Integration
    woocommerce_product_id = models.IntegerField(
        null=True,
        blank=True,
        verbose_name=_('WooCommerce Product ID'),
        help_text=_('WooCommerce product ID for sync')
    )
    last_synced_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Last Synced At'),
        help_text=_('Last sync with WooCommerce')
    )

    class Meta:
        verbose_name = _('מוצר')
        verbose_name_plural = _('מוצרים')
        ordering = ['name']
        unique_together = [['tenant', 'sku']]
        indexes = [
            models.Index(fields=['tenant', 'sku']),
            models.Index(fields=['tenant', 'barcode']),
            models.Index(fields=['tenant', 'is_active']),
        ]

    def __str__(self):
        return f"{self.name} ({self.sku})"

    @property
    def is_low_stock(self):
        """Check if product is below minimum stock level."""
        return self.stock_quantity < self.min_stock_level

    @property
    def profit_margin(self):
        """Calculate profit margin percentage."""
        if self.cost == 0:
            return 0
        return ((self.price - self.cost) / self.cost) * 100


class StockMovement(BaseModel):
    """
    Track all stock movements (in/out).
    """
    MOVEMENT_TYPES = [
        ('IN', _('Stock In')),
        ('OUT', _('Stock Out')),
        ('ADJUSTMENT', _('Adjustment')),
        ('RETURN', _('Return')),
    ]

    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name='stock_movements',
        verbose_name=_('Tenant')
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='stock_movements',
        verbose_name=_('Product')
    )
    movement_type = models.CharField(
        max_length=20,
        choices=MOVEMENT_TYPES,
        verbose_name=_('Movement Type')
    )
    quantity = models.IntegerField(
        verbose_name=_('Quantity')
    )
    notes = models.TextField(
        blank=True,
        verbose_name=_('Notes')
    )
    reference = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_('Reference'),
        help_text=_('Order number, invoice number, etc.')
    )

    class Meta:
        verbose_name = _('תנועת מלאי')
        verbose_name_plural = _('תנועות מלאי')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['tenant', 'product', '-created_at']),
            models.Index(fields=['tenant', 'movement_type']),
        ]

    def __str__(self):
        return f"{self.product.name} - {self.get_movement_type_display()} ({self.quantity})"
