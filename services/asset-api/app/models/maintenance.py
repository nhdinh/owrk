"""
Maintenance Model
"""

from sqlalchemy import Column, String, Numeric, Date, Text, ForeignKey, event
import enum

from app.models.base import BaseModel
from app.core.utils import generate_slug


class MaintenanceType(str, enum.Enum):
    """Maintenance type enumeration"""

    ROUTINE = "routine"
    PREVENTIVE = "preventive"
    CORRECTIVE = "corrective"
    EMERGENCY = "emergency"


class MaintenanceStatus(str, enum.Enum):
    """Maintenance status enumeration"""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class MaintenanceRecord(BaseModel):
    """Maintenance record model"""

    __tablename__ = "maintenance_records"
    __table_args__ = {"schema": "asset_db"}

    # Basic Information
    asset_id = Column(
        String(36), ForeignKey("asset_db.assets.id"), nullable=False, index=True
    )
    maintenance_type = Column(String(50), nullable=False)
    maintenance_date = Column(Date, nullable=False, index=True)
    completed_date = Column(Date, nullable=True)

    # Details
    cost = Column(Numeric(15, 2), nullable=False, default=0)
    technician = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)

    # Audit fields
    performed_by = Column(String(36), nullable=True)  # User UUID who performed maintenance
    created_by = Column(String(36), nullable=False)  # User UUID who created record

    # Status
    status = Column(
        String(50), default=MaintenanceStatus.PENDING.value, nullable=False, index=True
    )

    def __repr__(self):
        return f"<MaintenanceRecord(id={self.id}, asset_id={self.asset_id}, type={self.maintenance_type}, status={self.status})>"


# Event listener to auto-generate slug from asset_id and maintenance_date
@event.listens_for(MaintenanceRecord, "before_insert")
def generate_maintenance_slug(mapper, connection, target):
    """Auto-generate slug from asset_id, type, and date if not provided"""
    if not target.slug:
        asset_short = target.asset_id[:8] if target.asset_id else "unknown"
        date_str = target.maintenance_date.strftime("%Y%m%d") if target.maintenance_date else "nodate"
        target.slug = generate_slug(f"maint-{asset_short}-{target.maintenance_type}-{date_str}")
