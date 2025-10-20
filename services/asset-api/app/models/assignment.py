"""
Asset Assignment Model
"""

from sqlalchemy import Column, String, Integer, Date, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
import enum

from app.models.base import BaseModel


class AssignmentStatus(str, enum.Enum):
    """Assignment status enumeration"""
    ACTIVE = "ACTIVE"
    RETURNED = "RETURNED"


class ReturnCondition(str, enum.Enum):
    """Return condition enumeration"""
    GOOD = "GOOD"
    DAMAGED = "DAMAGED"
    BROKEN = "BROKEN"


class AssetAssignment(BaseModel):
    """Asset Assignment model - tracks asset assignment history"""

    __tablename__ = "asset_assignments"
    __table_args__ = {"schema": "asset_db"}

    asset_id = Column(Integer, ForeignKey("asset_db.assets.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    department_id = Column(Integer, nullable=False)

    # Assignment Information
    assigned_date = Column(Date, nullable=False, index=True)
    assigned_by = Column(Integer, nullable=False)
    notes = Column(Text, nullable=True)
    handover_document_url = Column(String(500), nullable=True)

    # Return Information
    returned_date = Column(Date, nullable=True)
    returned_by = Column(Integer, nullable=True)
    return_condition = Column(SQLEnum(ReturnCondition), nullable=True)
    return_notes = Column(Text, nullable=True)

    # Status
    status = Column(SQLEnum(AssignmentStatus), default=AssignmentStatus.ACTIVE, nullable=False, index=True)

    # Relationships
    asset = relationship("Asset", back_populates="assignments")

    def __repr__(self):
        return f"<AssetAssignment(id={self.id}, asset_id={self.asset_id}, user_id={self.user_id}, status={self.status})>"
