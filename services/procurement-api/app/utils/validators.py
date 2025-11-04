"""
Validation utilities
Common validation functions for business rules
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from fastapi import HTTPException, status


def validate_date_range(
    start_date: date, end_date: date, allow_past: bool = False
) -> None:
    """
    Validate date range

    Args:
        start_date: Start date
        end_date: End date
        allow_past: Allow start date in the past

    Raises:
        HTTPException: If validation fails
    """
    today = datetime.now().date()

    # Check if end date is after start date
    if end_date <= start_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="End date must be after start date",
        )

    # Check if start date is in the past
    if not allow_past and start_date < today:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Start date cannot be in the past",
        )


def validate_positive_amount(
    amount: Decimal, field_name: str = "Amount", allow_zero: bool = False
) -> None:
    """
    Validate that amount is positive

    Args:
        amount: Amount to validate
        field_name: Name of field for error message
        allow_zero: Allow zero value

    Raises:
        HTTPException: If validation fails
    """
    if allow_zero:
        if amount < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"{field_name} cannot be negative",
            )
    else:
        if amount <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"{field_name} must be greater than zero",
            )


def validate_quantity(
    quantity: int,
    field_name: str = "Quantity",
    min_value: int = 1,
    max_value: Optional[int] = None,
) -> None:
    """
    Validate quantity

    Args:
        quantity: Quantity to validate
        field_name: Name of field for error message
        min_value: Minimum allowed value
        max_value: Maximum allowed value (optional)

    Raises:
        HTTPException: If validation fails
    """
    if quantity < min_value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{field_name} must be at least {min_value}",
        )

    if max_value is not None and quantity > max_value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{field_name} cannot exceed {max_value}",
        )


def validate_email(email: str) -> None:
    """
    Validate email format

    Args:
        email: Email address to validate

    Raises:
        HTTPException: If email is invalid
    """
    import re

    email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

    if not re.match(email_pattern, email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid email format"
        )


def validate_phone(phone: str) -> None:
    """
    Validate phone number format

    Args:
        phone: Phone number to validate

    Raises:
        HTTPException: If phone number is invalid
    """
    import re

    # Allow formats: +84123456789, 0123456789, (012) 345-6789
    phone_pattern = (
        r"^[\+]?[(]?[0-9]{1,4}[)]?[-\s\.]?[(]?[0-9]{1,4}[)]?[-\s\.]?[0-9]{1,9}$"
    )

    if not re.match(phone_pattern, phone.replace(" ", "")):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid phone number format",
        )


def validate_tax_code(tax_code: str) -> None:
    """
    Validate Vietnamese tax code format
    Format: 10 or 13 digits

    Args:
        tax_code: Tax code to validate

    Raises:
        HTTPException: If tax code is invalid
    """
    if not tax_code.isdigit() or len(tax_code) not in [10, 13]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tax code must be 10 or 13 digits",
        )


def validate_rating(rating: Decimal) -> None:
    """
    Validate vendor rating (0.00 - 5.00)

    Args:
        rating: Rating to validate

    Raises:
        HTTPException: If rating is out of range
    """
    if not (0 <= rating <= 5):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Rating must be between 0.00 and 5.00",
        )


def validate_percentage(percentage: Decimal, field_name: str = "Percentage") -> None:
    """
    Validate percentage (0 - 100)

    Args:
        percentage: Percentage to validate
        field_name: Name of field for error message

    Raises:
        HTTPException: If percentage is out of range
    """
    if not (0 <= percentage <= 100):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{field_name} must be between 0 and 100",
        )


def validate_priority(priority: str) -> None:
    """
    Validate priority level

    Args:
        priority: Priority level (LOW, MEDIUM, HIGH, URGENT)

    Raises:
        HTTPException: If priority is invalid
    """
    valid_priorities = ["LOW", "MEDIUM", "HIGH", "URGENT"]

    if priority.upper() not in valid_priorities:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Priority must be one of: {', '.join(valid_priorities)}",
        )


def validate_approval_transition(current_status: str, new_status: str) -> None:
    """
    Validate approval status transition
    Ensures workflow follows proper sequence

    Args:
        current_status: Current approval status
        new_status: New approval status

    Raises:
        HTTPException: If transition is invalid
    """
    # Define valid transitions
    valid_transitions = {
        "DRAFT": ["PENDING", "CANCELLED"],
        "PENDING": ["LEVEL1_APPROVED", "REJECTED", "CANCELLED"],
        "LEVEL1_APPROVED": ["LEVEL2_APPROVED", "REJECTED", "CANCELLED"],
        "LEVEL2_APPROVED": ["APPROVED", "REJECTED", "CANCELLED"],
        "APPROVED": ["CANCELLED"],
        "REJECTED": [],
        "CANCELLED": [],
    }

    allowed = valid_transitions.get(current_status, [])

    if new_status not in allowed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot transition from {current_status} to {new_status}",
        )
