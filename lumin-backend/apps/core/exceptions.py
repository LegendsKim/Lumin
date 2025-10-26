# -*- coding: utf-8 -*-
"""
Custom exceptions for Lumin.

These exceptions provide clear error messages for plan limitations
and feature restrictions.
"""
from rest_framework.exceptions import APIException
from rest_framework import status


class PlanLimitExceeded(APIException):
    """
    Exception raised when tenant exceeds their plan limits.
    """
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = 'הגעת למגבלת התוכנית שלך'
    default_code = 'PLAN_LIMIT_EXCEEDED'

    def __init__(self, resource_type: str, max_allowed: int, upgrade_message: str = None):
        """
        Initialize exception with specific resource information.

        Args:
            resource_type: Type of resource (customers, products, staff_members)
            max_allowed: Maximum allowed for current plan
            upgrade_message: Optional custom upgrade message
        """
        detail = {
            'error': 'PLAN_LIMIT_EXCEEDED',
            'resource': resource_type,
            'max_allowed': max_allowed,
            'message': f'הגעת למקסימום {max_allowed} {self._translate_resource(resource_type)} במסלול הנוכחי',
            'upgrade_message': upgrade_message or 'שדרג ל-Pro כדי להסיר את המגבלה'
        }
        super().__init__(detail)

    @staticmethod
    def _translate_resource(resource_type: str) -> str:
        """Translate resource type to Hebrew."""
        translations = {
            'customers': 'לקוחות',
            'products': 'מוצרים',
            'staff_members': 'מטפלים',
        }
        return translations.get(resource_type, resource_type)


class ProFeatureRequired(APIException):
    """
    Exception raised when trying to use a PRO-only feature.
    """
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = 'תכונה זו זמינה רק במסלול Pro'
    default_code = 'PRO_FEATURE_REQUIRED'

    def __init__(self, feature_name: str, feature_description: str = None):
        """
        Initialize exception with feature information.

        Args:
            feature_name: Name of the feature
            feature_description: Optional description of the feature
        """
        detail = {
            'error': 'PRO_FEATURE_REQUIRED',
            'feature': feature_name,
            'message': f'התכונה "{self._translate_feature(feature_name)}" זמינה רק במסלול Pro',
            'description': feature_description,
            'upgrade_message': 'שדרג ל-Pro כדי לגשת לתכונה זו'
        }
        super().__init__(detail)

    @staticmethod
    def _translate_feature(feature_name: str) -> str:
        """Translate feature name to Hebrew."""
        translations = {
            'woocommerce_sync': 'סנכרון מלא עם WooCommerce',
            'sms_marketing': 'שיווק SMS',
            's3_unlimited': 'העלאת קבצים ללא הגבלה',
            'webhooks': 'Webhooks',
        }
        return translations.get(feature_name, feature_name)
