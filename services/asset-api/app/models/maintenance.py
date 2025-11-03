"""
Maintenance Model
"""

from sqlalchemy import Column, String, Integer, Numeric, Date, Text, ForeignKey
import enum

from app.models.base import BaseModel


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
    asset_id = Column(Integer, ForeignKey("asset_db.assets.id"), nullable=False, index=True)
    maintenance_type = Column(String(50), nullable=False)
    maintenance_date = Column(Date, nullable=False, index=True)
    completed_date = Column(Date, nullable=True)

    # Details
    cost = Column(Numeric(15, 2), nullable=False, default=0)
    technician = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)

    # Status
    status = Column(String(50), default=MaintenanceStatus.PENDING.value, nullable=False, index=True)

    def __repr__(self):
        return f"<MaintenanceRecord(id={self.id}, asset_id={self.asset_id}, type={self.maintenance_type}, status={self.status})>"
