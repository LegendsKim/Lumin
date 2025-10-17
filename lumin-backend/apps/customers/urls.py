"""URL configuration for Customers app."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

app_name = 'customers'
router = DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),
]
