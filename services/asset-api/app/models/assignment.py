"""
Asset Assignment Model
"""

from sqlalchemy import Column, String, Date, Text, ForeignKey, Enum as SQLEnum, event
from sqlalchemy.orm import relationship
import enum

from app.models.base import BaseModel
from app.core.utils import generate_slug


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

    asset_id = Column(
        String(32),
        ForeignKey("asset_db.assets.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id = Column(String(32), nullable=False, index=True)  # User UUID from auth service
    department_id = Column(String(32), nullable=False)  # Department UUID

    # Assignment Information
    assigned_date = Column(Date, nullable=False, index=True)
    assigned_by = Column(String(32), nullable=False)  # User UUID who assigned
    notes = Column(Text, nullable=True)
    handover_document_url = Column(String(500), nullable=True)

    # Return Information
    returned_date = Column(Date, nullable=True)
    returned_by = Column(String(32), nullable=True)  # User UUID who processed return
    return_condition = Column(SQLEnum(ReturnCondition), nullable=True)
    return_notes = Column(Text, nullable=True)

    # Status
    status = Column(
        SQLEnum(AssignmentStatus),
        default=AssignmentStatus.ACTIVE,
        nullable=False,
        index=True,
    )

    # Relationships
    asset = relationship("Asset", back_populates="assignments")

    def __repr__(self):
        return f"<AssetAssignment(id={self.id}, asset_id={self.asset_id}, user_id={self.user_id}, status={self.status})>"


# Event listener to auto-generate slug from asset_id and user_id
@event.listens_for(AssetAssignment, "before_insert")
def generate_assignment_slug(mapper, connection, target):
    """Auto-generate slug from asset and user IDs if not provided"""
    if not target.slug:
        # Use first 8 chars of each UUID for readable slug
        asset_short = target.asset_id[:8] if target.asset_id else "unknown"
        user_short = target.user_id[:8] if target.user_id else "unknown"
        target.slug = generate_slug(f"assignment-{asset_short}-{user_short}")
