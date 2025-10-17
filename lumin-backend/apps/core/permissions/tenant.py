"""
Tenant-aware permission classes for Django REST Framework.

CRITICAL SECURITY:
These permissions ensure that users can only access data belonging to their tenant.
"""
from rest_framework import permissions


class IsTenantMember(permissions.BasePermission):
    """
    Permission to check if user belongs to the tenant that owns the object.

    For list views: Automatically handled by TenantQuerySetMixin
    For detail views: Verifies object.tenant == request.user.tenant

    Usage:
        class ProductViewSet(viewsets.ModelViewSet):
            permission_classes = [IsTenantMember]
    """

    message = 'אין לך הרשאה לגשת למשאב זה'

    def has_permission(self, request, view):
        """
        Check if user is authenticated and has a tenant.

        Args:
            request: DRF Request object
            view: View being accessed

        Returns:
            bool: True if user has tenant access
        """
        # User must be authenticated
        if not request.user or not request.user.is_authenticated:
            return False

        # User must have a tenant
        if not hasattr(request, 'tenant') or not request.tenant:
            return False

        return True

    def has_object_permission(self, request, view, obj):
        """
        Check if object belongs to user's tenant.

        Args:
            request: DRF Request object
            view: View being accessed
            obj: Object being accessed

        Returns:
            bool: True if object belongs to user's tenant
        """
        # Check if object has tenant attribute
        if not hasattr(obj, 'tenant'):
            # If no tenant attribute, allow (might be a non-tenant model)
            return True

        # Verify object belongs to user's tenant
        return obj.tenant == request.tenant


class IsAdmin(permissions.BasePermission):
    """
    Permission to check if user is an admin of their tenant.

    Admins have full access to all features including financial data.

    Usage:
        class FinancialReportView(APIView):
            permission_classes = [IsAdmin]
    """

    message = 'רק מנהלים יכולים לבצע פעולה זו'

    def has_permission(self, request, view):
        """
        Check if user is an admin.

        Args:
            request: DRF Request object
            view: View being accessed

        Returns:
            bool: True if user is admin
        """
        if not request.user or not request.user.is_authenticated:
            return False

        return request.user.role == 'ADMIN'


class CanViewFinancials(permissions.BasePermission):
    """
    Permission to check if user can view financial data (cost, profit).

    Only admins can see:
    - cost_price
    - profit_margin
    - total_profit
    - line_profit

    Usage:
        @action(detail=False, permission_classes=[CanViewFinancials])
        def profit_report(self, request):
            ...
    """

    message = 'אין לך הרשאה לצפות במידע פיננסי'

    def has_permission(self, request, view):
        """
        Check if user can view financial data.

        Args:
            request: DRF Request object
            view: View being accessed

        Returns:
            bool: True if user can view financials
        """
        if not request.user or not request.user.is_authenticated:
            return False

        # Check if user has can_view_financials method
        if hasattr(request.user, 'can_view_financials'):
            return request.user.can_view_financials()

        # Fallback to role check
        return request.user.role == 'ADMIN'
