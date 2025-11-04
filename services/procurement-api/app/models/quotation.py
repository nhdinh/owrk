"""
Quotation models for vendor price quotes
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


class QuotationStatus(str, enum.Enum):
    """Quotation status enumeration"""

    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class Quotation(Base):
    """
    Quotation model for managing vendor price quotes

    Attributes:
        id: Primary key
        quotation_code: Unique quotation code
        purchase_request_id: Foreign key to purchase request
        vendor_id: Foreign key to vendor
        quotation_date: Date of quotation
        valid_until: Quotation validity date
        total_amount: Total quotation amount
        quotation_file_url: URL to quotation document
        notes: Additional notes
        status: Quotation status
        created_by: User ID who created the quotation
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """

    __tablename__ = "quotations"
    __table_args__ = {"schema": "procurement_db"}

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    quotation_code = Column(String(50), unique=True, nullable=False, index=True)
    purchase_request_id = Column(
        Integer,
        ForeignKey("procurement_db.purchase_requests.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    vendor_id = Column(
        Integer, ForeignKey("procurement_db.vendors.id"), nullable=False, index=True
    )

    # Quotation Information
    quotation_date = Column(DATE, nullable=False)
    valid_until = Column(DATE)
    total_amount = Column(DECIMAL(15, 2), nullable=False)

    # Attachments
    quotation_file_url = Column(String(500))

    # Notes
    notes = Column(Text)

    # Status
    status = Column(
        SQLEnum(QuotationStatus),
        nullable=False,
        default=QuotationStatus.PENDING,
        index=True,
    )

    # Metadata
    created_by = Column(Integer, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<Quotation(id={self.id}, code='{self.quotation_code}', vendor_id={self.vendor_id})>"


class QuotationItem(Base):
    """
    Quotation Item model for line items in quotations

    Attributes:
        id: Primary key
        quotation_id: Foreign key to quotation
        purchase_request_item_id: Optional link to request item
        product_name: Product name
        product_description: Product description
        unit: Unit of measurement
        quantity: Quantity
        unit_price: Price per unit
        total_price: Total price
        delivery_time: Delivery time estimate
        warranty_period: Warranty period
        created_at: Creation timestamp
    """

    __tablename__ = "quotation_items"
    __table_args__ = {"schema": "procurement_db"}

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    quotation_id = Column(
        Integer,
        ForeignKey("procurement_db.quotations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    purchase_request_item_id = Column(
        Integer,
        ForeignKey("procurement_db.purchase_request_items.id", ondelete="SET NULL"),
        index=True,
    )

    # Product Information
    product_name = Column(String(255), nullable=False)
    product_description = Column(Text)
    unit = Column(String(50), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(DECIMAL(15, 2), nullable=False)
    total_price = Column(DECIMAL(15, 2), nullable=False)

    # Additional Information
    delivery_time = Column(String(100))
    warranty_period = Column(String(100))

    created_at = Column(TIMESTAMP, server_default=func.now())

    def __repr__(self):
        return f"<QuotationItem(id={self.id}, quotation_id={self.quotation_id}, product='{self.product_name}')>"
