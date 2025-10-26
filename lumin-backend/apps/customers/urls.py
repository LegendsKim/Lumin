"""URL configuration for Customers app."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CustomerViewSet,
    PlatformIntegrationViewSet,
    ImportedCustomerViewSet,
    TreatmentTypeViewSet,
    StaffMemberViewSet,
    TreatmentViewSet,
    customers_page,
    customer_profile_page
)

app_name = 'customers'
router = DefaultRouter()
router.register(r'customers', CustomerViewSet, basename='customer')
router.register(r'integrations', PlatformIntegrationViewSet, basename='integration')
router.register(r'imported-customers', ImportedCustomerViewSet, basename='imported-customer')
router.register(r'treatment-types', TreatmentTypeViewSet, basename='treatment-type')
router.register(r'staff-members', StaffMemberViewSet, basename='staff-member')
router.register(r'treatments', TreatmentViewSet, basename='treatment')

urlpatterns = [
    path('', customers_page, name='customers_page'),
    path('<str:customer_id>/', customer_profile_page, name='customer_profile'),
    path('api/', include(router.urls)),
]
