"""
Generator utilities for creating unique codes and identifiers.
"""
import random
import string
from datetime import datetime


def generate_sku(tenant_id: str, product_name: str) -> str:
    """
    Auto-generate SKU for a product.

    Format: {FIRST_3_LETTERS}-{TIMESTAMP}-{RANDOM}

    Args:
        tenant_id: UUID of the tenant
        product_name: Name of the product

    Returns:
        str: Generated SKU

    Examples:
        >>> generate_sku('abc123', 'Lipstick Red')
        'LIP-20250117-A3K'
    """
    # Get first 3 letters of product name (uppercase, letters only)
    prefix = ''.join(c for c in product_name if c.isalpha())[:3].upper()
    if not prefix:
        prefix = 'PRD'

    # Get timestamp (YYYYMMDD format)
    timestamp = datetime.now().strftime('%Y%m%d')

    # Generate random 3-character suffix
    suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=3))

    return f'{prefix}-{timestamp}-{suffix}'


def generate_verification_code(length: int = 6) -> str:
    """
    Generate a random numeric verification code.

    Args:
        length: Length of the code (default: 6)

    Returns:
        str: Numeric verification code

    Examples:
        >>> code = generate_verification_code()
        >>> len(code)
        6
        >>> code.isdigit()
        True
    """
    return ''.join(random.choices(string.digits, k=length))


def generate_order_number(tenant_id: str) -> str:
    """
    Generate a unique order number.

    Format: ORD-{DATE}-{RANDOM}

    Args:
        tenant_id: UUID of the tenant

    Returns:
        str: Generated order number

    Examples:
        >>> generate_order_number('abc123')
        'ORD-20250117-7K9M'
    """
    # Get date (YYYYMMDD format)
    date_str = datetime.now().strftime('%Y%m%d')

    # Generate random 4-character suffix
    suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))

    return f'ORD-{date_str}-{suffix}'
