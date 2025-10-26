"""
URL configuration for Accounts app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FeaturesViewSet

app_name = 'accounts'

router = DefaultRouter()
router.register(r'features', FeaturesViewSet, basename='features')

urlpatterns = [
    path('', include(router.urls)),
]
