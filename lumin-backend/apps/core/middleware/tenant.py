"""
Tenant middleware to inject tenant context into every request.

CRITICAL SECURITY COMPONENT:
This middleware ensures that every authenticated request has access to the
user's tenant, preventing data leakage between different tenants.
"""
import logging

logger = logging.getLogger(__name__)


class TenantMiddleware:
    """
    Middleware to inject tenant into request object.

    For authenticated users, sets request.tenant to the user's tenant.
    For anonymous users, sets request.tenant to None.

    Usage in views:
        if request.tenant:
            products = Product.objects.filter(tenant=request.tenant)
    """

    def __init__(self, get_response):
        """Initialize middleware."""
        self.get_response = get_response

    def __call__(self, request):
        """
        Process each request to inject tenant context.

        Args:
            request: Django HttpRequest object

        Returns:
            HttpResponse: Response from the next middleware/view
        """
        # Initialize tenant as None
        request.tenant = None

        # If user is authenticated and has a tenant, set it
        if request.user and request.user.is_authenticated:
            try:
                if hasattr(request.user, 'tenant') and request.user.tenant:
                    request.tenant = request.user.tenant
                    logger.debug(
                        f'Tenant context set: {request.tenant.business_name} '
                        f'(ID: {request.tenant.id}) for user {request.user.email}'
                    )
                else:
                    # Auto-create tenant for users without one
                    logger.warning(
                        f'Authenticated user {request.user.email} has no tenant assigned - creating one'
                    )
                    from apps.accounts.models import Tenant

                    # Create tenant for this user
                    tenant = Tenant.objects.create(
                        business_name=f"{request.user.first_name} {request.user.last_name}'s Business",
                        owner_email=request.user.email,
                        owner_phone=request.user.phone if request.user.phone else '+972500000000',
                        plan='BASIC'
                    )

                    # Assign to user
                    request.user.tenant = tenant
                    request.user.save()
                    request.tenant = tenant

                    logger.info(
                        f'✅ Auto-created tenant "{tenant.business_name}" for user {request.user.email}'
                    )
            except Exception as e:
                logger.error(f'Error setting tenant context: {e}')
                request.tenant = None

        # Continue processing the request
        response = self.get_response(request)
        return response

    def process_exception(self, request, exception):
        """
        Log any exceptions that occur during request processing.

        Args:
            request: Django HttpRequest object
            exception: Exception that was raised
        """
        logger.error(
            f'Exception in request for tenant {getattr(request, "tenant", None)}: {exception}'
        )
        return None
