"""
Asset Repository
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func
from app.models.asset import Asset, AssetStatus, AssetType
from app.repositories.base_repository import BaseRepository


class AssetRepository(BaseRepository[Asset]):
    """Repository for Asset operations"""

    def __init__(self, session: Session):
        super().__init__(Asset, session)

    def get_by_code(self, asset_code: str) -> Optional[Asset]:
        """Get asset by asset code"""
        return self.session.query(Asset).filter(
            Asset.asset_code == asset_code,
            Asset.deleted_at == None
        ).first()

    def search_assets(
        self,
        search: Optional[str] = None,
        category_id: Optional[int] = None,
        status: Optional[AssetStatus] = None,
        asset_type: Optional[AssetType] = None,
        department_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 20
    ) -> tuple[List[Asset], int]:
        """
        Search and filter assets with pagination
        Returns: (assets, total_count)
        """
        query = self.session.query(Asset).filter(Asset.deleted_at == None)

        # Search by code, name, manufacturer, model, serial_number
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                or_(
                    Asset.asset_code.like(search_pattern),
                    Asset.name.like(search_pattern),
                    Asset.manufacturer.like(search_pattern),
                    Asset.model.like(search_pattern),
                    Asset.serial_number.like(search_pattern)
                )
            )

        # Filter by category
        if category_id:
            query = query.filter(Asset.category_id == category_id)

        # Filter by status
        if status:
            query = query.filter(Asset.status == status)

        # Filter by asset type
        if asset_type:
            query = query.filter(Asset.asset_type == asset_type)

        # Filter by department
        if department_id:
            query = query.filter(Asset.department_id == department_id)

        # Get total count
        total = query.count()

        # Apply pagination and ordering
        assets = query.order_by(Asset.created_at.desc()).offset(skip).limit(limit).all()

        return assets, total

    def get_assets_by_status(self, status: AssetStatus) -> List[Asset]:
        """Get all assets with specific status"""
        return self.session.query(Asset).filter(
            Asset.status == status,
            Asset.deleted_at == None
        ).all()

    def get_assets_by_category(self, category_id: int) -> List[Asset]:
        """Get all assets in a category"""
        return self.session.query(Asset).filter(
            Asset.category_id == category_id,
            Asset.deleted_at == None
        ).all()

    def get_assets_by_department(self, department_id: int) -> List[Asset]:
        """Get all assets in a department"""
        return self.session.query(Asset).filter(
            Asset.department_id == department_id,
            Asset.deleted_at == None
        ).all()

    def get_assets_assigned_to_user(self, user_id: int) -> List[Asset]:
        """Get all assets currently assigned to a user"""
        return self.session.query(Asset).filter(
            Asset.current_user_id == user_id,
            Asset.status == AssetStatus.IN_USE,
            Asset.deleted_at == None
        ).all()

    def get_fixed_assets_for_depreciation(self) -> List[Asset]:
        """Get all fixed assets that need depreciation calculation"""
        return self.session.query(Asset).filter(
            Asset.asset_type == AssetType.FIXED_ASSET,
            Asset.depreciation_method != None,
            Asset.status.in_([AssetStatus.IN_USE, AssetStatus.AVAILABLE]),
            Asset.deleted_at == None
        ).all()

    def update_status(self, asset_id: int, status: AssetStatus) -> bool:
        """Update asset status"""
        asset = self.get_by_id(asset_id)
        if asset and not asset.deleted_at:
            asset.status = status
            self.session.flush()
            return True
        return False

    def assign_to_user(self, asset_id: int, user_id: int, department_id: int) -> bool:
        """Assign asset to user"""
        asset = self.get_by_id(asset_id)
        if asset and not asset.deleted_at:
            asset.current_user_id = user_id
            asset.department_id = department_id
            asset.status = AssetStatus.IN_USE
            self.session.flush()
            return True
        return False

    def unassign_from_user(self, asset_id: int) -> bool:
        """Unassign asset from current user"""
        asset = self.get_by_id(asset_id)
        if asset and not asset.deleted_at:
            asset.current_user_id = None
            asset.status = AssetStatus.AVAILABLE
            self.session.flush()
            return True
        return False

    def soft_delete(self, asset_id: int) -> bool:
        """Soft delete an asset"""
        asset = self.get_by_id(asset_id)
        if asset and not asset.deleted_at:
            asset.deleted_at = datetime.utcnow()
            asset.status = AssetStatus.DISPOSED
            self.session.flush()
            return True
        return False

    def get_statistics(self) -> Dict[str, Any]:
        """Get asset statistics"""
        total = self.session.query(func.count(Asset.id)).filter(Asset.deleted_at == None).scalar()

        by_status = self.session.query(
            Asset.status,
            func.count(Asset.id)
        ).filter(Asset.deleted_at == None).group_by(Asset.status).all()

        by_type = self.session.query(
            Asset.asset_type,
            func.count(Asset.id)
        ).filter(Asset.deleted_at == None).group_by(Asset.asset_type).all()

        return {
            "total": total,
            "by_status": {status.value: count for status, count in by_status},
            "by_type": {asset_type.value: count for asset_type, count in by_type}
        }
