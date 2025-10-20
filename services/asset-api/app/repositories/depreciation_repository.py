"""
Depreciation Repository
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.depreciation import AssetDepreciationRecord
from app.repositories.base_repository import BaseRepository


class DepreciationRepository(BaseRepository[AssetDepreciationRecord]):
    """Repository for AssetDepreciationRecord operations"""

    def __init__(self, session: Session):
        super().__init__(AssetDepreciationRecord, session)

    def get_asset_records(self, asset_id: int) -> List[AssetDepreciationRecord]:
        """Get all depreciation records for an asset"""
        return self.session.query(AssetDepreciationRecord).filter(
            AssetDepreciationRecord.asset_id == asset_id
        ).order_by(AssetDepreciationRecord.period_month.desc()).all()

    def get_period_record(self, asset_id: int, period_month: int) -> Optional[AssetDepreciationRecord]:
        """Get depreciation record for specific period"""
        return self.session.query(AssetDepreciationRecord).filter(
            AssetDepreciationRecord.asset_id == asset_id,
            AssetDepreciationRecord.period_month == period_month
        ).first()

    def get_latest_record(self, asset_id: int) -> Optional[AssetDepreciationRecord]:
        """Get the latest depreciation record for an asset"""
        return self.session.query(AssetDepreciationRecord).filter(
            AssetDepreciationRecord.asset_id == asset_id
        ).order_by(AssetDepreciationRecord.period_month.desc()).first()

    def record_exists(self, asset_id: int, period_month: int) -> bool:
        """Check if record exists for asset and period"""
        return self.session.query(AssetDepreciationRecord).filter(
            AssetDepreciationRecord.asset_id == asset_id,
            AssetDepreciationRecord.period_month == period_month
        ).first() is not None
