"""
User History Model - Separate Versioning Table
Tracks all changes to User entity for audit and rollback
"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    Text,
    ForeignKey,
    Numeric,
)
from sqlalchemy.sql import func
from app.models.base import Base


class UserHistory(Base):
    """
    User version history table
    Stores snapshot of user entity on every update
    """

    __tablename__ = "user_history"
    __table_args__ = {"schema": "auth_db"}

    # Primary key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # Foreign key to original user
    user_id = Column(
        String(36), ForeignKey("auth_db.users.id"), nullable=False, index=True
    )

    # Version metadata
    version = Column(Integer, nullable=False)  # Version number (1, 2, 3, ...)
    changed_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    changed_by = Column(String(36), nullable=True)  # User ID who made the change
    change_reason = Column(String(500), nullable=True)  # Optional reason for change
    change_type = Column(
        String(50), nullable=False
    )  # 'created', 'updated', 'deleted', 'activated', 'deactivated'

    # Snapshot of user data at this version
    email = Column(String(255), nullable=False)
    username = Column(String(100), nullable=True)
    full_name = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=True)

    # User type
    user_type = Column(String(20), nullable=False, default="local")
    ad_sync_id = Column(String(255), nullable=True)

    # Status
    is_active = Column(Boolean, nullable=False, default=True)
    is_superuser = Column(Boolean, nullable=False, default=False)
    email_verified = Column(Boolean, nullable=False, default=False)

    # MFA/Security
    mfa_enabled = Column(Boolean, nullable=False, default=False)
    # Note: We don't store mfa_secret in history for security

    # Security tracking
    failed_login_attempts = Column(Integer, nullable=False, default=0)
    locked_until = Column(DateTime(timezone=True), nullable=True)
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    last_login_ip = Column(String(45), nullable=True)

    # Password management
    password_changed_at = Column(DateTime(timezone=True), nullable=True)
    require_password_change = Column(Boolean, nullable=False, default=False)

    # Department & Contact
    department_id = Column(Integer, nullable=True)
    phone_number = Column(String(20), nullable=True)
    address = Column(Text, nullable=True)
    position = Column(String(100), nullable=True)

    # Role
    role_id = Column(String(36), nullable=True)

    # Original timestamps (from user table)
    original_created_at = Column(DateTime(timezone=True), nullable=False)
    original_updated_at = Column(DateTime(timezone=True), nullable=False)

    def __repr__(self):
        return f"<UserHistory(user_id={self.user_id}, version={self.version}, changed_at={self.changed_at})>"

    @classmethod
    def from_user(
        cls,
        user,
        changed_by: int = None,
        change_reason: str = None,
        change_type: str = "updated",
    ):
        """
        Create a history entry from a User object

        Args:
            user: User model instance
            changed_by: ID of user who made the change
            change_reason: Reason for the change
            change_type: Type of change (created, updated, deleted, etc.)

        Returns:
            UserHistory instance
        """
        return cls(
            user_id=user.id,
            version=user.version,
            changed_by=changed_by,
            change_reason=change_reason,
            change_type=change_type,
            # Snapshot all user fields
            email=user.email,
            username=user.username,
            full_name=user.full_name,
            hashed_password=user.hashed_password,
            user_type=user.user_type,
            ad_sync_id=user.ad_sync_id,
            is_active=user.is_active,
            is_superuser=user.is_superuser,
            email_verified=user.email_verified,
            mfa_enabled=user.mfa_enabled,
            failed_login_attempts=user.failed_login_attempts,
            locked_until=user.locked_until,
            last_login_at=user.last_login_at,
            last_login_ip=user.last_login_ip,
            password_changed_at=user.password_changed_at,
            require_password_change=user.require_password_change,
            department_id=user.department_id,
            phone_number=user.phone_number,
            address=user.address,
            position=user.position,
            role_id=user.role_id,
            original_created_at=user.created_at,
            original_updated_at=user.updated_at,
        )
