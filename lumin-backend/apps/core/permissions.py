"""
Custom permissions for plan-based access control.

These permissions check if the tenant has access to specific features
or can add more resources based on their subscription plan.
"""
from rest_framework.permissions import BasePermission
from .exceptions import PlanLimitExceeded, ProFeatureRequired


class PlanBasedPermission(BasePermission):
    """
    Base permission class for plan-based checks.

    Subclasses should override check_permission method.
    """

    def has_permission(self, request, view):
        """
        Check if user has permission based on their plan.

        Only applies to CREATE actions. Other actions are always allowed.
        """
        if request.method != 'POST' or not hasattr(request.user, 'tenant'):
            return True

        return self.check_permission(request, view)

    def check_permission(self, request, view):
        """
        Override this method in subclasses.

        Should raise PlanLimitExceeded or ProFeatureRequired if not allowed.
        """
        return True


class CanAddCustomerPermission(PlanBasedPermission):
    """
    Permission to check if tenant can add more customers.
    """

    def check_permission(self, request, view):
        tenant = request.user.tenant

        if not tenant.can_add_customer():
            raise PlanLimitExceeded(
                resource_type='customers',
                max_allowed=tenant.max_customers
            )

        return True


class CanAddProductPermission(PlanBasedPermission):
    """
    Permission to check if tenant can add more products.
    """

    def check_permission(self, request, view):
        tenant = request.user.tenant

        if not tenant.can_add_product():
            raise PlanLimitExceeded(
                resource_type='products',
                max_allowed=tenant.max_products
            )

        return True


class CanAddStaffMemberPermission(PlanBasedPermission):
    """
    Permission to check if tenant can add more staff members.
    """

    def check_permission(self, request, view):
        tenant = request.user.tenant

        if not tenant.can_add_staff_member():
            raise PlanLimitExceeded(
                resource_type='staff_members',
                max_allowed=tenant.max_staff_members
            )

        return True


class ProFeaturePermission(BasePermission):
    """
    Generic permission to check if tenant has access to a PRO feature.

    Usage:
        Add to view: permission_classes = [ProFeaturePermission]
        Set feature_name in view: pro_feature_name = 'woocommerce_sync'
    """

    def has_permission(self, request, view):
        if not hasattr(request.user, 'tenant'):
            return False

        tenant = request.user.tenant

        # Get feature name from view
        feature_name = getattr(view, 'pro_feature_name', None)

        if not feature_name:
            # If no specific feature defined, just check if PRO
            if tenant.plan != 'PRO':
                raise ProFeatureRequired('unknown', 'פיצ\'ר זה זמין רק במסלול Pro')
            return True

        # Check specific feature
        if not tenant.has_feature(feature_name):
            raise ProFeatureRequired(feature_name)

        return True


class CanUseWooCommerceSyncPermission(BasePermission):
    """
    Permission to check if tenant can use WooCommerce full sync.

    BASIC users can do one-time import, but not full sync with webhooks.
    """

    def has_permission(self, request, view):
        if not hasattr(request.user, 'tenant'):
            return False

        tenant = request.user.tenant

        # Check if this is a full sync request (with webhooks)
        is_full_sync = request.data.get('enable_webhooks', False)

        if is_full_sync and not tenant.can_use_woocommerce_full_sync():
            raise ProFeatureRequired(
                'woocommerce_sync',
                'סנכרון אוטומטי עם Webhooks זמין רק במסלול Pro. במסלול Basic אפשר לבצע ייבוא חד-פעמי בלבד.'
            )

        return True


class CanSendSMSMarketingPermission(BasePermission):
    """
    Permission to check if tenant can send SMS marketing campaigns.

    Note: SMS verification is always allowed, this is only for marketing.
    """

    def has_permission(self, request, view):
        if not hasattr(request.user, 'tenant'):
            return False

        tenant = request.user.tenant

        if not tenant.can_send_sms_marketing():
            raise ProFeatureRequired(
                'sms_marketing',
                'שליחת SMS שיווקי זמינה רק במסלול Pro'
            )

        return True


class CanUploadToS3Permission(BasePermission):
    """
    Permission to check if tenant can upload files to S3.

    BASIC: Up to 5MB per file
    PRO: Unlimited
    """

    def has_permission(self, request, view):
        if not hasattr(request.user, 'tenant'):
            return False

        tenant = request.user.tenant

        # Check file size if file is being uploaded
        if 'image' in request.FILES or 'file' in request.FILES:
            file_obj = request.FILES.get('image') or request.FILES.get('file')
            file_size_mb = file_obj.size / (1024 * 1024)  # Convert to MB

            if not tenant.can_upload_to_s3(file_size_mb):
                raise ProFeatureRequired(
                    's3_unlimited',
                    f'קובץ גדול מדי. במסלול Basic ניתן להעלות קבצים עד {tenant.max_s3_storage_mb}MB. שדרג ל-Pro להעלאה ללא הגבלה.'
                )

        return True
