"""
Trash Repository - Data access layer for trash/recycle bin operations
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_

from app.models.trash import TrashItem, TrashConfig


class TrashRepository:
    """Repository for trash item operations"""

    def __init__(self, db: Session):
        self.db = db

    def create_trash_item(self, trash_item: TrashItem) -> TrashItem:
        """Soft delete an item by adding it to trash"""
        self.db.add(trash_item)
        self.db.commit()
        self.db.refresh(trash_item)
        return trash_item

    def get_trash_items(
        self,
        module_name: Optional[str] = None,
        resource_type: Optional[str] = None,
        deleted_by: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        is_restorable: Optional[bool] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[List[TrashItem], int]:
        """
        Get trash items with filters and pagination

        Returns:
            tuple: (items, total_count)
        """
        query = self.db.query(TrashItem).filter(TrashItem.restored_at.is_(None))

        # Apply filters
        if module_name:
            query = query.filter(TrashItem.module_name == module_name)
        if resource_type:
            query = query.filter(TrashItem.resource_type == resource_type)
        if deleted_by:
            query = query.filter(TrashItem.deleted_by == deleted_by)
        if start_date:
            query = query.filter(TrashItem.deleted_at >= start_date)
        if end_date:
            query = query.filter(TrashItem.deleted_at <= end_date)
        if is_restorable is not None:
            query = query.filter(TrashItem.is_restorable == is_restorable)

        # Get total count
        total = query.count()

        # Apply pagination and ordering
        items = query.order_by(TrashItem.deleted_at.desc()).offset(skip).limit(limit).all()

        return items, total

    def get_trash_by_id(self, trash_id: int) -> Optional[TrashItem]:
        """Get a specific trash item by ID"""
        return self.db.query(TrashItem).filter(TrashItem.id == trash_id).first()

    def get_trash_by_resource(
        self, module_name: str, resource_type: str, resource_id: str
    ) -> Optional[TrashItem]:
        """Get trash item by resource identifiers"""
        return (
            self.db.query(TrashItem)
            .filter(
                and_(
                    TrashItem.module_name == module_name,
                    TrashItem.resource_type == resource_type,
                    TrashItem.resource_id == resource_id,
                    TrashItem.restored_at.is_(None),
                )
            )
            .first()
        )

    def restore_item(
        self, trash_id: int, restored_by: int, restored_by_email: str
    ) -> Optional[TrashItem]:
        """Mark item as restored"""
        trash_item = self.get_trash_by_id(trash_id)
        if not trash_item:
            return None

        trash_item.restored_at = datetime.utcnow()
        trash_item.restored_by = restored_by
        trash_item.restored_by_email = restored_by_email

        self.db.commit()
        self.db.refresh(trash_item)
        return trash_item

    def permanent_delete(self, trash_id: int) -> bool:
        """Permanently delete a trash item"""
        trash_item = self.get_trash_by_id(trash_id)
        if not trash_item:
            return False

        self.db.delete(trash_item)
        self.db.commit()
        return True

    def get_trash_stats(self) -> Dict[str, Any]:
        """Get trash statistics for dashboard"""
        # Total items in trash (not restored)
        total_items = (
            self.db.query(func.count(TrashItem.id))
            .filter(TrashItem.restored_at.is_(None))
            .scalar()
        )

        # Count by module
        by_module = dict(
            self.db.query(TrashItem.module_name, func.count(TrashItem.id))
            .filter(TrashItem.restored_at.is_(None))
            .group_by(TrashItem.module_name)
            .all()
        )

        # Count by resource type
        by_type = dict(
            self.db.query(TrashItem.resource_type, func.count(TrashItem.id))
            .filter(TrashItem.restored_at.is_(None))
            .group_by(TrashItem.resource_type)
            .all()
        )

        # Restorable count
        restorable_count = (
            self.db.query(func.count(TrashItem.id))
            .filter(
                and_(TrashItem.restored_at.is_(None), TrashItem.is_restorable == True)
            )
            .scalar()
        )

        # Scheduled for deletion
        scheduled_for_deletion = (
            self.db.query(func.count(TrashItem.id))
            .filter(
                and_(
                    TrashItem.restored_at.is_(None),
                    TrashItem.permanent_delete_at.isnot(None),
                    TrashItem.permanent_delete_at <= datetime.utcnow(),
                )
            )
            .scalar()
        )

        # Oldest and newest items
        oldest_item = (
            self.db.query(func.min(TrashItem.deleted_at))
            .filter(TrashItem.restored_at.is_(None))
            .scalar()
        )
        newest_item = (
            self.db.query(func.max(TrashItem.deleted_at))
            .filter(TrashItem.restored_at.is_(None))
            .scalar()
        )

        return {
            "total_items": total_items or 0,
            "by_module": by_module,
            "by_type": by_type,
            "restorable_count": restorable_count or 0,
            "scheduled_for_deletion": scheduled_for_deletion or 0,
            "oldest_item": oldest_item,
            "newest_item": newest_item,
        }

    def cleanup_old_items(self, module_name: str, resource_type: str) -> int:
        """
        Cleanup old items based on trash config

        Returns:
            Number of items permanently deleted
        """
        config = self.get_trash_config(module_name, resource_type)
        if not config or config.auto_delete_days == 0:
            return 0

        cutoff_date = datetime.utcnow() - timedelta(days=config.auto_delete_days)

        # Delete items older than cutoff date
        deleted_count = (
            self.db.query(TrashItem)
            .filter(
                and_(
                    TrashItem.module_name == module_name,
                    TrashItem.resource_type == resource_type,
                    TrashItem.restored_at.is_(None),
                    TrashItem.deleted_at <= cutoff_date,
                )
            )
            .delete(synchronize_session=False)
        )

        self.db.commit()
        return deleted_count

    def cleanup_scheduled_items(self) -> int:
        """
        Cleanup items with permanent_delete_at <= now

        Returns:
            Number of items permanently deleted
        """
        deleted_count = (
            self.db.query(TrashItem)
            .filter(
                and_(
                    TrashItem.restored_at.is_(None),
                    TrashItem.permanent_delete_at.isnot(None),
                    TrashItem.permanent_delete_at <= datetime.utcnow(),
                )
            )
            .delete(synchronize_session=False)
        )

        self.db.commit()
        return deleted_count

    # Trash Config Methods
    def get_trash_config(
        self, module_name: str, resource_type: str
    ) -> Optional[TrashConfig]:
        """Get trash configuration for a specific module/resource"""
        return (
            self.db.query(TrashConfig)
            .filter(
                and_(
                    TrashConfig.module_name == module_name,
                    TrashConfig.resource_type == resource_type,
                )
            )
            .first()
        )

    def get_all_trash_configs(
        self, module_name: Optional[str] = None
    ) -> List[TrashConfig]:
        """Get all trash configurations, optionally filtered by module"""
        query = self.db.query(TrashConfig)
        if module_name:
            query = query.filter(TrashConfig.module_name == module_name)
        return query.all()

    def create_trash_config(self, config: TrashConfig) -> TrashConfig:
        """Create new trash configuration"""
        self.db.add(config)
        self.db.commit()
        self.db.refresh(config)
        return config

    def update_trash_config(
        self, config_id: int, update_data: Dict[str, Any]
    ) -> Optional[TrashConfig]:
        """Update trash configuration"""
        config = self.db.query(TrashConfig).filter(TrashConfig.id == config_id).first()
        if not config:
            return None

        for key, value in update_data.items():
            if hasattr(config, key) and value is not None:
                setattr(config, key, value)

        config.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(config)
        return config

    def delete_trash_config(self, config_id: int) -> bool:
        """Delete trash configuration"""
        config = self.db.query(TrashConfig).filter(TrashConfig.id == config_id).first()
        if not config:
            return False

        self.db.delete(config)
        self.db.commit()
        return True
