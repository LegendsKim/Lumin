"""URL configuration for Inventory app."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

app_name = 'inventory'

router = DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),
]
