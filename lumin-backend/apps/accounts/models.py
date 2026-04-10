"""
Account models: Tenant and User.

CRITICAL: User model extends AbstractUser with tenant foreign key.
All other models in the system will reference this tenant.
"""
import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
from apps.core.models import BaseModel


class Tenant(BaseModel):
    """
    Tenant model representing a business/organization.

    Each tenant is completely isolated from others.
    This is the foundation of the multi-tenant architecture.

    Fields:
        business_name: Name of the business
        owner_email: Email of the business owner
        owner_phone: Phone number of the business owner
        phone_verified: Whether the phone has been verified
        logo: Business logo (optional)
        plan: Subscription plan (BASIC or PRO)
        stripe_customer_id: Stripe customer ID for billing
        subscription_expires_at: When subscription expires
        is_active: Whether the tenant account is active
    """

    PLAN_CHOICES = [
        ('BASIC', 'Basic'),
        ('PRO', 'Pro'),
    ]

    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('LOCKED_BASIC', 'Locked - Over Limit'),
    ]

    business_name = models.CharField(
        max_length=255,
        verbose_name=_('Business Name'),
        help_text=_('Name of the business or clinic')
    )

    owner_email = models.EmailField(
        unique=True,
        verbose_name=_('Owner Email'),
        help_text=_('Email address of the business owner')
    )

    owner_phone = models.CharField(
        max_length=20,
        verbose_name=_('Owner Phone'),
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message=_('Phone number must be entered in the format: "+999999999". Up to 15 digits allowed.')
            )
        ],
        help_text=_('Phone number of the business owner')
    )

    phone_verified = models.BooleanField(
        default=False,
        verbose_name=_('Phone Verified'),
        help_text=_('Whether the phone number has been verified via SMS')
    )

    logo = models.ImageField(
        upload_to='tenant_logos/',
        null=True,
        blank=True,
        verbose_name=_('Business Logo'),
        help_text=_('Logo of the business (optional)')
    )

    plan = models.CharField(
        max_length=10,
        choices=PLAN_CHOICES,
        default='BASIC',
        verbose_name=_('Subscription Plan'),
        help_text=_('Current subscription plan')
    )

    stripe_customer_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name=_('Stripe Customer ID'),
        help_text=_('Stripe customer ID for billing')
    )

    subscription_expires_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Subscription Expires At'),
        help_text=_('When the current subscription expires')
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Is Active'),
        help_text=_('Whether this tenant account is active')
    )

    account_status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='ACTIVE',
        verbose_name=_('Account Status'),
        help_text=_('Account status (ACTIVE or LOCKED_BASIC if over limits)')
    )

    class Meta:
        verbose_name = _('Tenant')
        verbose_name_plural = _('Tenants')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['owner_email']),
            models.Index(fields=['is_active', 'plan']),
        ]

    def __str__(self):
        return f'{self.business_name} ({self.plan})'

    @property
    def max_products(self) -> int:
        """
        Get maximum number of products allowed for this plan.

        Returns:
            int: Maximum products (10 for BASIC, unlimited for PRO)
        """
        return 10 if self.plan == 'BASIC' else float('inf')

    @property
    def max_customers(self) -> int:
        """
        Get maximum number of customers allowed for this plan.

        Returns:
            int: Maximum customers (10 for BASIC, unlimited for PRO)
        """
        return 10 if self.plan == 'BASIC' else float('inf')

    @property
    def max_staff_members(self) -> int:
        """
        Get maximum number of staff members allowed for this plan.

        Returns:
            int: Maximum staff members (1 for BASIC, unlimited for PRO)
        """
        return 1 if self.plan == 'BASIC' else float('inf')

    @property
    def max_s3_storage_mb(self) -> int:
        """
        Get maximum S3 storage in MB allowed for this plan.

        Returns:
            int: Maximum storage (5MB for BASIC, unlimited for PRO)
        """
        return 5 if self.plan == 'BASIC' else float('inf')



    def is_locked(self) -> bool:
        """
        Check if tenant account is locked due to exceeding limits.

        Returns:
            bool: True if account is locked
        """
        return self.account_status == 'LOCKED_BASIC'



    def unlock_account(self):
        """
        Unlock account (called after upgrade to PRO or after reducing resources).
        """
        if self.account_status == 'LOCKED_BASIC':
            self.account_status = 'ACTIVE'
            self.save(update_fields=['account_status'])


class User(AbstractUser, BaseModel):
    """
    Custom User model extending Django's AbstractUser.

    CRITICAL CHANGES:
    - Uses UUID as primary key (inherited from BaseModel)
    - Email is the USERNAME_FIELD (not username)
    - Each user belongs to exactly one tenant
    - Supports Google OAuth via google_sub field
    - Role-based access control (ADMIN vs BASIC_STAFF)

    Fields:
        tenant: The tenant this user belongs to
        email: Email address (unique, used for login)
        phone: Phone number (optional)
        phone_verified: Whether phone is verified
        role: User role (ADMIN or BASIC_STAFF)
        google_sub: Google OAuth subject identifier
        is_active: Whether user account is active
        last_login: Last login timestamp
    """

    ROLE_CHOICES = [
        ('ADMIN', 'Admin'),
        ('BASIC_STAFF', 'Basic Staff'),
    ]

    # Remove username field (we use email instead)
    username = None

    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name='users',
        null=True,  # Can be null during initial registration
        blank=True,
        verbose_name=_('Tenant'),
        help_text=_('The tenant (business) this user belongs to')
    )

    email = models.EmailField(
        unique=True,
        verbose_name=_('Email Address'),
        help_text=_('Email address (used for login)')
    )

    phone = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name=_('Phone Number'),
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message=_('Phone number must be entered in the format: "+999999999". Up to 15 digits allowed.')
            )
        ]
    )

    phone_verified = models.BooleanField(
        default=False,
        verbose_name=_('Phone Verified'),
        help_text=_('Whether the phone number has been verified via SMS')
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='BASIC_STAFF',
        verbose_name=_('Role'),
        help_text=_('User role (Admin or Basic Staff)')
    )

    google_sub = models.CharField(
        max_length=255,
        unique=True,
        null=True,
        blank=True,
        verbose_name=_('Google Subject ID'),
        help_text=_('Google OAuth subject identifier')
    )

    supabase_uid = models.CharField(
        max_length=255,
        unique=True,
        null=True,
        blank=True,
        verbose_name=_('Supabase User ID'),
        help_text=_('Supabase Auth user identifier (UUID)')
    )

    onboarding_completed = models.BooleanField(
        default=False,
        verbose_name=_('Onboarding Completed'),
        help_text=_('Whether the user has completed the onboarding process')
    )

    # Use email as the username field
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  # Remove email from required fields since it's the username

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['tenant', 'is_active']),
            models.Index(fields=['google_sub']),
            models.Index(fields=['supabase_uid']),
        ]

    def __str__(self):
        return f'{self.email} ({self.get_role_display()})'

    def can_view_financials(self) -> bool:
        """
        Check if user can view financial data (cost, profit).

        Returns:
            bool: True if user is ADMIN
        """
        return self.role == 'ADMIN'

    def is_admin(self) -> bool:
        """
        Check if user is an admin.

        Returns:
            bool: True if user role is ADMIN
        """
        return self.role == 'ADMIN'

    def save(self, *args, **kwargs):
        """
        Override save to set first/last name from email if not provided.
        """
        if not self.first_name and not self.last_name:
            # Extract name from email
            email_name = self.email.split('@')[0]
            self.first_name = email_name.capitalize()

        super().save(*args, **kwargs)
