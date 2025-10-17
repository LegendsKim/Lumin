"""
Tenant-aware mixin for ViewSets.

CRITICAL SECURITY:
This mixin automatically filters querysets by tenant, preventing data leakage.
"""
import logging

logger = logging.getLogger(__name__)


class TenantQuerySetMixin:
    """
    Mixin to automatically filter QuerySets by tenant.

    MUST be used with all ViewSets that deal with tenant-specific data.

    Usage:
        class ProductViewSet(TenantQuerySetMixin, viewsets.ModelViewSet):
            queryset = Product.objects.all()
            serializer_class = ProductSerializer

    The get_queryset() method will automatically filter by request.tenant.
    """

    def get_queryset(self):
        """
        Override get_queryset to filter by tenant.

        Returns:
            QuerySet: Filtered queryset for the current tenant

        Raises:
            ValueError: If no tenant context is available
        """
        # Get the base queryset
        queryset = super().get_queryset() if hasattr(super(), 'get_queryset') else self.queryset

        # Check if request has tenant
        if not hasattr(self.request, 'tenant') or not self.request.tenant:
            logger.warning(
                f'No tenant context in request for {self.__class__.__name__}. '
                'Returning empty queryset.'
            )
            return queryset.none()

        # Filter by tenant
        if hasattr(queryset.model, 'tenant'):
            filtered_queryset = queryset.filter(tenant=self.request.tenant)
            logger.debug(
                f'Filtered {queryset.model.__name__} queryset by tenant: '
                f'{self.request.tenant.business_name} (ID: {self.request.tenant.id})'
            )
            return filtered_queryset
        else:
            logger.warning(
                f'Model {queryset.model.__name__} does not have tenant field. '
                'Returning full queryset (potential security issue!).'
            )
            return queryset

    def perform_create(self, serializer):
        """
        Override perform_create to automatically set tenant on creation.

        Args:
            serializer: Serializer instance with validated data
        """
        # Check if model has tenant field
        if hasattr(serializer.Meta.model, 'tenant'):
            if not self.request.tenant:
                raise ValueError('Cannot create object without tenant context')

            # Set tenant and created_by/updated_by if applicable
            save_kwargs = {'tenant': self.request.tenant}

            if hasattr(serializer.Meta.model, 'created_by'):
                save_kwargs['created_by'] = self.request.user

            if hasattr(serializer.Meta.model, 'updated_by'):
                save_kwargs['updated_by'] = self.request.user

            serializer.save(**save_kwargs)
            logger.info(
                f'Created {serializer.Meta.model.__name__} for tenant: '
                f'{self.request.tenant.business_name}'
            )
        else:
            serializer.save()

    def perform_update(self, serializer):
        """
        Override perform_update to set updated_by.

        Args:
            serializer: Serializer instance with validated data
        """
        save_kwargs = {}

        if hasattr(serializer.Meta.model, 'updated_by'):
            save_kwargs['updated_by'] = self.request.user

        serializer.save(**save_kwargs)
        logger.info(
            f'Updated {serializer.Meta.model.__name__} '
            f'(ID: {serializer.instance.id})'
        )
