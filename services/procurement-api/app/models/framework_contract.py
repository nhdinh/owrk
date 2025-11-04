"""
Framework Contract model for long-term vendor agreements
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


class ContractStatus(str, enum.Enum):
    """Contract status enumeration"""

    ACTIVE = "ACTIVE"
    EXPIRED = "EXPIRED"
    TERMINATED = "TERMINATED"


class FrameworkContract(Base):
    """
    Framework Contract model for managing long-term vendor agreements

    Attributes:
        id: Primary key
        contract_code: Unique contract code
        contract_name: Contract name
        vendor_id: Foreign key to vendor
        contract_value: Total contract value
        start_date: Contract start date
        end_date: Contract end date
        terms_and_conditions: Contract terms
        payment_terms: Payment terms
        delivery_terms: Delivery terms
        contract_file_url: URL to contract document
        status: Contract status
        created_by: User ID who created the contract
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """

    __tablename__ = "framework_contracts"
    __table_args__ = {"schema": "procurement_db"}

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    contract_code = Column(String(50), unique=True, nullable=False, index=True)
    contract_name = Column(String(255), nullable=False)
    vendor_id = Column(
        Integer, ForeignKey("procurement_db.vendors.id"), nullable=False, index=True
    )

    # Contract Information
    contract_value = Column(DECIMAL(15, 2), nullable=False)
    start_date = Column(DATE, nullable=False, index=True)
    end_date = Column(DATE, nullable=False, index=True)

    # Terms
    terms_and_conditions = Column(Text)
    payment_terms = Column(Text)
    delivery_terms = Column(Text)

    # Attachments
    contract_file_url = Column(String(500))

    # Status
    status = Column(
        SQLEnum(ContractStatus),
        nullable=False,
        default=ContractStatus.ACTIVE,
        index=True,
    )

    # Metadata
    created_by = Column(Integer, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<FrameworkContract(id={self.id}, code='{self.contract_code}', vendor_id={self.vendor_id})>"
