"""
Soft Delete Mixin
Provides soft-delete functionality for SQLAlchemy models
"""

from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import Column, Boolean, Integer, TIMESTAMP
from sqlalchemy.orm import Session

from app.models.trash import TrashItem
from app.repositories.trash_repository import TrashRepository


class SoftDeleteMixin:
    """
    Mixin to add soft-delete functionality to SQLAlchemy models

    Usage:
        class MyModel(Base, SoftDeleteMixin):
            __tablename__ = "my_table"
            id = Column(Integer, primary_key=True)
            name = Column(String(100))

    The mixin adds:
        - is_deleted: Boolean flag
        - deleted_at: Timestamp when deleted
        - deleted_by: User ID who deleted

    Methods:
        - soft_delete(db, user_id, user_email, reason): Soft delete the record
        - restore(db, user_id, user_email): Restore soft-deleted record
        - is_soft_deleted(): Check if record is soft-deleted
    """

    # Soft delete columns
    is_deleted = Column(Boolean, default=False, nullable=False, index=True)
    deleted_at = Column(TIMESTAMP, nullable=True)
    deleted_by = Column(Integer, nullable=True)

    def soft_delete(
        self,
        db: Session,
        user_id: int,
        user_email: str,
        reason: Optional[str] = None,
        module_name: str = None,
        resource_type: str = None,
        create_trash_entry: bool = True,
    ) -> Optional[TrashItem]:
        """
        Soft delete this record

        Args:
            db: Database session
            user_id: ID of user performing deletion
            user_email: Email of user performing deletion
            reason: Optional reason for deletion
            module_name: Module name (e.g., 'auth', 'asset')
            resource_type: Resource type (e.g., 'user', 'asset')
            create_trash_entry: Whether to create entry in trash table

        Returns:
            TrashItem if trash entry created, None otherwise
        """
        # Mark as deleted
        self.is_deleted = True
        self.deleted_at = datetime.utcnow()
        self.deleted_by = user_id

        trash_item = None

        # Create trash entry if requested
        if create_trash_entry and module_name and resource_type:
            # Serialize model to dict for snapshot
            resource_data = self._to_dict()

            # Get resource name (try common name fields)
            resource_name = (
                getattr(self, 'name', None)
                or getattr(self, 'title', None)
                or getattr(self, 'email', None)
                or getattr(self, 'full_name', None)
                or f"{resource_type}_{self.id}"
            )

            # Create trash item
            trash_item = TrashItem(
                module_name=module_name,
                resource_type=resource_type,
                resource_id=str(self.id),
                resource_name=resource_name,
                resource_data=resource_data,
                deleted_by=user_id,
                deleted_by_email=user_email,
                deleted_reason=reason,
                is_restorable=True,
            )

            trash_repo = TrashRepository(db)
            trash_item = trash_repo.create_trash_item(trash_item)

        db.commit()
        db.refresh(self)

        return trash_item

    def restore(
        self,
        db: Session,
        user_id: int,
        user_email: str,
    ) -> None:
        """
        Restore a soft-deleted record

        Args:
            db: Database session
            user_id: ID of user performing restoration
            user_email: Email of user performing restoration
        """
        if not self.is_deleted:
            raise ValueError("Record is not soft-deleted")

        self.is_deleted = False
        self.deleted_at = None
        self.deleted_by = None

        db.commit()
        db.refresh(self)

    def is_soft_deleted(self) -> bool:
        """Check if this record is soft-deleted"""
        return self.is_deleted is True

    def _to_dict(self) -> Dict[str, Any]:
        """
        Convert model instance to dictionary for trash snapshot

        Override this method in your model for custom serialization
        """
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)

            # Handle datetime serialization
            if isinstance(value, datetime):
                value = value.isoformat()

            result[column.name] = value

        return result


class SoftDeleteQueryMixin:
    """
    Query mixin to filter out soft-deleted records

    Usage:
        class MyRepository:
            def get_active_items(self, db: Session):
                return db.query(MyModel).filter(MyModel.is_deleted == False).all()
    """

    @classmethod
    def get_active_query(cls, db: Session):
        """Get query for non-deleted records"""
        return db.query(cls).filter(cls.is_deleted == False)

    @classmethod
    def get_deleted_query(cls, db: Session):
        """Get query for soft-deleted records"""
        return db.query(cls).filter(cls.is_deleted == True)

    @classmethod
    def get_all_query(cls, db: Session):
        """Get query for all records (including deleted)"""
        return db.query(cls)
