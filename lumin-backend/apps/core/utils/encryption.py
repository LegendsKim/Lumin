"""
Encryption utilities for sensitive data.

Uses Fernet (AES-256) for symmetric encryption of API keys and other secrets.
"""
import base64
import logging
from cryptography.fernet import Fernet
from django.conf import settings

logger = logging.getLogger(__name__)


def get_encryption_key() -> bytes:
    """
    Get or generate encryption key from Django SECRET_KEY.

    Returns:
        bytes: Fernet encryption key

    Note:
        In production, consider using a dedicated encryption key
        stored in environment variables, separate from SECRET_KEY.
    """
    # Use first 32 bytes of SECRET_KEY and base64 encode
    key = base64.urlsafe_b64encode(settings.SECRET_KEY[:32].encode().ljust(32)[:32])
    return key


def encrypt_api_key(plain_text: str) -> str:
    """
    Encrypt a plaintext API key or sensitive string.

    Args:
        plain_text: The plaintext string to encrypt

    Returns:
        str: Encrypted string (base64 encoded)

    Example:
        >>> encrypted = encrypt_api_key("my-secret-api-key")
        >>> print(encrypted)
        'gAAAAABh...'
    """
    try:
        fernet = Fernet(get_encryption_key())
        encrypted = fernet.encrypt(plain_text.encode())
        return encrypted.decode()
    except Exception as e:
        logger.error(f'Error encrypting data: {e}')
        raise


def decrypt_api_key(encrypted_text: str) -> str:
    """
    Decrypt an encrypted API key or sensitive string.

    Args:
        encrypted_text: The encrypted string (base64 encoded)

    Returns:
        str: Decrypted plaintext string

    Raises:
        cryptography.fernet.InvalidToken: If decryption fails

    Example:
        >>> decrypted = decrypt_api_key(encrypted)
        >>> print(decrypted)
        'my-secret-api-key'
    """
    try:
        fernet = Fernet(get_encryption_key())
        decrypted = fernet.decrypt(encrypted_text.encode())
        return decrypted.decode()
    except Exception as e:
        logger.error(f'Error decrypting data: {e}')
        raise
