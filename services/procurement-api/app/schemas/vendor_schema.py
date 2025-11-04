"""
Vendor Pydantic Schemas
Request and response models for vendor operations
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field, field_validator

from app.models.vendor import VendorStatus


class VendorBase(BaseModel):
    """Base vendor schema with common fields"""

    company_name: str = Field(
        ..., min_length=1, max_length=255, description="Vendor company name"
    )
    contact_person: Optional[str] = Field(
        None, max_length=255, description="Contact person name"
    )
    email: Optional[str] = Field(None, max_length=255, description="Email address")
    phone: Optional[str] = Field(None, max_length=50, description="Phone number")
    address: Optional[str] = Field(None, description="Full address")
    tax_code: Optional[str] = Field(
        None, max_length=50, description="Tax identification number"
    )
    business_registration: Optional[str] = Field(
        None, max_length=50, description="Business registration number"
    )
    bank_account: Optional[str] = Field(
        None, max_length=100, description="Bank account number"
    )
    bank_name: Optional[str] = Field(None, max_length=255, description="Bank name")
    notes: Optional[str] = Field(None, description="Additional notes")

    @field_validator("email")
    @classmethod
    def validate_email_format(cls, v: Optional[str]) -> Optional[str]:
        """Validate email format"""
        if v:
            import re

            email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
            if not re.match(email_pattern, v):
                raise ValueError("Invalid email format")
        return v

    @field_validator("tax_code")
    @classmethod
    def validate_tax_code_format(cls, v: Optional[str]) -> Optional[str]:
        """Validate Vietnamese tax code format (10 or 13 digits)"""
        if v:
            if not v.isdigit() or len(v) not in [10, 13]:
                raise ValueError("Tax code must be 10 or 13 digits")
        return v


class VendorCreate(VendorBase):
    """Schema for creating a new vendor"""

    pass


class VendorUpdate(BaseModel):
    """Schema for updating an existing vendor (all fields optional)"""

    company_name: Optional[str] = Field(None, min_length=1, max_length=255)
    contact_person: Optional[str] = Field(None, max_length=255)
    email: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=50)
    address: Optional[str] = None
    tax_code: Optional[str] = Field(None, max_length=50)
    business_registration: Optional[str] = Field(None, max_length=50)
    bank_account: Optional[str] = Field(None, max_length=100)
    bank_name: Optional[str] = Field(None, max_length=255)
    notes: Optional[str] = None

    @field_validator("email")
    @classmethod
    def validate_email_format(cls, v: Optional[str]) -> Optional[str]:
        """Validate email format"""
        if v:
            import re

            email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
            if not re.match(email_pattern, v):
                raise ValueError("Invalid email format")
        return v

    @field_validator("tax_code")
    @classmethod
    def validate_tax_code_format(cls, v: Optional[str]) -> Optional[str]:
        """Validate Vietnamese tax code format"""
        if v:
            if not v.isdigit() or len(v) not in [10, 13]:
                raise ValueError("Tax code must be 10 or 13 digits")
        return v


class VendorResponse(VendorBase):
    """Schema for vendor response (includes system fields)"""

    id: int
    vendor_code: str
    rating: Decimal = Field(default=Decimal("0.00"), description="Vendor rating (0-5)")
    status: VendorStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class VendorListResponse(BaseModel):
    """Schema for paginated vendor list response"""

    vendors: list[VendorResponse]
    total: int
    page: int
    page_size: int


class VendorRatingUpdate(BaseModel):
    """Schema for updating vendor rating"""

    rating: Decimal = Field(..., ge=0, le=5, description="Rating from 0 to 5")

    @field_validator("rating")
    @classmethod
    def validate_rating_precision(cls, v: Decimal) -> Decimal:
        """Validate rating has max 2 decimal places"""
        if v.as_tuple().exponent < -2:
            raise ValueError("Rating can have maximum 2 decimal places")
        return v


class VendorStatusUpdate(BaseModel):
    """Schema for updating vendor status"""

    status: VendorStatus
    reason: Optional[str] = Field(None, description="Reason for status change")


class VendorBlacklistRequest(BaseModel):
    """Schema for blacklisting a vendor"""

    reason: str = Field(
        ..., min_length=10, description="Reason for blacklisting (min 10 characters)"
    )


class VendorSummary(BaseModel):
    """Summary schema for vendor (used in dropdowns/references)"""

    id: int
    vendor_code: str
    company_name: str
    status: VendorStatus
    rating: Decimal

    class Config:
        from_attributes = True
