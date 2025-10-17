"""Admin configuration for Sales app."""
from django.contrib import admin
from django.utils.html import format_html
from .models import Customer, Order, OrderItem, Invoice, Payment


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1
    fields = ['product', 'quantity', 'unit_price', 'discount', 'total_price']
    readonly_fields = ['total_price']


class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0
    fields = ['amount', 'payment_method', 'reference', 'received_by', 'created_at']
    readonly_fields = ['created_at']


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone', 'email', 'total_orders', 'total_spent_display', 'is_active', 'tenant']
    list_filter = ['tenant', 'is_active', 'created_at']
    search_fields = ['name', 'phone', 'email', 'tax_id']
    ordering = ['name']
    readonly_fields = ['created_at', 'updated_at', 'total_orders', 'total_spent_display']

    fieldsets = (
        ('מידע בסיסי', {
            'fields': ('tenant', 'name', 'phone', 'email')
        }),
        ('פרטים נוספים', {
            'fields': ('address', 'tax_id', 'notes', 'is_active')
        }),
        ('סטטיסטיקה', {
            'fields': ('total_orders', 'total_spent_display', 'created_at', 'updated_at')
        }),
    )

    def total_spent_display(self, obj):
        return f"₪{obj.total_spent:,.2f}"
    total_spent_display.short_description = 'סה"כ הוצאות'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'customer_name', 'status', 'payment_status',
                    'total_amount_display', 'balance_due_display', 'created_at', 'tenant']
    list_filter = ['tenant', 'status', 'payment_status', 'created_at']
    search_fields = ['order_number', 'customer_name', 'customer__name']
    ordering = ['-created_at']
    readonly_fields = ['order_number', 'created_at', 'updated_at', 'balance_due_display']
    inlines = [OrderItemInline, PaymentInline]

    fieldsets = (
        ('מידע הזמנה', {
            'fields': ('tenant', 'order_number', 'customer', 'customer_name', 'created_by')
        }),
        ('סטטוס', {
            'fields': ('status', 'payment_status')
        }),
        ('פירוט כספי', {
            'fields': ('subtotal', 'discount', 'tax', 'total_amount', 'paid_amount', 'balance_due_display')
        }),
        ('נוסף', {
            'fields': ('notes', 'created_at', 'updated_at')
        }),
    )

    def total_amount_display(self, obj):
        return f"₪{obj.total_amount:,.2f}"
    total_amount_display.short_description = 'סכום כולל'

    def balance_due_display(self, obj):
        balance = obj.balance_due
        color = 'red' if balance > 0 else 'green'
        return format_html(
            '<span style="color: {};">₪{:,.2f}</span>',
            color,
            balance
        )
    balance_due_display.short_description = 'יתרה לתשלום'


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'quantity', 'unit_price', 'discount', 'total_price', 'tenant']
    list_filter = ['tenant', 'created_at']
    search_fields = ['order__order_number', 'product__name']
    ordering = ['-created_at']
    readonly_fields = ['total_price', 'created_at', 'updated_at']


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'order', 'status', 'issue_date', 'due_date', 'tenant']
    list_filter = ['tenant', 'status', 'issue_date', 'due_date']
    search_fields = ['invoice_number', 'order__order_number']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('מידע חשבונית', {
            'fields': ('tenant', 'invoice_number', 'order')
        }),
        ('תאריכים', {
            'fields': ('issue_date', 'due_date')
        }),
        ('פרטים', {
            'fields': ('status', 'notes', 'created_at', 'updated_at')
        }),
    )


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['order', 'amount_display', 'payment_method', 'reference', 'received_by', 'created_at', 'tenant']
    list_filter = ['tenant', 'payment_method', 'created_at']
    search_fields = ['order__order_number', 'reference']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('מידע תשלום', {
            'fields': ('tenant', 'order', 'amount', 'payment_method')
        }),
        ('פרטים', {
            'fields': ('reference', 'notes', 'received_by')
        }),
        ('נוסף', {
            'fields': ('created_at', 'updated_at')
        }),
    )

    def amount_display(self, obj):
        return f"₪{obj.amount:,.2f}"
    amount_display.short_description = 'סכום'
