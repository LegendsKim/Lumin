"""
Supabase JWT Authentication Backend for Django REST Framework.

Validates JWT tokens issued by Supabase Auth, and maps them
to the local Django User model (creating users on first login).
"""
import jwt
import requests
from functools import lru_cache
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


@lru_cache(maxsize=1)
def get_supabase_jwks():
    """
    Fetch Supabase's JWKS (public keys) for JWT verification.
    Cached to avoid repeated HTTP calls.
    """
    supabase_url = getattr(settings, 'SUPABASE_URL', None)
    if not supabase_url:
        raise AuthenticationFailed('SUPABASE_URL not configured in Django settings.')

    jwks_url = f"{supabase_url}/auth/v1/.well-known/jwks.json"
    try:
        response = requests.get(jwks_url, timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.error(f"Failed to fetch Supabase JWKS: {e}")
        raise AuthenticationFailed('Unable to verify authentication. Please try again.')


class SupabaseJWTAuthentication(BaseAuthentication):
    """
    Authenticate requests using Supabase JWT tokens.

    Usage: Include this in REST_FRAMEWORK['DEFAULT_AUTHENTICATION_CLASSES']

    Flow:
    1. Frontend sends: Authorization: Bearer <supabase_jwt>
    2. This backend validates the JWT using Supabase's public keys
    3. If the user doesn't exist in Django, we create them (first login)
    4. Returns (user, token_payload)
    """

    def authenticate(self, request):
        """Extract and validate the JWT from the Authorization header."""
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')

        if not auth_header.startswith('Bearer '):
            return None  # Let other authentication backends handle it

        token = auth_header[7:]  # Remove 'Bearer ' prefix

        try:
            payload = self._verify_token(token)
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Token has expired. Please log in again.')
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid JWT token: {e}")
            raise AuthenticationFailed('Invalid authentication token.')

        user = self._get_or_create_user(payload)
        return (user, payload)

    def _verify_token(self, token):
        """
        Verify JWT using Supabase's JWT secret.
        Uses HS256 with the Supabase JWT secret for simplicity.
        """
        jwt_secret = getattr(settings, 'SUPABASE_JWT_SECRET', None)
        if not jwt_secret:
            raise AuthenticationFailed('SUPABASE_JWT_SECRET not configured.')

        return jwt.decode(
            token,
            jwt_secret,
            algorithms=['HS256'],
            audience='authenticated',
            options={
                'verify_exp': True,
                'verify_aud': True,
            }
        )

    def _get_or_create_user(self, payload):
        """
        Get or create a Django user based on the Supabase JWT payload.

        JWT payload contains:
        - sub: Supabase user UUID
        - email: User's email
        - user_metadata: {full_name, avatar_url, ...}
        """
        supabase_uid = payload.get('sub')
        email = payload.get('email', '')
        user_metadata = payload.get('user_metadata', {})

        if not supabase_uid:
            raise AuthenticationFailed('Invalid token: missing user ID.')

        try:
            # Try to find existing user by email
            user = User.objects.get(email=email)

            # Update Supabase UID if not set
            if not user.supabase_uid:
                user.supabase_uid = supabase_uid
                user.save(update_fields=['supabase_uid'])

            return user
        except User.DoesNotExist:
            pass

        try:
            # Try to find by Supabase UID (in case email changed)
            user = User.objects.get(supabase_uid=supabase_uid)
            return user
        except (User.DoesNotExist, Exception):
            pass

        # Create new user on first login
        full_name = user_metadata.get('full_name', email.split('@')[0])
        name_parts = full_name.split(' ', 1)
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ''

        logger.info(f"Creating new user from Supabase: {email}")

        user = User.objects.create(
            email=email,
            first_name=first_name,
            last_name=last_name,
            supabase_uid=supabase_uid,
            is_active=True,
        )

        return user

    def authenticate_header(self, request):
        """Return the WWW-Authenticate header for 401 responses."""
        return 'Bearer realm="api"'
