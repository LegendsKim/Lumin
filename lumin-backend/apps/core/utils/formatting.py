"""
Formatting utilities for display purposes.
"""
import re
from decimal import Decimal
from typing import Union


def format_currency(amount: Union[int, float, Decimal], currency_symbol: str = '₪') -> str:
    """
    Format a number as currency with Hebrew Shekel symbol.

    Args:
        amount: The amount to format
        currency_symbol: Currency symbol (default: ₪ for ILS)

    Returns:
        str: Formatted currency string

    Examples:
        >>> format_currency(1234.56)
        '₪1,234.56'
        >>> format_currency(1000)
        '₪1,000.00'
    """
    if amount is None:
        return f'{currency_symbol}0.00'

    # Convert to Decimal for precise formatting
    if not isinstance(amount, Decimal):
        amount = Decimal(str(amount))

    # Format with thousands separator and 2 decimal places
    formatted = f'{currency_symbol}{amount:,.2f}'
    return formatted


def format_phone_number(phone: str, country_code: str = '+972') -> str:
    """
    Format phone number to Israeli format.

    Args:
        phone: Phone number string
        country_code: Country code (default: +972 for Israel)

    Returns:
        str: Formatted phone number

    Examples:
        >>> format_phone_number('0501234567')
        '+972501234567'
        >>> format_phone_number('+972501234567')
        '+972501234567'
        >>> format_phone_number('972501234567')
        '+972501234567'
    """
    if not phone:
        return ''

    # Remove all non-digit characters except +
    cleaned = re.sub(r'[^\d+]', '', phone)

    # If already has country code, return as is
    if cleaned.startswith('+972'):
        return cleaned

    # If starts with 972 without +, add it
    if cleaned.startswith('972'):
        return f'+{cleaned}'

    # If starts with 0, remove it and add country code
    if cleaned.startswith('0'):
        return f'{country_code}{cleaned[1:]}'

    # Otherwise, assume local number and add country code
    return f'{country_code}{cleaned}'


def format_percentage(value: Union[int, float, Decimal], decimals: int = 2) -> str:
    """
    Format a number as percentage.

    Args:
        value: The value to format (e.g., 15.5 for 15.5%)
        decimals: Number of decimal places

    Returns:
        str: Formatted percentage string

    Examples:
        >>> format_percentage(15.5)
        '15.50%'
        >>> format_percentage(0.5, decimals=1)
        '0.5%'
    """
    if value is None:
        return '0.00%'

    if not isinstance(value, Decimal):
        value = Decimal(str(value))

    return f'{value:.{decimals}f}%'
