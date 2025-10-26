"""Customer models."""
from django.db import models
from django.core.validators import EmailValidator, RegexValidator
from django.utils.translation import gettext_lazy as _
from django.db.models import F
from django.utils import timezone
from apps.core.models import BaseModel
from apps.accounts.models import Tenant, User
import uuid


class Customer(BaseModel):
    """Customer model for CRM."""

    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name='crm_customers',
        verbose_name=_('Tenant')
    )

    # Personal Information
    first_name = models.CharField(
        max_length=100,
        verbose_name=_('First Name')
    )
    last_name = models.CharField(
        max_length=100,
        verbose_name=_('Last Name')
    )
    email = models.EmailField(
        validators=[EmailValidator()],
        blank=True,
        verbose_name=_('Email')
    )
    phone = models.CharField(
        max_length=20,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message=_('Phone number must be entered in the format: "+999999999". Up to 15 digits allowed.')
            )
        ],
        verbose_name=_('Phone')
    )

    # Address
    address = models.TextField(
        blank=True,
        verbose_name=_('Address')
    )
    city = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_('City')
    )
    postal_code = models.CharField(
        max_length=20,
        blank=True,
        verbose_name=_('Postal Code')
    )

    # Business Information
    company = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_('Company')
    )
    tax_id = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_('Tax ID'),
        help_text=_('מספר עוסק מורשה / ח.פ')
    )

    # Customer Status
    CUSTOMER_TYPES = [
        ('PRIVATE', _('Private Customer')),
        ('BUSINESS', _('Business Customer')),
        ('TREATMENT', _('Treatment Customer')),
        ('VIP', _('VIP')),
    ]
    customer_type = models.CharField(
        max_length=20,
        choices=CUSTOMER_TYPES,
        default='PRIVATE',
        verbose_name=_('Customer Type')
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Active')
    )

    # Profile Image (S3)
    profile_image = models.ImageField(
        upload_to='customer_profiles/',
        null=True,
        blank=True,
        verbose_name=_('Profile Image'),
        help_text=_('Customer profile picture (PRO+ feature)')
    )

    # Birthday & Age
    birth_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('Birth Date'),
        help_text=_('Used for birthday marketing campaigns')
    )

    # Notes & Preferences
    notes = models.TextField(
        blank=True,
        verbose_name=_('General Notes'),
        help_text=_('General customer notes and preferences')
    )

    medical_notes = models.TextField(
        blank=True,
        verbose_name=_('Medical Notes'),
        help_text=_('Allergies, medical conditions, etc.')
    )

    preferences = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_('Preferences'),
        help_text=_('Custom preferences (skin type, preferred products, etc.)')
    )

    # WooCommerce Integration
    woocommerce_customer_id = models.IntegerField(
        null=True,
        blank=True,
        verbose_name=_('WooCommerce Customer ID')
    )

    last_synced_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Last Synced At'),
        help_text=_('Last sync with WooCommerce')
    )

    # Stats (Denormalized) - Purchases
    total_purchases = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name=_('Total Purchases'),
        help_text=_('Total spent on products')
    )

    purchase_count = models.IntegerField(
        default=0,
        verbose_name=_('Purchase Count'),
        help_text=_('Number of product purchases')
    )

    last_purchase_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Last Purchase Date')
    )

    # Stats (Denormalized) - Treatments
    total_treatments = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name=_('Total Treatments'),
        help_text=_('Total spent on treatments')
    )

    treatment_count = models.IntegerField(
        default=0,
        verbose_name=_('Treatment Count'),
        help_text=_('Number of treatments')
    )

    last_treatment_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Last Treatment Date')
    )

    # Legacy - Keep for backward compatibility
    total_orders = models.IntegerField(
        default=0,
        verbose_name=_('Total Orders (Legacy)')
    )
    total_spent = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name=_('Total Spent (Legacy)')
    )
    last_order_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Last Order Date (Legacy)')
    )

    class Meta:
        verbose_name = _('לקוח')
        verbose_name_plural = _('לקוחות')
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['tenant', 'phone'],
                name='unique_phone_per_tenant'
            ),
            models.UniqueConstraint(
                fields=['tenant', 'email'],
                name='unique_email_per_tenant',
                condition=~models.Q(email='')
            ),
        ]
        indexes = [
            models.Index(fields=['tenant', 'email']),
            models.Index(fields=['tenant', 'phone']),
            models.Index(fields=['tenant', 'is_active']),
            models.Index(fields=['tenant', '-total_spent']),
            models.Index(fields=['woocommerce_customer_id']),
            models.Index(fields=['birth_date']),
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self):
        """Return customer's full name."""
        return f"{self.first_name} {self.last_name}"

    @property
    def age(self):
        """Calculate customer age from birth_date."""
        if not self.birth_date:
            return None
        today = timezone.now().date()
        age = today.year - self.birth_date.year
        if today.month < self.birth_date.month or (today.month == self.birth_date.month and today.day < self.birth_date.day):
            age -= 1
        return age

    @property
    def profile_image_url(self):
        """Return profile image URL."""
        if self.profile_image:
            return self.profile_image.url
        return None

    @property
    def average_order_value(self):
        """Calculate average order value."""
        if self.total_orders == 0:
            return 0
        return self.total_spent / self.total_orders


class PlatformIntegration(BaseModel):
    """Store API keys and settings for e-commerce platform integrations."""

    PLATFORM_CHOICES = [
        ('WOOCOMMERCE', _('WooCommerce')),
        ('SHOPIFY', _('Shopify')),
    ]

    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name='platform_integrations',
        verbose_name=_('Tenant')
    )

    platform = models.CharField(
        max_length=20,
        choices=PLATFORM_CHOICES,
        verbose_name=_('Platform')
    )

    # API Configuration
    store_url = models.URLField(
        verbose_name=_('Store URL'),
        help_text=_('e.g., https://mystore.com')
    )

    api_key = models.CharField(
        max_length=255,
        verbose_name=_('API Key')
    )

    api_secret = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_('API Secret'),
        help_text=_('Required for some platforms')
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Active')
    )

    # Sync Settings
    auto_sync_customers = models.BooleanField(
        default=False,
        verbose_name=_('Auto Sync Customers'),
        help_text=_('Automatically import new customers')
    )

    auto_sync_orders = models.BooleanField(
        default=False,
        verbose_name=_('Auto Sync Orders'),
        help_text=_('Automatically import new orders')
    )

    last_sync_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Last Sync At')
    )

    class Meta:
        verbose_name = _('אינטגרציית פלטפורמה')
        verbose_name_plural = _('אינטגרציות פלטפורמה')
        unique_together = [['tenant', 'platform', 'store_url']]
        indexes = [
            models.Index(fields=['tenant', 'is_active']),
        ]

    def __str__(self):
        return f"{self.get_platform_display()} - {self.store_url}"


class ImportedCustomer(BaseModel):
    """Track customers imported from external platforms."""

    integration = models.ForeignKey(
        PlatformIntegration,
        on_delete=models.CASCADE,
        related_name='imported_customers',
        verbose_name=_('Integration')
    )

    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name='imports',
        verbose_name=_('Customer')
    )

    external_id = models.CharField(
        max_length=100,
        verbose_name=_('External ID'),
        help_text=_('Customer ID in the external platform')
    )

    external_data = models.JSONField(
        default=dict,
        verbose_name=_('External Data'),
        help_text=_('Raw data from external platform')
    )

    imported_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Imported At')
    )

    class Meta:
        verbose_name = _('לקוח מיובא')
        verbose_name_plural = _('לקוחות מיובאים')
        unique_together = [['integration', 'external_id']]
        indexes = [
            models.Index(fields=['integration', 'external_id']),
            models.Index(fields=['customer']),
        ]

    def __str__(self):
        return f"{self.customer.full_name} (from {self.integration.get_platform_display()})"


# ==================== TREATMENT MODELS ====================

class TreatmentType(BaseModel):
    """Treatment types/services offered by the business."""

    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name='treatment_types',
        verbose_name=_('Tenant')
    )

    name = models.CharField(
        max_length=255,
        verbose_name=_('Treatment Name'),
        help_text=_('e.g., טיפול פנים, לייזר שיער')
    )

    description = models.TextField(
        blank=True,
        verbose_name=_('Description')
    )

    default_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_('Default Price'),
        help_text=_('Default price for this treatment')
    )

    default_duration_minutes = models.IntegerField(
        null=True,
        blank=True,
        verbose_name=_('Default Duration (minutes)'),
        help_text=_('Estimated duration for scheduling')
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Active')
    )

    class Meta:
        verbose_name = _('סוג טיפול')
        verbose_name_plural = _('סוגי טיפולים')
        ordering = ['name']
        constraints = [
            models.UniqueConstraint(
                fields=['tenant', 'name'],
                name='unique_treatment_name_per_tenant'
            ),
        ]
        indexes = [
            models.Index(fields=['tenant', 'is_active']),
        ]

    def __str__(self):
        return self.name


class StaffMember(BaseModel):
    """Staff members who provide treatments."""

    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name='staff_members',
        verbose_name=_('Tenant')
    )

    full_name = models.CharField(
        max_length=255,
        verbose_name=_('Full Name')
    )

    role = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_('Role'),
        help_text=_('e.g., קוסמטיקאית, מטפלת בייזר')
    )

    phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name=_('Phone')
    )

    email = models.EmailField(
        blank=True,
        verbose_name=_('Email')
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Active')
    )

    class Meta:
        verbose_name = _('מטפל/ת')
        verbose_name_plural = _('מטפלים')
        ordering = ['full_name']
        indexes = [
            models.Index(fields=['tenant', 'is_active']),
        ]

    def __str__(self):
        if self.role:
            return f"{self.full_name} - {self.role}"
        return self.full_name


class Treatment(BaseModel):
    """Treatment history for customers."""

    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name='treatments',
        verbose_name=_('Tenant')
    )

    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name='treatments',
        verbose_name=_('Customer')
    )

    # Treatment Details
    treatment_type = models.ForeignKey(
        TreatmentType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='treatments',
        verbose_name=_('Treatment Type')
    )

    treatment_name = models.CharField(
        max_length=255,
        verbose_name=_('Treatment Name'),
        help_text=_('Snapshot of treatment name at time of treatment')
    )

    treatment_date = models.DateField(
        verbose_name=_('Treatment Date')
    )

    # Staff
    staff_member = models.ForeignKey(
        StaffMember,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='treatments',
        verbose_name=_('Staff Member')
    )

    staff_member_name = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_('Staff Member Name'),
        help_text=_('Snapshot of staff member name at time of treatment')
    )

    # Pricing
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_('Price')
    )

    # Notes
    notes = models.TextField(
        blank=True,
        verbose_name=_('Notes'),
        help_text=_('Treatment notes, observations, recommendations')
    )

    # Metadata
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_treatments',
        verbose_name=_('Created By')
    )

    class Meta:
        verbose_name = _('טיפול')
        verbose_name_plural = _('טיפולים')
        ordering = ['-treatment_date', '-created_at']
        indexes = [
            models.Index(fields=['tenant', '-treatment_date']),
            models.Index(fields=['customer', '-treatment_date']),
            models.Index(fields=['treatment_type']),
            models.Index(fields=['staff_member']),
        ]

    def __str__(self):
        return f"{self.treatment_name} - {self.customer.full_name} ({self.treatment_date})"

    def save(self, *args, **kwargs):
        """Auto-populate snapshot fields and update customer stats."""
        # Snapshot treatment type name
        if self.treatment_type and not self.treatment_name:
            self.treatment_name = self.treatment_type.name

        # Snapshot staff member name
        if self.staff_member and not self.staff_member_name:
            self.staff_member_name = self.staff_member.full_name

        is_new = self.pk is None
        super().save(*args, **kwargs)

        # Update customer stats (only for new treatments)
        if is_new:
            from django.db.models import F
            Customer.objects.filter(pk=self.customer_id).update(
                total_treatments=F('total_treatments') + self.price,
                treatment_count=F('treatment_count') + 1,
                last_treatment_date=self.treatment_date
            )
