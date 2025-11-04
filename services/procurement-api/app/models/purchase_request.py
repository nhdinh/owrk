"""
Purchase Request models for procurement requests with multi-level approval
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


class Priority(str, enum.Enum):
    """Priority level enumeration"""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    URGENT = "URGENT"


class ProcurementType(str, enum.Enum):
    """Procurement type enumeration"""

    FRAMEWORK_CONTRACT = "FRAMEWORK_CONTRACT"
    ONE_TIME = "ONE_TIME"


class ApprovalStatus(str, enum.Enum):
    """Approval status enumeration"""

    DRAFT = "DRAFT"
    PENDING = "PENDING"
    LEVEL1_APPROVED = "LEVEL1_APPROVED"
    LEVEL2_APPROVED = "LEVEL2_APPROVED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"


class PurchaseRequest(Base):
    """
    Purchase Request model for managing procurement requests

    Attributes:
        id: Primary key
        request_code: Unique request code
        title: Request title
        description: Detailed description
        requested_by: User ID who created the request
        department_id: Department ID
        priority: Request priority level
        request_date: Date of request
        expected_delivery_date: Expected delivery date
        procurement_type: Type of procurement
        framework_contract_id: Optional framework contract ID
        estimated_total: Estimated total cost
        approval_status: Current approval status
        level1_approved_by: Department manager approval
        level1_approved_at: Level 1 approval timestamp
        level1_notes: Level 1 approval notes
        level2_approved_by: HR manager approval
        level2_approved_at: Level 2 approval timestamp
        level2_notes: Level 2 approval notes
        level3_approved_by: Director approval
        level3_approved_at: Level 3 approval timestamp
        level3_notes: Level 3 approval notes
        rejected_by: User ID who rejected
        rejected_at: Rejection timestamp
        rejection_reason: Reason for rejection
        created_at: Creation timestamp
        updated_at: Last update timestamp
        deleted_at: Soft delete timestamp
    """

    __tablename__ = "purchase_requests"
    __table_args__ = {"schema": "procurement_db"}

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    request_code = Column(String(50), unique=True, nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)

    # Request Information
    requested_by = Column(Integer, nullable=False, index=True)
    department_id = Column(Integer, nullable=False, index=True)
    priority = Column(SQLEnum(Priority), nullable=False, index=True)
    request_date = Column(DATE, nullable=False, index=True)
    expected_delivery_date = Column(DATE)

    # Procurement Type
    procurement_type = Column(SQLEnum(ProcurementType), nullable=False)
    framework_contract_id = Column(
        Integer, ForeignKey("procurement_db.framework_contracts.id")
    )

    # Estimated Total
    estimated_total = Column(DECIMAL(15, 2))

    # Approval Status
    approval_status = Column(
        SQLEnum(ApprovalStatus),
        nullable=False,
        default=ApprovalStatus.DRAFT,
        index=True,
    )

    # Level 1 Approval (Department Manager)
    level1_approved_by = Column(Integer)
    level1_approved_at = Column(TIMESTAMP)
    level1_notes = Column(Text)

    # Level 2 Approval (HR Manager)
    level2_approved_by = Column(Integer)
    level2_approved_at = Column(TIMESTAMP)
    level2_notes = Column(Text)

    # Level 3 Approval (Director)
    level3_approved_by = Column(Integer)
    level3_approved_at = Column(TIMESTAMP)
    level3_notes = Column(Text)

    # Rejection
    rejected_by = Column(Integer)
    rejected_at = Column(TIMESTAMP)
    rejection_reason = Column(Text)

    # Timestamps
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    deleted_at = Column(TIMESTAMP)

    # Relationships
    items = relationship(
        "PurchaseRequestItem",
        back_populates="purchase_request",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<PurchaseRequest(id={self.id}, code='{self.request_code}', status='{self.approval_status}')>"


class PurchaseRequestItem(Base):
    """
    Purchase Request Item model for line items in purchase requests

    Attributes:
        id: Primary key
        purchase_request_id: Foreign key to purchase request
        product_name: Product name
        product_description: Product description
        specification: Technical specifications
        unit: Unit of measurement
        quantity: Quantity requested
        estimated_unit_price: Estimated price per unit
        estimated_total: Estimated total price
        reason: Reason for purchase
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """

    __tablename__ = "purchase_request_items"
    __table_args__ = {"schema": "procurement_db"}

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    purchase_request_id = Column(
        Integer,
        ForeignKey("procurement_db.purchase_requests.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Product Information
    product_name = Column(String(255), nullable=False)
    product_description = Column(Text)
    specification = Column(Text)
    unit = Column(String(50), nullable=False)
    quantity = Column(Integer, nullable=False)

    # Estimated Pricing
    estimated_unit_price = Column(DECIMAL(15, 2))
    estimated_total = Column(DECIMAL(15, 2))

    # Reason
    reason = Column(Text)

    # Timestamps
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relationships
    purchase_request = relationship("PurchaseRequest", back_populates="items")

    def __repr__(self):
        return f"<PurchaseRequestItem(id={self.id}, request_id={self.purchase_request_id}, product='{self.product_name}')>"
