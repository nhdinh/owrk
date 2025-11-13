"""
Trash (Recycle Bin) model for tracking deleted items across all modules
"""

from sqlalchemy import (
    Column,
    String,
    Text,
    DateTime,
    JSON,
    Boolean,
    Integer,
    event,
)
from sqlalchemy.sql import func
from app.models.base import BaseModel
from app.core.utils import generate_slug


class TrashItem(BaseModel):
    """
    Trash Item model for soft-deleted records across all modules

    This table stores metadata about deleted items from any module,
    allowing admins to review, restore, or permanently delete items.

    Attributes:
        id: Primary key (UUID)
        slug: URL-friendly identifier
        module_name: Name of the module (auth, asset, procurement, etc.)
        resource_type: Type of resource (user, asset, purchase_order, etc.)
        resource_id: Original UUID of the deleted resource
        resource_name: Human-readable name/title of the resource
        resource_data: Full JSON snapshot of the deleted resource
        deleted_by: User UUID who deleted the item
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

    # Resource identification
    module_name = Column(String(50), nullable=False, index=True)
    resource_type = Column(String(100), nullable=False, index=True)
    resource_id = Column(String(32), nullable=False, index=True)  # UUID of deleted resource
    resource_name = Column(String(500), nullable=False)  # Display name

    # Resource data snapshot
    resource_data = Column(JSON, nullable=False)  # Full object snapshot

    # Deletion metadata
    deleted_by = Column(String(32), nullable=False, index=True)  # User UUID
    deleted_by_email = Column(String(255), nullable=True)
    deleted_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    deleted_reason = Column(Text, nullable=True)

    # Restoration control
    is_restorable = Column(Boolean, default=True, nullable=False)
    permanent_delete_at = Column(DateTime(timezone=True), nullable=True, index=True)  # Auto-delete after X days
    restore_dependencies = Column(JSON, nullable=True)  # List of dependent items

    # Additional metadata (renamed from 'metadata' to avoid SQLAlchemy reserved name)
    extra_metadata = Column(JSON, nullable=True)  # Tags, categories, custom fields

    # Restoration tracking
    restored_at = Column(DateTime(timezone=True), nullable=True)
    restored_by = Column(String(32), nullable=True)  # User UUID
    restored_by_email = Column(String(255), nullable=True)
    permanently_deleted_by = Column(String(32), nullable=True)  # User UUID who permanently deleted

    def __repr__(self):
        return f"<TrashItem(module={self.module_name}, type={self.resource_type}, id={self.resource_id})>"


# Event listener to auto-generate slug from module, resource type, and resource name
@event.listens_for(TrashItem, "before_insert")
def generate_trash_item_slug(mapper, connection, target):
    """Auto-generate slug from resource info if not provided"""
    if not target.slug:
        resource_short = target.resource_id[:8] if target.resource_id else "unknown"
        target.slug = generate_slug(f"{target.module_name}-{target.resource_type}-{resource_short}")


class TrashConfig(BaseModel):
    """
    Configuration for trash/soft-delete behavior per module

    Attributes:
        id: Primary key (UUID)
        slug: URL-friendly identifier
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

    module_name = Column(String(50), nullable=False, index=True)
    resource_type = Column(String(100), nullable=False, index=True)

    # Configuration
    auto_delete_days = Column(Integer, default=30, nullable=False)  # 0 = never auto-delete
    enable_soft_delete = Column(Boolean, default=True, nullable=False)
    enable_restore = Column(Boolean, default=True, nullable=False)
    require_approval = Column(Boolean, default=False, nullable=False)
    cascade_delete = Column(Boolean, default=False, nullable=False)

    def __repr__(self):
        return f"<TrashConfig(module={self.module_name}, type={self.resource_type})>"


# Event listener to auto-generate slug from module and resource type
@event.listens_for(TrashConfig, "before_insert")
def generate_trash_config_slug(mapper, connection, target):
    """Auto-generate slug from module and resource type if not provided"""
    if not target.slug:
        target.slug = generate_slug(f"{target.module_name}-{target.resource_type}-config")
