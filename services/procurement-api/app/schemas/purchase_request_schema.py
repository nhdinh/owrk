"""
Purchase Request Pydantic Schemas
Request and response models for purchase request operations
"""

from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, Field

from app.models.purchase_request import Priority, ProcurementType, ApprovalStatus


# Purchase Request Item Schemas


class PurchaseRequestItemBase(BaseModel):
    """Base schema for purchase request items"""

    product_name: str = Field(
        ..., min_length=1, max_length=255, description="Product name"
    )
    product_description: Optional[str] = Field(None, description="Product description")
    specification: Optional[str] = Field(None, description="Technical specifications")
    unit: str = Field(
        ..., min_length=1, max_length=50, description="Unit of measurement"
    )
    quantity: int = Field(..., gt=0, description="Quantity requested")
    estimated_unit_price: Optional[Decimal] = Field(
        None, ge=0, description="Estimated price per unit"
    )
    estimated_total: Optional[Decimal] = Field(
        None, ge=0, description="Estimated total price"
    )
    reason: Optional[str] = Field(None, description="Reason for purchase")


class PurchaseRequestItemCreate(PurchaseRequestItemBase):
    """Schema for creating a purchase request item"""

    pass


class PurchaseRequestItemUpdate(BaseModel):
    """Schema for updating a purchase request item"""

    product_name: Optional[str] = Field(None, min_length=1, max_length=255)
    product_description: Optional[str] = None
    specification: Optional[str] = None
    unit: Optional[str] = Field(None, min_length=1, max_length=50)
    quantity: Optional[int] = Field(None, gt=0)
    estimated_unit_price: Optional[Decimal] = Field(None, ge=0)
    estimated_total: Optional[Decimal] = Field(None, ge=0)
    reason: Optional[str] = None


class PurchaseRequestItemResponse(PurchaseRequestItemBase):
    """Schema for purchase request item response"""

    id: int
    purchase_request_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Purchase Request Schemas


class PurchaseRequestBase(BaseModel):
    """Base schema for purchase requests"""

    title: str = Field(..., min_length=1, max_length=255, description="Request title")
    description: Optional[str] = Field(None, description="Detailed description")
    department_id: int = Field(..., gt=0, description="Department ID")
    priority: Priority = Field(..., description="Request priority")
    request_date: date = Field(..., description="Date of request")
    expected_delivery_date: Optional[date] = Field(
        None, description="Expected delivery date"
    )
    procurement_type: ProcurementType = Field(..., description="Type of procurement")
    framework_contract_id: Optional[int] = Field(
        None, description="Optional framework contract ID"
    )
    estimated_total: Optional[Decimal] = Field(
        None, ge=0, description="Estimated total cost"
    )


class PurchaseRequestCreate(PurchaseRequestBase):
    """Schema for creating a purchase request"""

    items: List[PurchaseRequestItemCreate] = Field(
        ..., min_items=1, description="List of items to purchase"
    )


class PurchaseRequestUpdate(BaseModel):
    """Schema for updating a purchase request"""

    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    department_id: Optional[int] = Field(None, gt=0)
    priority: Optional[Priority] = None
    request_date: Optional[date] = None
    expected_delivery_date: Optional[date] = None
    procurement_type: Optional[ProcurementType] = None
    framework_contract_id: Optional[int] = None
    estimated_total: Optional[Decimal] = Field(None, ge=0)


class PurchaseRequestResponse(PurchaseRequestBase):
    """Schema for purchase request response"""

    id: int
    request_code: str
    requested_by: int
    approval_status: ApprovalStatus
    level1_approved_by: Optional[int]
    level1_approved_at: Optional[datetime]
    level1_notes: Optional[str]
    level2_approved_by: Optional[int]
    level2_approved_at: Optional[datetime]
    level2_notes: Optional[str]
    level3_approved_by: Optional[int]
    level3_approved_at: Optional[datetime]
    level3_notes: Optional[str]
    rejected_by: Optional[int]
    rejected_at: Optional[datetime]
    rejection_reason: Optional[str]
    created_at: datetime
    updated_at: datetime
    items: List[PurchaseRequestItemResponse] = []

    class Config:
        from_attributes = True


class PurchaseRequestListResponse(BaseModel):
    """Schema for paginated purchase request list"""

    requests: List[PurchaseRequestResponse]
    total: int
    page: int
    page_size: int


# Approval Schemas


class ApprovalRequest(BaseModel):
    """Schema for approving a purchase request"""

    notes: Optional[str] = Field(
        None, max_length=1000, description="Approval notes/comments"
    )


class RejectionRequest(BaseModel):
    """Schema for rejecting a purchase request"""

    reason: str = Field(
        ..., min_length=10, description="Reason for rejection (min 10 characters)"
    )


class SubmitForApprovalRequest(BaseModel):
    """Schema for submitting a purchase request for approval"""

    pass  # No additional fields needed


# Summary Schema


class PurchaseRequestSummary(BaseModel):
    """Summary schema for purchase request (for dropdowns/references)"""

    id: int
    request_code: str
    title: str
    approval_status: ApprovalStatus
    estimated_total: Optional[Decimal]
    requested_by: int

    class Config:
        from_attributes = True
