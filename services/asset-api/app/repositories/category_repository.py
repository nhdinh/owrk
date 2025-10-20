"""
Category Repository
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.category import AssetCategory
from app.repositories.base_repository import BaseRepository


class CategoryRepository(BaseRepository[AssetCategory]):
    """Repository for AssetCategory operations"""

    def __init__(self, session: Session):
        super().__init__(AssetCategory, session)

    def get_by_code(self, code: str) -> Optional[AssetCategory]:
        """Get category by code"""
        return self.session.query(AssetCategory).filter(AssetCategory.code == code).first()

    def get_active_categories(self) -> List[AssetCategory]:
        """Get all active categories"""
        return self.session.query(AssetCategory).filter(AssetCategory.is_active == True).all()

    def get_root_categories(self) -> List[AssetCategory]:
        """Get categories without parent (root level)"""
        return self.session.query(AssetCategory).filter(AssetCategory.parent_id == None).all()

    def get_children(self, parent_id: int) -> List[AssetCategory]:
        """Get child categories of a parent"""
        return self.session.query(AssetCategory).filter(AssetCategory.parent_id == parent_id).all()

    def deactivate(self, id: int) -> bool:
        """Deactivate a category"""
        category = self.get_by_id(id)
        if category:
            category.is_active = False
            self.session.flush()
            return True
        return False
