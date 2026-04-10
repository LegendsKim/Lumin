"""
Tenant business logic and service layer.
"""
from django.conf import settings

# Use local imports in methods to avoid circular dependencies if needed,
# but since this is a service, we can import models at the top if they don't import this service.
# However, Product/Customer models import Tenant, so we should be careful.
# This Service depends on Tenant, Product, Customer.
# Tenant depends on... nothing (BaseModel).
# Product depends on Tenant.
# So imports here are safe: Service -> (Tenant, Product)
# Tenant -> (nothing)
# Product -> Tenant

class TenantService:
    """
    Service class for handling tenant-related business logic and limits.
    """
    
    def __init__(self, tenant):
        """
        Initialize the service with a tenant instance.
        
        Args:
            tenant: The Tenant instance to operate on
        """
        self.tenant = tenant

    def can_add_product(self) -> bool:
        """
        Check if tenant can add more products.

        Returns:
            bool: True if under limit
        """
        if self.tenant.plan == 'PRO':
            return True
            
        from apps.inventory.models import Product
        current_count = Product.objects.filter(tenant=self.tenant).count()
        return current_count < self.tenant.max_products

    def can_add_customer(self) -> bool:
        """
        Check if tenant can add more customers.

        Returns:
            bool: True if under limit
        """
        if self.tenant.plan == 'PRO':
            return True
            
        from apps.customers.models import Customer
        current_count = Customer.objects.filter(tenant=self.tenant).count()
        return current_count < self.tenant.max_customers

    def can_add_staff_member(self) -> bool:
        """
        Check if tenant can add more staff members.

        Returns:
            bool: True if under limit
        """
        if self.tenant.plan == 'PRO':
            return True
            
        from apps.customers.models import StaffMember
        current_count = StaffMember.objects.filter(tenant=self.tenant, is_active=True).count()
        return current_count < self.tenant.max_staff_members

    def can_upload_to_s3(self, file_size_mb: float = 0) -> bool:
        """
        Check if tenant can upload files to S3.

        Args:
            file_size_mb: Size of file to upload in MB

        Returns:
            bool: True if under storage limit
        """
        if self.tenant.plan == 'PRO':
            return True
        return file_size_mb <= self.tenant.max_s3_storage_mb

    def can_use_woocommerce_full_sync(self) -> bool:
        return self.tenant.plan == 'PRO'

    def can_send_sms_marketing(self) -> bool:
        return self.tenant.plan == 'PRO'

    def has_feature(self, feature_name: str) -> bool:
        """
        Generic method to check if tenant has access to a feature.

        Args:
            feature_name: Name of the feature to check

        Returns:
            bool: True if tenant has access to feature
        """
        feature_map = {
            'woocommerce_sync': self.can_use_woocommerce_full_sync(),
            'sms_marketing': self.can_send_sms_marketing(),
            's3_uploads': self.tenant.plan in ['BASIC', 'PRO'],
            'unlimited_customers': self.tenant.plan == 'PRO',
            'unlimited_products': self.tenant.plan == 'PRO',
            'unlimited_staff': self.tenant.plan == 'PRO',
        }
        return feature_map.get(feature_name, False)

    def get_current_counts(self) -> dict:
        """
        Get current resource counts for this tenant.

        Returns:
            dict: Current counts of customers, products, staff members
        """
        from apps.customers.models import Customer, StaffMember
        from apps.inventory.models import Product

        return {
            'customers': Customer.objects.filter(tenant=self.tenant).count(),
            'products': Product.objects.filter(tenant=self.tenant).count(),
            'staff_members': StaffMember.objects.filter(tenant=self.tenant, is_active=True).count(),
        }

    def check_and_lock_if_over_limit(self) -> bool:
        """
        Check if tenant has exceeded plan limits and lock account if necessary.
        
        Returns:
            bool: True if account was locked, False otherwise
        """
        # Only applies to BASIC plan
        if self.tenant.plan != 'BASIC':
            return False

        # If already locked, return True
        if self.tenant.is_locked():
            return True

        counts = self.get_current_counts()

        # Check if any limit is exceeded
        over_limit = (
            counts['customers'] > self.tenant.max_customers or
            counts['products'] > self.tenant.max_products or
            counts['staff_members'] > self.tenant.max_staff_members
        )

        if over_limit:
            self.tenant.account_status = 'LOCKED_BASIC'
            self.tenant.save(update_fields=['account_status'])
            return True

        return False
