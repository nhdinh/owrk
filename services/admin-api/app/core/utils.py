"""
Utility functions for UUID and slug generation
"""

import uuid
import re
from typing import Optional
from unidecode import unidecode


def generate_uuid() -> str:
    """
    Generate a UUID4 string

    Returns:
        str: UUID string without dashes (32 characters)
    """
    return str(uuid.uuid4())


def generate_slug(text: str, max_length: int = 100) -> str:
    """
    Generate a URL-friendly slug from text

    Args:
        text: Text to convert to slug
        max_length: Maximum length of slug (default: 100)

    Returns:
        str: URL-friendly slug

    Examples:
        >>> generate_slug("Nguyễn Văn A")
        'nguyen-van-a'
        >>> generate_slug("Admin User 123")
        'admin-user-123'
    """
    # Convert Vietnamese characters to ASCII
    text = unidecode(text)

    # Convert to lowercase
    text = text.lower()

    # Replace spaces and underscores with dashes
    text = re.sub(r"[\s_]+", "-", text)

    # Remove all non-alphanumeric characters except dashes
    text = re.sub(r"[^a-z0-9-]", "", text)

    # Remove multiple consecutive dashes
    text = re.sub(r"-+", "-", text)

    # Remove leading/trailing dashes
    text = text.strip("-")

    # Truncate to max_length
    if len(text) > max_length:
        text = text[:max_length].rstrip("-")

    return text


def ensure_unique_slug(base_slug: str, existing_slugs: list[str]) -> str:
    """
    Ensure slug is unique by appending a number if needed

    Args:
        base_slug: Base slug to check
        existing_slugs: List of existing slugs

    Returns:
        str: Unique slug

    Examples:
        >>> ensure_unique_slug("admin", ["admin", "admin-2"])
        'admin-3'
    """
    if base_slug not in existing_slugs:
        return base_slug

    counter = 2
    while f"{base_slug}-{counter}" in existing_slugs:
        counter += 1

    return f"{base_slug}-{counter}"


def is_valid_uuid(value: str) -> bool:
    """
    Check if a string is a valid UUID (with or without dashes)

    Args:
        value: String to check

    Returns:
        bool: True if valid UUID
    """
    if not value:
        return False

    # Remove dashes if present
    clean_value = value.replace("-", "")

    # Check if it's a valid hex string of length 32
    if len(clean_value) != 32:
        return False

    try:
        int(clean_value, 16)
        return True
    except ValueError:
        return False


def format_uuid(value: str, with_dashes: bool = False) -> str:
    """
    Format UUID string (add or remove dashes)

    Args:
        value: UUID string
        with_dashes: Whether to include dashes

    Returns:
        str: Formatted UUID
    """
    clean_value = value.replace("-", "")

    if not with_dashes:
        return clean_value

    # Format as: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
    return f"{clean_value[:8]}-{clean_value[8:12]}-{clean_value[12:16]}-{clean_value[16:20]}-{clean_value[20:]}"
