"""
Trash (Recycle Bin) model for tracking deleted items across all modules
"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    TIMESTAMP,
    JSON,
    Boolean,
)
from sqlalchemy.sql import func
from app.models.base import Base


class TrashItem(Base):
    """
    Trash Item model for soft-deleted records across all modules

    This table stores metadata about deleted items from any module,
    allowing admins to review, restore, or permanently delete items.

    Attributes:
        id: Primary key
        module_name: Name of the module (auth, asset, procurement, etc.)
        resource_type: Type of resource (user, asset, purchase_order, etc.)
        resource_id: Original ID of the deleted resource
        resource_name: Human-readable name/title of the resource
        resource_data: Full JSON snapshot of the deleted resource
        deleted_by: User ID who deleted the item
        deleted_by_email: Email of user who deleted
        deleted_at: Timestamp when item was deleted
        deleted_reason: Optional reason for deletion
        is_restorable: Whether item can be restored
        permanent_delete_at: Scheduled date for permanent deletion
        restore_dependencies: JSON array of dependent items that need restoration
        extra_metadata: Additional metadata (tags, categories, etc.)
    """

    __tablename__ = "trash_items"
    __table_args__ = {"schema": "admin_db"}

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # Resource identification
    module_name = Column(String(50), nullable=False, index=True)
    resource_type = Column(String(100), nullable=False, index=True)
    resource_id = Column(String(100), nullable=False, index=True)  # String to support various ID types
    resource_name = Column(String(500), nullable=False)  # Display name

    # Resource data snapshot
    resource_data = Column(JSON, nullable=False)  # Full object snapshot

    # Deletion metadata
    deleted_by = Column(Integer, nullable=False, index=True)
    deleted_by_email = Column(String(255), nullable=True)
    deleted_at = Column(TIMESTAMP, server_default=func.now(), nullable=False, index=True)
    deleted_reason = Column(Text, nullable=True)

    # Restoration control
    is_restorable = Column(Boolean, default=True, nullable=False)
    permanent_delete_at = Column(TIMESTAMP, nullable=True, index=True)  # Auto-delete after X days
    restore_dependencies = Column(JSON, nullable=True)  # List of dependent items

    # Additional metadata (renamed from 'metadata' to avoid SQLAlchemy reserved name)
    extra_metadata = Column(JSON, nullable=True)  # Tags, categories, custom fields

    # Restoration tracking
    restored_at = Column(TIMESTAMP, nullable=True)
    restored_by = Column(Integer, nullable=True)
    restored_by_email = Column(String(255), nullable=True)

    def __repr__(self):
        return f"<TrashItem(module={self.module_name}, type={self.resource_type}, id={self.resource_id})>"


class TrashConfig(Base):
    """
    Configuration for trash/soft-delete behavior per module

    Attributes:
        id: Primary key
        module_name: Name of the module
        resource_type: Type of resource
        auto_delete_days: Days before permanent deletion (0 = never)
        enable_soft_delete: Whether soft delete is enabled
        enable_restore: Whether restoration is allowed
        require_approval: Whether restoration requires admin approval
        cascade_delete: Whether to cascade delete related items
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """

    __tablename__ = "trash_config"
    __table_args__ = {"schema": "admin_db"}

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    module_name = Column(String(50), nullable=False, index=True)
    resource_type = Column(String(100), nullable=False, index=True)

    # Configuration
    auto_delete_days = Column(Integer, default=30, nullable=False)  # 0 = never auto-delete
    enable_soft_delete = Column(Boolean, default=True, nullable=False)
    enable_restore = Column(Boolean, default=True, nullable=False)
    require_approval = Column(Boolean, default=False, nullable=False)
    cascade_delete = Column(Boolean, default=False, nullable=False)

    # Metadata
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<TrashConfig(module={self.module_name}, type={self.resource_type})>"
