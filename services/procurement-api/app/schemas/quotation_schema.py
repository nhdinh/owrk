"""
Quotation Pydantic Schemas
Request and response models for quotation operations
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator

from app.models.quotation import QuotationStatus


# ===== Quotation Item Schemas =====

class QuotationItemBase(BaseModel):
    """Base quotation item schema"""

    product_name: str = Field(..., min_length=1, max_length=255)
    product_description: Optional[str] = None
    quantity: int = Field(..., gt=0)
    unit: str = Field(..., min_length=1, max_length=50)
    unit_price: Decimal = Field(..., ge=0)
    total_price: Decimal = Field(..., ge=0)


class QuotationItemCreate(QuotationItemBase):
    """Schema for creating quotation item"""

    pass


class QuotationItemResponse(QuotationItemBase):
    """Schema for quotation item response"""

    id: int
    quotation_id: int
    purchase_request_item_id: Optional[int] = None
    delivery_time: Optional[str] = None
    warranty_period: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ===== Quotation Schemas =====

class QuotationBase(BaseModel):
    """Base quotation schema"""

    purchase_request_id: int = Field(..., gt=0)
    vendor_id: int = Field(..., gt=0)
    quotation_date: date
    valid_until: Optional[date] = None
    tax_amount: Optional[Decimal] = Field(default=0, ge=0)
    discount_amount: Optional[Decimal] = Field(default=0, ge=0)
    payment_terms: Optional[str] = None
    delivery_terms: Optional[str] = None
    warranty_terms: Optional[str] = None
    notes: Optional[str] = None

    @field_validator("valid_until")
    @classmethod
    def validate_valid_until(cls, v, info):
        """Validate that valid_until is after quotation_date"""
        if v and "quotation_date" in info.data and v < info.data["quotation_date"]:
            raise ValueError("valid_until must be after quotation_date")
        return v


class QuotationCreate(QuotationBase):
    """Schema for creating quotation"""

    items: List[QuotationItemCreate] = Field(..., min_length=1)


class QuotationUpdate(BaseModel):
    """Schema for updating quotation"""

    quotation_date: Optional[date] = None
    valid_until: Optional[date] = None
    tax_amount: Optional[Decimal] = Field(None, ge=0)
    discount_amount: Optional[Decimal] = Field(None, ge=0)
    payment_terms: Optional[str] = None
    delivery_terms: Optional[str] = None
    warranty_terms: Optional[str] = None
    notes: Optional[str] = None
    items: Optional[List[QuotationItemCreate]] = None


class VendorSummary(BaseModel):
    """Vendor summary for quotation response"""

    id: int
    vendor_code: str
    name: str
    rating: Optional[Decimal] = None

    class Config:
        from_attributes = True


class PurchaseRequestSummary(BaseModel):
    """Purchase request summary for quotation response"""

    id: int
    request_code: str
    title: str

    class Config:
        from_attributes = True


class QuotationResponse(QuotationBase):
    """Schema for quotation response"""

    id: int
    quotation_code: str
    total_amount: Decimal
    final_amount: Decimal
    status: QuotationStatus
    vendor: Optional[VendorSummary] = None
    purchase_request: Optional[PurchaseRequestSummary] = None
    items: List[QuotationItemResponse] = []
    accepted_by: Optional[int] = None
    accepted_at: Optional[datetime] = None
    rejected_by: Optional[int] = None
    rejected_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    created_by: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class QuotationListResponse(BaseModel):
    """Schema for paginated quotation list"""

    quotations: List[QuotationResponse]
    total: int
    page: int
    page_size: int


class QuotationComparisonItem(BaseModel):
    """Schema for quotation in comparison"""

    id: int
    quotation_code: str
    vendor: VendorSummary
    final_amount: Decimal
    delivery_terms: Optional[str] = None
    warranty_terms: Optional[str] = None
    valid_until: Optional[date] = None
    items: List[QuotationItemResponse]


class QuotationComparison(BaseModel):
    """Schema for comparing quotations for a purchase request"""

    purchase_request: PurchaseRequestSummary
    quotations: List[QuotationComparisonItem]


class AcceptQuotationRequest(BaseModel):
    """Schema for accepting a quotation"""

    reason: Optional[str] = Field(None, max_length=500)


class RejectQuotationRequest(BaseModel):
    """Schema for rejecting a quotation"""

    reason: str = Field(..., min_length=1, max_length=1000)
