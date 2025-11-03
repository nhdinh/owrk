"""
Maintenance Repository
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.maintenance import MaintenanceRecord
from app.repositories.base_repository import BaseRepository


class MaintenanceRepository(BaseRepository[MaintenanceRecord]):
    """Repository for maintenance record operations"""

    def __init__(self, db: Session):
        super().__init__(MaintenanceRecord, db)

    def get_by_asset(self, asset_id: int) -> List[MaintenanceRecord]:
        """Get all maintenance records for an asset"""
        return self.session.query(self.model).filter(
            self.model.asset_id == asset_id
        ).order_by(self.model.maintenance_date.desc()).all()

    def get_by_status(self, status: str) -> List[MaintenanceRecord]:
        """Get maintenance records by status"""
        return self.session.query(self.model).filter(
            self.model.status == status
        ).order_by(self.model.maintenance_date.desc()).all()

    def get_by_asset_and_status(self, asset_id: int, status: str) -> List[MaintenanceRecord]:
        """Get maintenance records by asset and status"""
        return self.session.query(self.model).filter(
            and_(
                self.model.asset_id == asset_id,
                self.model.status == status
            )
        ).order_by(self.model.maintenance_date.desc()).all()

    def get_all_with_details(self) -> List[dict]:
        """Get all maintenance records with asset details"""
        from app.models.asset import Asset

        records = self.session.query(
            MaintenanceRecord,
            Asset.asset_code,
            Asset.name.label('asset_name')
        ).join(
            Asset,
            MaintenanceRecord.asset_id == Asset.id
        ).order_by(
            MaintenanceRecord.maintenance_date.desc()
        ).all()

        return [
            {
                **record[0].__dict__,
                'asset_code': record[1],
                'asset_name': record[2]
            }
            for record in records
        ]
