"""
Vendor model for supplier management
"""

from sqlalchemy import Column, Integer, String, DECIMAL, TIMESTAMP, Text, Enum as SQLEnum
from sqlalchemy.sql import func
from app.models.base import Base
import enum


class VendorStatus(str, enum.Enum):
    """Vendor status enumeration"""
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    BLACKLISTED = "BLACKLISTED"


class Vendor(Base):
    """
    Vendor model for managing suppliers

    Attributes:
        id: Primary key
        vendor_code: Unique vendor code
        company_name: Vendor company name
        contact_person: Contact person name
        email: Contact email
        phone: Contact phone number
        address: Vendor address
        tax_code: Tax identification number
        website: Vendor website URL
        business_registration: Business registration number
        bank_account: Bank account number
        bank_name: Bank name
        rating: Vendor rating (0-5)
        status: Vendor status (ACTIVE, INACTIVE, BLACKLISTED)
        notes: Additional notes
        created_by: User ID who created the vendor
        created_at: Creation timestamp
        updated_at: Last update timestamp
        deleted_at: Soft delete timestamp
    """

    __tablename__ = "vendors"
    __table_args__ = {"schema": "procurement_db"}

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    vendor_code = Column(String(50), unique=True, nullable=False, index=True)
    company_name = Column(String(255), nullable=False, index=True)

    # Contact Information
    contact_person = Column(String(255))
    email = Column(String(255))
    phone = Column(String(50))
    address = Column(Text)

    # Tax Information
    tax_code = Column(String(50), unique=True)

    # Business Information
    website = Column(String(255))
    business_registration = Column(String(100))
    bank_account = Column(String(100))
    bank_name = Column(String(255))

    # Rating & Status
    rating = Column(DECIMAL(3, 2), default=0.00)  # 0.00 to 5.00
    status = Column(
        SQLEnum(VendorStatus),
        nullable=False,
        default=VendorStatus.ACTIVE,
        index=True
    )

    # Metadata
    notes = Column(Text)
    created_by = Column(Integer, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    deleted_at = Column(TIMESTAMP, nullable=True)

    def __repr__(self):
        return f"<Vendor(id={self.id}, code='{self.vendor_code}', name='{self.company_name}')>"
