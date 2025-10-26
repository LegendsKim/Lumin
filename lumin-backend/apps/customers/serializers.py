"""Serializers for Customers app."""
from rest_framework import serializers
from .models import (
    Customer, PlatformIntegration, ImportedCustomer,
    TreatmentType, StaffMember, Treatment
)


class PlatformIntegrationSerializer(serializers.ModelSerializer):
    """Serializer for Platform Integration."""

    platform_display = serializers.CharField(source='get_platform_display', read_only=True)

    class Meta:
        model = PlatformIntegration
        fields = [
            'id', 'platform', 'platform_display', 'store_url', 'api_key',
            'api_secret', 'is_active', 'auto_sync_customers', 'auto_sync_orders',
            'last_sync_at', 'created_at', 'updated_at'
        ]
        extra_kwargs = {
            'api_key': {'write_only': True},
            'api_secret': {'write_only': True}
        }


class ImportedCustomerSerializer(serializers.ModelSerializer):
    """Serializer for Imported Customer."""

    customer_name = serializers.CharField(source='customer.full_name', read_only=True)
    platform = serializers.CharField(source='integration.get_platform_display', read_only=True)

    class Meta:
        model = ImportedCustomer
        fields = [
            'id', 'integration', 'customer', 'customer_name', 'platform',
            'external_id', 'external_data', 'imported_at'
        ]
        read_only_fields = ['imported_at']


class CustomerListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for customer lists."""

    full_name = serializers.ReadOnlyField()
    age = serializers.ReadOnlyField()
    profile_image_url = serializers.SerializerMethodField()
    customer_type_display = serializers.CharField(source='get_customer_type_display', read_only=True)

    class Meta:
        model = Customer
        fields = [
            'id', 'first_name', 'last_name', 'full_name', 'email', 'phone',
            'profile_image_url', 'birth_date', 'age',
            'company', 'customer_type', 'customer_type_display', 'is_active',
            'total_purchases', 'purchase_count', 'last_purchase_date',
            'total_treatments', 'treatment_count', 'last_treatment_date',
            'created_at'
        ]

    def get_profile_image_url(self, obj):
        """Return profile image URL."""
        if obj.profile_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.profile_image.url)
        return None


class CustomerDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for single customer with full history."""

    full_name = serializers.ReadOnlyField()
    age = serializers.ReadOnlyField()
    profile_image_url = serializers.SerializerMethodField()
    customer_type_display = serializers.CharField(source='get_customer_type_display', read_only=True)
    recent_treatments = serializers.SerializerMethodField()
    recent_orders = serializers.SerializerMethodField()

    class Meta:
        model = Customer
        fields = [
            'id', 'first_name', 'last_name', 'full_name', 'email', 'phone',
            'profile_image_url', 'birth_date', 'age',
            'address', 'city', 'postal_code', 'company', 'tax_id',
            'customer_type', 'customer_type_display', 'is_active',
            'notes', 'medical_notes', 'preferences',
            'total_purchases', 'purchase_count', 'last_purchase_date',
            'total_treatments', 'treatment_count', 'last_treatment_date',
            'woocommerce_customer_id', 'last_synced_at',
            'recent_treatments', 'recent_orders',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'full_name', 'age', 'profile_image_url',
            'total_purchases', 'purchase_count', 'last_purchase_date',
            'total_treatments', 'treatment_count', 'last_treatment_date',
            'created_at', 'updated_at'
        ]

    def get_profile_image_url(self, obj):
        """Return profile image URL."""
        if obj.profile_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.profile_image.url)
        return None

    def get_recent_treatments(self, obj):
        """Return recent 10 treatments."""
        treatments = obj.treatments.all().order_by('-treatment_date')[:10]
        return TreatmentSerializer(treatments, many=True).data

    def get_recent_orders(self, obj):
        """Return recent 10 orders (from sales app)."""
        # This will be implemented when sales app is ready
        # from apps.sales.serializers import OrderListSerializer
        # orders = obj.orders.all().order_by('-created_at')[:10]
        # return OrderListSerializer(orders, many=True).data
        return []


class CustomerCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating customers."""

    class Meta:
        model = Customer
        fields = [
            'id', 'first_name', 'last_name', 'email', 'phone',
            'birth_date',
            'address', 'city', 'postal_code', 'company', 'tax_id',
            'customer_type', 'is_active',
            'notes', 'medical_notes', 'preferences'
        ]
        read_only_fields = ['id']

    def create(self, validated_data):
        """Create customer with tenant assignment and plan limit check."""
        request = self.context['request']
        validated_data['tenant'] = request.user.tenant

        # Check plan limits
        tenant = request.user.tenant
        current_count = Customer.objects.filter(tenant=tenant).count()

        # Get max customers from tenant plan settings
        # For now, set defaults: BASIC=100, PRO=1000, ENTERPRISE=unlimited
        plan_limits = {
            'BASIC': 100,
            'PRO': 1000,
            'ENTERPRISE': 999999
        }

        max_customers = plan_limits.get(tenant.plan, 100)

        if current_count >= max_customers:
            raise serializers.ValidationError({
                'limit_reached': f'הגעת למגבלת {max_customers} לקוחות במסלול {tenant.plan}.'
            })

        customer = super().create(validated_data)

        # Async: Sync to WooCommerce if enabled
        # from apps.customers.tasks import sync_customer_to_woocommerce
        # if hasattr(tenant, 'woocommerce_sync_enabled') and tenant.woocommerce_sync_enabled:
        #     sync_customer_to_woocommerce.delay(customer.id)

        return customer


# ==================== TREATMENT SERIALIZERS ====================

class TreatmentTypeSerializer(serializers.ModelSerializer):
    """Serializer for Treatment Types."""

    class Meta:
        model = TreatmentType
        fields = [
            'id', 'name', 'description',
            'default_price', 'default_duration_minutes',
            'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

    def create(self, validated_data):
        """Create treatment type with tenant assignment."""
        request = self.context['request']
        validated_data['tenant'] = request.user.tenant
        return super().create(validated_data)


class StaffMemberSerializer(serializers.ModelSerializer):
    """Serializer for Staff Members."""

    class Meta:
        model = StaffMember
        fields = [
            'id', 'full_name', 'role',
            'phone', 'email', 'is_active',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']

    def create(self, validated_data):
        """Create staff member with tenant assignment."""
        request = self.context['request']
        validated_data['tenant'] = request.user.tenant
        return super().create(validated_data)


class TreatmentSerializer(serializers.ModelSerializer):
    """Serializer for Treatments."""

    treatment_type_name = serializers.CharField(source='treatment_name', read_only=True)
    staff_member_display = serializers.CharField(source='staff_member_name', read_only=True)
    customer_name = serializers.CharField(source='customer.full_name', read_only=True)

    class Meta:
        model = Treatment
        fields = [
            'id', 'customer', 'customer_name',
            'treatment_type', 'treatment_type_name',
            'treatment_date',
            'staff_member', 'staff_member_display',
            'price', 'notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def create(self, validated_data):
        """Create treatment with tenant assignment and snapshot fields."""
        request = self.context['request']
        validated_data['tenant'] = request.user.tenant
        validated_data['created_by'] = request.user

        # Snapshot treatment type name
        treatment_type = validated_data.get('treatment_type')
        if treatment_type and 'treatment_name' not in validated_data:
            validated_data['treatment_name'] = treatment_type.name

        # Snapshot staff member name
        staff_member = validated_data.get('staff_member')
        if staff_member and 'staff_member_name' not in validated_data:
            validated_data['staff_member_name'] = staff_member.full_name

        return super().create(validated_data)
