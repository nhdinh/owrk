"""
Role History Model - Separate Versioning Table
Tracks all changes to Role entity for audit and rollback
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.sql import func
from app.models.base import Base


class RoleHistory(Base):
    """
    Role version history table
    Stores snapshot of role entity on every update
    """
    __tablename__ = "role_history"
    __table_args__ = {'schema': 'auth_db'}

    # Primary key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # Foreign key to original role
    role_id = Column(Integer, ForeignKey('auth_db.roles.id'), nullable=False, index=True)

    # Version metadata
    version = Column(Integer, nullable=False)  # Version number (1, 2, 3, ...)
    changed_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    changed_by = Column(Integer, nullable=True)  # User ID who made the change
    change_reason = Column(String(500), nullable=True)  # Optional reason for change
    change_type = Column(String(50), nullable=False)  # 'created', 'updated', 'deleted'

    # Snapshot of role data at this version
    name = Column(String(100), nullable=False)
    display_name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    permissions = Column(JSON, nullable=True)  # Array of permission codes
    is_active = Column(Boolean, nullable=False, default=True)

    # Original timestamps (from role table)
    original_created_at = Column(DateTime(timezone=True), nullable=False)
    original_updated_at = Column(DateTime(timezone=True), nullable=False)

    def __repr__(self):
        return f"<RoleHistory(role_id={self.role_id}, version={self.version}, changed_at={self.changed_at})>"

    @classmethod
    def from_role(cls, role, changed_by: int = None, change_reason: str = None, change_type: str = "updated"):
        """
        Create a history entry from a Role object

        Args:
            role: Role model instance
            changed_by: ID of user who made the change
            change_reason: Reason for the change
            change_type: Type of change (created, updated, deleted)

        Returns:
            RoleHistory instance
        """
        return cls(
            role_id=role.id,
            version=role.version,
            changed_by=changed_by,
            change_reason=change_reason,
            change_type=change_type,
            # Snapshot all role fields
            name=role.name,
            display_name=role.display_name,
            description=role.description,
            permissions=role.permissions,
            is_active=role.is_active,
            original_created_at=role.created_at,
            original_updated_at=role.updated_at
        )
