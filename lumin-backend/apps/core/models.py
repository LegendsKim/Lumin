"""
Core models providing base classes for all apps.
"""
import uuid
from django.db import models


class BaseModel(models.Model):
    """
    Abstract base model providing common fields for all models.

    Fields:
        id: UUID primary key
        created_at: Timestamp when the record was created
        updated_at: Timestamp when the record was last updated
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text='Unique identifier for this record'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text='Timestamp when this record was created'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text='Timestamp when this record was last updated'
    )

    class Meta:
        abstract = True
        ordering = ['-created_at']

    def __str__(self):
        return str(self.id)


class TenantMixin(models.Model):
    """
    Abstract mixin to add tenant foreign key to models.

    CRITICAL SECURITY:
    - Every model using this mixin MUST filter by tenant_id in queries
    - Never trust client-sent tenant_id
    - Always use request.user.tenant for filtering
    """
    tenant = models.ForeignKey(
        'accounts.Tenant',
        on_delete=models.CASCADE,
        related_name='%(class)s_set',
        help_text='The tenant (business) this record belongs to'
    )

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        """
        Override save to ensure tenant is always set.
        Raises ValueError if tenant is not set.
        """
        if not self.tenant_id:
            raise ValueError(
                f'{self.__class__.__name__} cannot be saved without a tenant. '
                'This is a critical security requirement.'
            )
        super().save(*args, **kwargs)
