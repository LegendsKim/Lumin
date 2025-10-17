"""URL configuration for Sales app."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

app_name = 'sales'
router = DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),
]
