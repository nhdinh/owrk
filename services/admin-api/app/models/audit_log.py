"""
Audit Log model for tracking administrative actions
"""

from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, JSON
from sqlalchemy.sql import func
from app.models.base import Base


class AuditLog(Base):
    """
    Audit Log model for tracking all administrative actions

    Attributes:
        id: Primary key
        user_id: ID of user who performed the action
        user_email: Email of user who performed the action
        action: Action type (CREATE, UPDATE, DELETE, etc.)
        module_name: Module where action was performed
        resource_type: Type of resource affected (setting, module, user, etc.)
        resource_id: ID of affected resource
        description: Human-readable action description
        changes: JSON object with before/after values
        ip_address: IP address of the user
        user_agent: User agent string
        created_at: Timestamp of the action
    """

    __tablename__ = "audit_logs"
    __table_args__ = {"schema": "admin_db"}

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, nullable=True, index=True)
    user_email = Column(String(255), nullable=True)

    # Action details
    action = Column(String(50), nullable=False, index=True)  # CREATE, UPDATE, DELETE, LOGIN, etc.
    module_name = Column(String(50), nullable=False, index=True)
    resource_type = Column(String(100), nullable=False, index=True)
    resource_id = Column(String(100), nullable=True)
    description = Column(Text, nullable=False)

    # Change tracking
    changes = Column(JSON, nullable=True)  # {"before": {...}, "after": {...}}

    # Request metadata
    ip_address = Column(String(45), nullable=True)  # IPv6 max length
    user_agent = Column(String(500), nullable=True)

    # Timestamp
    created_at = Column(TIMESTAMP, server_default=func.now(), index=True)

    def __repr__(self):
        return f"<AuditLog(user={self.user_email}, action={self.action}, module={self.module_name})>"


class SystemLog(Base):
    """
    System Log model for tracking system-level events and errors

    Attributes:
        id: Primary key
        log_level: Log level (INFO, WARNING, ERROR, CRITICAL)
        module_name: Module that generated the log
        message: Log message
        details: Additional details (JSON)
        stack_trace: Stack trace for errors
        created_at: Log timestamp
    """

    __tablename__ = "system_logs"
    __table_args__ = {"schema": "admin_db"}

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    log_level = Column(String(20), nullable=False, index=True)  # INFO, WARNING, ERROR, CRITICAL
    module_name = Column(String(50), nullable=False, index=True)
    message = Column(Text, nullable=False)
    details = Column(JSON, nullable=True)
    stack_trace = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now(), index=True)

    def __repr__(self):
        return f"<SystemLog(level={self.log_level}, module={self.module_name})>"
