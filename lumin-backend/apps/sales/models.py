"""
Sales models - Orders, Invoices, and Payments.
"""
from django.db import models
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _
from decimal import Decimal
from apps.core.models import BaseModel
from apps.accounts.models import Tenant, User
from apps.inventory.models import Product


class Customer(BaseModel):
    """
    Customer model for sales.
    """
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name='customers',
        verbose_name=_('Tenant')
    )
    name = models.CharField(
        max_length=255,
        verbose_name=_('Customer Name')
    )
    email = models.EmailField(
        blank=True,
        verbose_name=_('Email')
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name=_('Phone')
    )
    address = models.TextField(
        blank=True,
        verbose_name=_('Address')
    )
    tax_id = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_('Tax ID'),
        help_text=_('VAT number or business registration')
    )
    notes = models.TextField(
        blank=True,
        verbose_name=_('Notes')
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Active')
    )

    class Meta:
        verbose_name = _('לקוח')
        verbose_name_plural = _('לקוחות')
        ordering = ['name']
        indexes = [
            models.Index(fields=['tenant', 'name']),
            models.Index(fields=['tenant', 'phone']),
            models.Index(fields=['tenant', 'email']),
        ]

    def __str__(self):
        return self.name

    @property
    def total_orders(self):
        """Get total number of orders."""
        return self.orders.count()

    @property
    def total_spent(self):
        """Get total amount spent by customer."""
        return self.orders.filter(
            status='COMPLETED'
        ).aggregate(
            total=models.Sum('total_amount')
        )['total'] or Decimal('0.00')


class Order(BaseModel):
    """
    Sales Order model.
    """
    STATUS_CHOICES = [
        ('DRAFT', _('Draft')),
        ('PENDING', _('Pending')),
        ('PROCESSING', _('Processing')),
        ('COMPLETED', _('Completed')),
        ('CANCELLED', _('Cancelled')),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('UNPAID', _('Unpaid')),
        ('PARTIAL', _('Partially Paid')),
        ('PAID', _('Paid')),
        ('REFUNDED', _('Refunded')),
    ]

    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name=_('Tenant')
    )
    order_number = models.CharField(
        max_length=50,
        unique=True,
        verbose_name=_('Order Number')
    )
    customer = models.ForeignKey(
        Customer,
        on_delete=models.PROTECT,
        related_name='orders',
        verbose_name=_('Customer'),
        null=True,
        blank=True
    )
    customer_name = models.CharField(
        max_length=255,
        verbose_name=_('Customer Name'),
        help_text=_('For walk-in customers without account')
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='DRAFT',
        verbose_name=_('Status')
    )
    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='UNPAID',
        verbose_name=_('Payment Status')
    )
    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name=_('Subtotal')
    )
    discount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name=_('Discount')
    )
    tax = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name=_('Tax')
    )
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name=_('Total Amount')
    )
    paid_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name=_('Paid Amount')
    )
    notes = models.TextField(
        blank=True,
        verbose_name=_('Notes')
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_orders',
        verbose_name=_('Created By')
    )

    class Meta:
        verbose_name = _('הזמנה')
        verbose_name_plural = _('הזמנות')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['tenant', '-created_at']),
            models.Index(fields=['tenant', 'status']),
            models.Index(fields=['tenant', 'order_number']),
            models.Index(fields=['tenant', 'customer']),
        ]

    def __str__(self):
        return f"{self.order_number} - {self.customer_name}"

    def save(self, *args, **kwargs):
        """Auto-generate order number if not set."""
        if not self.order_number:
            # Get last order number for this tenant
            last_order = Order.objects.filter(
                tenant=self.tenant
            ).order_by('-created_at').first()

            if last_order and last_order.order_number:
                try:
                    last_num = int(last_order.order_number.split('-')[-1])
                    new_num = last_num + 1
                except (ValueError, IndexError):
                    new_num = 1
            else:
                new_num = 1

            self.order_number = f"ORD-{new_num:06d}"

        super().save(*args, **kwargs)

    @property
    def balance_due(self):
        """Calculate remaining balance."""
        return self.total_amount - self.paid_amount


class OrderItem(BaseModel):
    """
    Order line items.
    """
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name='order_items',
        verbose_name=_('Tenant')
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name=_('Order')
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name='order_items',
        verbose_name=_('Product')
    )
    quantity = models.IntegerField(
        validators=[MinValueValidator(1)],
        verbose_name=_('Quantity')
    )
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name=_('Unit Price')
    )
    discount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name=_('Discount')
    )
    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name=_('Total Price')
    )

    class Meta:
        verbose_name = _('פריט הזמנה')
        verbose_name_plural = _('פריטי הזמנה')
        ordering = ['id']
        indexes = [
            models.Index(fields=['tenant', 'order']),
            models.Index(fields=['tenant', 'product']),
        ]

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

    def save(self, *args, **kwargs):
        """Calculate total price before saving."""
        self.total_price = (self.unit_price * self.quantity) - self.discount
        super().save(*args, **kwargs)


class Invoice(BaseModel):
    """
    Invoice model for orders.
    """
    STATUS_CHOICES = [
        ('DRAFT', _('Draft')),
        ('SENT', _('Sent')),
        ('PAID', _('Paid')),
        ('CANCELLED', _('Cancelled')),
    ]

    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name='invoices',
        verbose_name=_('Tenant')
    )
    invoice_number = models.CharField(
        max_length=50,
        unique=True,
        verbose_name=_('Invoice Number')
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='invoices',
        verbose_name=_('Order')
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='DRAFT',
        verbose_name=_('Status')
    )
    issue_date = models.DateField(
        auto_now_add=True,
        verbose_name=_('Issue Date')
    )
    due_date = models.DateField(
        verbose_name=_('Due Date')
    )
    notes = models.TextField(
        blank=True,
        verbose_name=_('Notes')
    )

    class Meta:
        verbose_name = _('חשבונית')
        verbose_name_plural = _('חשבוניות')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['tenant', '-created_at']),
            models.Index(fields=['tenant', 'invoice_number']),
            models.Index(fields=['tenant', 'status']),
        ]

    def __str__(self):
        return f"{self.invoice_number} - {self.order.customer_name}"


class Payment(BaseModel):
    """
    Payment records for orders.
    """
    PAYMENT_METHODS = [
        ('CASH', _('Cash')),
        ('CREDIT_CARD', _('Credit Card')),
        ('BANK_TRANSFER', _('Bank Transfer')),
        ('CHECK', _('Check')),
        ('OTHER', _('Other')),
    ]

    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name='payments',
        verbose_name=_('Tenant')
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='payments',
        verbose_name=_('Order')
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name=_('Amount')
    )
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHODS,
        verbose_name=_('Payment Method')
    )
    reference = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_('Reference'),
        help_text=_('Transaction ID, check number, etc.')
    )
    notes = models.TextField(
        blank=True,
        verbose_name=_('Notes')
    )
    received_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='received_payments',
        verbose_name=_('Received By')
    )

    class Meta:
        verbose_name = _('תשלום')
        verbose_name_plural = _('תשלומים')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['tenant', '-created_at']),
            models.Index(fields=['tenant', 'order']),
            models.Index(fields=['tenant', 'payment_method']),
        ]

    def __str__(self):
        return f"{self.order.order_number} - ₪{self.amount}"
