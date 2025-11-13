"""
Asset Depreciation Record Model
"""

from sqlalchemy import Column, String, Integer, Numeric, ForeignKey, UniqueConstraint, event
from sqlalchemy.orm import relationship

from app.models.base import BaseModel
from app.core.utils import generate_slug


class AssetDepreciationRecord(BaseModel):
    """Asset Depreciation Record model - monthly depreciation tracking"""

    __tablename__ = "asset_depreciation_records"
    __table_args__ = (
        UniqueConstraint("asset_id", "period_month", name="uk_asset_period"),
        {"schema": "asset_db"},
    )

    asset_id = Column(
        String(32),
        ForeignKey("asset_db.assets.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    period_month = Column(
        Integer, nullable=False, index=True
    )  # Format: YYYYMM (e.g., 202501)

    # Values
    opening_value = Column(Numeric(15, 2), nullable=False)
    depreciation_amount = Column(Numeric(15, 2), nullable=False)
    closing_value = Column(Numeric(15, 2), nullable=False)
    accumulated_depreciation = Column(Numeric(15, 2), nullable=False)

    # Audit field
    calculated_by = Column(String(32), nullable=True)  # User UUID who ran calculation

    # Relationships
    asset = relationship("Asset", back_populates="depreciation_records")

    def __repr__(self):
        return f"<AssetDepreciationRecord(id={self.id}, asset_id={self.asset_id}, period={self.period_month})>"


# Event listener to auto-generate slug from asset_id and period
@event.listens_for(AssetDepreciationRecord, "before_insert")
def generate_depreciation_slug(mapper, connection, target):
    """Auto-generate slug from asset_id and period_month if not provided"""
    if not target.slug:
        asset_short = target.asset_id[:8] if target.asset_id else "unknown"
        target.slug = generate_slug(f"depreciation-{asset_short}-{target.period_month}")
