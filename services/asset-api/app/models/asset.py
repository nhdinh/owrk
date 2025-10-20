"""
Asset Model
"""

from sqlalchemy import Column, String, Integer, Numeric, Date, Text, ForeignKey, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.models.base import BaseModel


class AssetType(str, enum.Enum):
    """Asset type enumeration"""
    FIXED_ASSET = "FIXED_ASSET"  # Tài sản cố định
    TOOL = "TOOL"  # Công cụ dụng cụ


class AssetStatus(str, enum.Enum):
    """Asset status enumeration"""
    NEW = "NEW"
    IN_USE = "IN_USE"
    AVAILABLE = "AVAILABLE"
    MAINTENANCE = "MAINTENANCE"
    BROKEN = "BROKEN"
    DISPOSED = "DISPOSED"


class DepreciationMethod(str, enum.Enum):
    """Depreciation method enumeration"""
    STRAIGHT_LINE = "STRAIGHT_LINE"  # Khấu hao đường thẳng
    DECLINING_BALANCE = "DECLINING_BALANCE"  # Khấu hao số dư giảm dần


class Asset(BaseModel):
    """Asset model"""

    __tablename__ = "assets"
    __table_args__ = {"schema": "asset_db"}

    # Basic Information
    asset_code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    category_id = Column(Integer, ForeignKey("asset_db.asset_categories.id"), nullable=False, index=True)
    asset_type = Column(SQLEnum(AssetType), nullable=False, index=True)
    description = Column(Text, nullable=True)
    manufacturer = Column(String(255), nullable=True)
    model = Column(String(255), nullable=True)
    serial_number = Column(String(255), nullable=True)

    # Financial Information
    purchase_price = Column(Numeric(15, 2), nullable=False)
    purchase_date = Column(Date, nullable=False, index=True)
    purchase_order_id = Column(Integer, nullable=True)  # Link to procurement service

    # Depreciation (for Fixed Assets)
    depreciation_rate = Column(Numeric(5, 2), nullable=True)  # %/year
    depreciation_method = Column(SQLEnum(DepreciationMethod), nullable=True)
    useful_life_months = Column(Integer, nullable=True)
    residual_value = Column(Numeric(15, 2), nullable=True)

    # Warranty
    warranty_months = Column(Integer, nullable=True)
    warranty_start_date = Column(Date, nullable=True)
    warranty_end_date = Column(Date, nullable=True)
    warranty_provider = Column(String(255), nullable=True)

    # Status
    status = Column(SQLEnum(AssetStatus), default=AssetStatus.NEW, nullable=False, index=True)

    # Location
    location = Column(String(255), nullable=True)
    department_id = Column(Integer, nullable=True, index=True)
    current_user_id = Column(Integer, nullable=True, index=True)  # Currently assigned user

    # QR Code
    qr_code = Column(String(500), nullable=True)

    # Audit
    created_by = Column(Integer, nullable=False)
    deleted_at = Column(DateTime, nullable=True)

    # Relationships
    category = relationship("AssetCategory", back_populates="assets")
    assignments = relationship("AssetAssignment", back_populates="asset", cascade="all, delete-orphan")
    attachments = relationship("AssetAttachment", back_populates="asset", cascade="all, delete-orphan")
    depreciation_records = relationship("AssetDepreciationRecord", back_populates="asset", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Asset(id={self.id}, code={self.asset_code}, name={self.name}, status={self.status})>"
