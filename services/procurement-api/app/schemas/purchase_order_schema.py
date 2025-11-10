"""
Purchase Order Pydantic Schemas
Request and response models for purchase order operations
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, Field

from app.models.purchase_order import OrderStatus


# ===== Purchase Order Item Schemas =====

class PurchaseOrderItemBase(BaseModel):
    """Base purchase order item schema"""

    product_name: str = Field(..., min_length=1, max_length=255)
    product_description: Optional[str] = None
    quantity: int = Field(..., gt=0)
    unit: str = Field(..., min_length=1, max_length=50)
    unit_price: Decimal = Field(..., ge=0)
    total_price: Decimal = Field(..., ge=0)
    received_quantity: int = Field(default=0, ge=0)


class PurchaseOrderItemCreate(PurchaseOrderItemBase):
    """Schema for creating purchase order item"""

    pass


class PurchaseOrderItemResponse(PurchaseOrderItemBase):
    """Schema for purchase order item response"""

    id: int
    purchase_order_id: int
    quotation_item_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ===== Purchase Order Schemas =====

class PurchaseOrderBase(BaseModel):
    """Base purchase order schema"""

    purchase_request_id: int = Field(..., gt=0)
    quotation_id: int = Field(..., gt=0)
    order_date: date
    expected_delivery_date: Optional[date] = None
    tax_amount: Optional[Decimal] = Field(default=0, ge=0)
    discount_amount: Optional[Decimal] = Field(default=0, ge=0)
    shipping_cost: Optional[Decimal] = Field(default=0, ge=0)
    payment_terms: Optional[str] = None
    delivery_address: Optional[str] = None
    billing_address: Optional[str] = None
    notes: Optional[str] = None


class PurchaseOrderCreate(PurchaseOrderBase):
    """Schema for creating purchase order"""

    pass


class PurchaseOrderUpdate(BaseModel):
    """Schema for updating purchase order"""

    expected_delivery_date: Optional[date] = None
    actual_delivery_date: Optional[date] = None
    tax_amount: Optional[Decimal] = Field(None, ge=0)
    discount_amount: Optional[Decimal] = Field(None, ge=0)
    shipping_cost: Optional[Decimal] = Field(None, ge=0)
    payment_terms: Optional[str] = None
    delivery_address: Optional[str] = None
    billing_address: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[OrderStatus] = None


class VendorDetail(BaseModel):
    """Vendor detail for purchase order response"""

    id: int
    vendor_code: str
    name: str
    contact_person: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None

    class Config:
        from_attributes = True


class QuotationSummary(BaseModel):
    """Quotation summary for purchase order response"""

    id: int
    quotation_code: str

    class Config:
        from_attributes = True


class PurchaseRequestDetail(BaseModel):
    """Purchase request detail for purchase order response"""

    id: int
    request_code: str
    title: str

    class Config:
        from_attributes = True


class PurchaseOrderResponse(PurchaseOrderBase):
    """Schema for purchase order response"""

    id: int
    po_code: str
    vendor_id: int
    vendor: Optional[VendorDetail] = None
    quotation: Optional[QuotationSummary] = None
    purchase_request: Optional[PurchaseRequestDetail] = None
    total_amount: Decimal
    final_amount: Decimal
    actual_delivery_date: Optional[date] = None
    status: OrderStatus
    approved_by: Optional[int] = None
    approved_at: Optional[datetime] = None
    items: List[PurchaseOrderItemResponse] = []
    created_by: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PurchaseOrderListResponse(BaseModel):
    """Schema for paginated purchase order list"""

    purchase_orders: List[PurchaseOrderResponse]
    total: int
    page: int
    page_size: int


class ConfirmOrderRequest(BaseModel):
    """Schema for confirming a purchase order"""

    notes: Optional[str] = Field(None, max_length=500)


class ApproveOrderRequest(BaseModel):
    """Schema for approving a purchase order"""

    reason: Optional[str] = Field(None, max_length=500)


class SendOrderRequest(BaseModel):
    """Schema for sending a purchase order to vendor"""

    send_email: bool = Field(default=True)
    additional_notes: Optional[str] = Field(None, max_length=1000)


class ShipOrderRequest(BaseModel):
    """Schema for marking order as shipped"""

    tracking_number: Optional[str] = Field(None, max_length=200)
    carrier: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = Field(None, max_length=500)


class ReceiveItemRequest(BaseModel):
    """Schema for receiving items"""

    item_id: int = Field(..., gt=0)
    received_quantity: int = Field(..., gt=0)


class ReceiveOrderRequest(BaseModel):
    """Schema for receiving purchase order items"""

    items: List[ReceiveItemRequest] = Field(..., min_length=1)
    actual_delivery_date: Optional[date] = None
    notes: Optional[str] = Field(None, max_length=1000)


class CompleteOrderRequest(BaseModel):
    """Schema for completing a purchase order"""

    create_assets: bool = Field(default=True)
    notes: Optional[str] = Field(None, max_length=500)


class CancelOrderRequest(BaseModel):
    """Schema for cancelling a purchase order"""

    reason: str = Field(..., min_length=1, max_length=1000)
