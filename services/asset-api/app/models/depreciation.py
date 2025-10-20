"""
Asset Depreciation Record Model
"""

from sqlalchemy import Column, Integer, Numeric, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class AssetDepreciationRecord(BaseModel):
    """Asset Depreciation Record model - monthly depreciation tracking"""

    __tablename__ = "asset_depreciation_records"
    __table_args__ = (
        UniqueConstraint("asset_id", "period_month", name="uk_asset_period"),
        {"schema": "asset_db"}
    )

    asset_id = Column(Integer, ForeignKey("asset_db.assets.id", ondelete="CASCADE"), nullable=False, index=True)
    period_month = Column(Integer, nullable=False, index=True)  # Format: YYYYMM (e.g., 202501)

    # Values
    opening_value = Column(Numeric(15, 2), nullable=False)
    depreciation_amount = Column(Numeric(15, 2), nullable=False)
    closing_value = Column(Numeric(15, 2), nullable=False)
    accumulated_depreciation = Column(Numeric(15, 2), nullable=False)

    # Relationships
    asset = relationship("Asset", back_populates="depreciation_records")

    def __repr__(self):
        return f"<AssetDepreciationRecord(id={self.id}, asset_id={self.asset_id}, period={self.period_month})>"
