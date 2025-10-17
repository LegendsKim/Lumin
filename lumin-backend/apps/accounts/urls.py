"""
URL configuration for Accounts app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
# Views will be imported once created
# from .views import AuthViewSet, UserViewSet

app_name = 'accounts'

router = DefaultRouter()
# router.register(r'auth', AuthViewSet, basename='auth')
# router.register(r'users', UserViewSet, basename='users')

urlpatterns = [
    path('', include(router.urls)),
]
