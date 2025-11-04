"""
Purchase Order models for final procurement orders
"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    DECIMAL,
    DATE,
    TIMESTAMP,
    Text,
    ForeignKey,
    Enum as SQLEnum,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import Base
import enum


class OrderStatus(str, enum.Enum):
    """Order status enumeration"""

    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    PROCESSING = "PROCESSING"
    SHIPPED = "SHIPPED"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"
    COMPLETED = "COMPLETED"


class PaymentStatus(str, enum.Enum):
    """Payment status enumeration"""

    PENDING = "PENDING"
    PARTIAL = "PARTIAL"
    PAID = "PAID"


class PurchaseOrder(Base):
    """
    Purchase Order model for managing final procurement orders

    Attributes:
        id: Primary key
        order_code: Unique order code
        purchase_request_id: Foreign key to purchase request
        quotation_id: Foreign key to selected quotation
        vendor_id: Foreign key to vendor
        order_date: Date of order
        expected_delivery_date: Expected delivery date
        actual_delivery_date: Actual delivery date
        subtotal: Subtotal amount
        tax_amount: Tax amount
        discount_amount: Discount amount
        total_amount: Total amount
        delivery_address: Delivery address
        delivery_contact: Delivery contact person
        delivery_phone: Delivery phone number
        payment_terms: Payment terms
        payment_status: Payment status
        status: Order status
        notes: Additional notes
        created_by: User ID who created the order
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """

    __tablename__ = "purchase_orders"
    __table_args__ = {"schema": "procurement_db"}

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    order_code = Column(String(50), unique=True, nullable=False, index=True)
    purchase_request_id = Column(
        Integer, ForeignKey("procurement_db.purchase_requests.id"), nullable=False
    )
    quotation_id = Column(
        Integer, ForeignKey("procurement_db.quotations.id"), nullable=False
    )
    vendor_id = Column(
        Integer, ForeignKey("procurement_db.vendors.id"), nullable=False, index=True
    )

    # Order Information
    order_date = Column(DATE, nullable=False, index=True)
    expected_delivery_date = Column(DATE)
    actual_delivery_date = Column(DATE)

    # Financial Information
    subtotal = Column(DECIMAL(15, 2), nullable=False)
    tax_amount = Column(DECIMAL(15, 2), default=0)
    discount_amount = Column(DECIMAL(15, 2), default=0)
    total_amount = Column(DECIMAL(15, 2), nullable=False)

    # Delivery Information
    delivery_address = Column(Text)
    delivery_contact = Column(String(255))
    delivery_phone = Column(String(50))

    # Payment Information
    payment_terms = Column(Text)
    payment_status = Column(SQLEnum(PaymentStatus), default=PaymentStatus.PENDING)

    # Order Status
    status = Column(
        SQLEnum(OrderStatus), nullable=False, default=OrderStatus.PENDING, index=True
    )

    # Notes
    notes = Column(Text)

    # Metadata
    created_by = Column(Integer, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<PurchaseOrder(id={self.id}, code='{self.order_code}', status='{self.status}')>"


class PurchaseOrderItem(Base):
    """
    Purchase Order Item model for line items in purchase orders

    Attributes:
        id: Primary key
        purchase_order_id: Foreign key to purchase order
        quotation_item_id: Optional link to quotation item
        product_name: Product name
        product_description: Product description
        unit: Unit of measurement
        quantity: Quantity ordered
        unit_price: Price per unit
        total_price: Total price
        received_quantity: Quantity received
        created_at: Creation timestamp
    """

    __tablename__ = "purchase_order_items"
    __table_args__ = {"schema": "procurement_db"}

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    purchase_order_id = Column(
        Integer,
        ForeignKey("procurement_db.purchase_orders.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    quotation_item_id = Column(
        Integer, ForeignKey("procurement_db.quotation_items.id", ondelete="SET NULL")
    )

    # Product Information
    product_name = Column(String(255), nullable=False)
    product_description = Column(Text)
    unit = Column(String(50), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(DECIMAL(15, 2), nullable=False)
    total_price = Column(DECIMAL(15, 2), nullable=False)

    # Received Quantity
    received_quantity = Column(Integer, default=0)

    created_at = Column(TIMESTAMP, server_default=func.now())

    def __repr__(self):
        return f"<PurchaseOrderItem(id={self.id}, order_id={self.purchase_order_id}, product='{self.product_name}')>"
