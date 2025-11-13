"""
Audit Log model for tracking administrative actions
"""

from sqlalchemy import Column, String, Text, JSON, event
from app.models.base import BaseModel
from app.core.utils import generate_slug


class AuditLog(BaseModel):
    """
    Audit Log model for tracking all administrative actions

    Attributes:
        id: Primary key (UUID)
        slug: URL-friendly identifier
        user_id: UUID of user who performed the action
        user_email: Email of user who performed the action
        action: Action type (CREATE, UPDATE, DELETE, etc.)
        module_name: Module where action was performed
        resource_type: Type of resource affected (setting, module, user, etc.)
        resource_id: UUID of affected resource
        description: Human-readable action description
        changes: JSON object with before/after values
        ip_address: IP address of the user
        user_agent: User agent string
        created_at: Timestamp of the action
    """

    __tablename__ = "audit_logs"
    __table_args__ = {"schema": "admin_db"}

    user_id = Column(String(32), nullable=True, index=True)  # User UUID
    user_email = Column(String(255), nullable=True)

    # Action details
    action = Column(String(50), nullable=False, index=True)  # CREATE, UPDATE, DELETE, LOGIN, etc.
    module_name = Column(String(50), nullable=False, index=True)
    resource_type = Column(String(100), nullable=False, index=True)
    resource_id = Column(String(32), nullable=True)  # UUID of affected resource

    description = Column(Text, nullable=False)

    # Change tracking
    changes = Column(JSON, nullable=True)  # {"before": {...}, "after": {...}}

    # Request metadata
    ip_address = Column(String(45), nullable=True)  # IPv6 max length
    user_agent = Column(String(500), nullable=True)

    def __repr__(self):
        return f"<AuditLog(user={self.user_email}, action={self.action}, module={self.module_name})>"


# Event listener to auto-generate slug from action, module, and user
@event.listens_for(AuditLog, "before_insert")
def generate_audit_log_slug(mapper, connection, target):
    """Auto-generate slug from action, module, and timestamp if not provided"""
    if not target.slug:
        user_short = target.user_id[:8] if target.user_id else "system"
        target.slug = generate_slug(f"{target.module_name}-{target.action}-{user_short}")


class SystemLog(BaseModel):
    """
    System Log model for tracking system-level events and errors

    Attributes:
        id: Primary key (UUID)
        slug: URL-friendly identifier
        log_level: Log level (INFO, WARNING, ERROR, CRITICAL)
        module_name: Module that generated the log
        message: Log message
        details: Additional details (JSON)
        stack_trace: Stack trace for errors
        created_at: Log timestamp
    """

    __tablename__ = "system_logs"
    __table_args__ = {"schema": "admin_db"}

    log_level = Column(String(20), nullable=False, index=True)  # INFO, WARNING, ERROR, CRITICAL
    module_name = Column(String(50), nullable=False, index=True)
    message = Column(Text, nullable=False)
    details = Column(JSON, nullable=True)
    stack_trace = Column(Text, nullable=True)

    def __repr__(self):
        return f"<SystemLog(level={self.log_level}, module={self.module_name})>"


# Event listener to auto-generate slug from log level and module
@event.listens_for(SystemLog, "before_insert")
def generate_system_log_slug(mapper, connection, target):
    """Auto-generate slug from level, module, and timestamp if not provided"""
    if not target.slug:
        target.slug = generate_slug(f"{target.log_level}-{target.module_name}")
