# -*- coding: utf-8 -*-
"""
Custom views for accounts app.
"""
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.views import OAuth2LoginView, OAuth2CallbackView
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .serializers import PlanFeaturesSerializer


class CustomGoogleOAuth2Adapter(GoogleOAuth2Adapter):
    """Custom Google OAuth2 adapter that skips intermediate page."""
    pass


oauth2_login = OAuth2LoginView.adapter_view(CustomGoogleOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(CustomGoogleOAuth2Adapter)


class FeaturesViewSet(viewsets.ViewSet):
    """
    ViewSet for checking plan features and limits.

    Provides endpoint: GET /api/auth/features/
    Returns all plan information needed by frontend.
    """

    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def check(self, request):
        """
        GET /api/auth/features/check/

        Returns complete plan information including:
        - Current plan and status
        - All limits and current usage
        - Feature availability
        - Whether can add more resources
        """
        serializer = PlanFeaturesSerializer(request.user)
        return Response(serializer.data)

    def list(self, request):
        """
        GET /api/auth/features/

        Same as check() - for convenience.
        """
        serializer = PlanFeaturesSerializer(request.user)
        return Response(serializer.data)
