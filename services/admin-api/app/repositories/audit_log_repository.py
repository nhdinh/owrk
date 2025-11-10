"""
Repository for Audit Log data access
"""

from typing import Optional, List, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc

from app.models.audit_log import AuditLog, SystemLog


class AuditLogRepository:
    """Repository for audit logs operations"""

    def __init__(self, db: Session):
        self.db = db

    def create(self, log: AuditLog) -> AuditLog:
        """Create a new audit log entry"""
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        return log

    def get_by_id(self, log_id: int) -> Optional[AuditLog]:
        """Get audit log by ID"""
        return self.db.query(AuditLog).filter(AuditLog.id == log_id).first()

    def get_logs(
        self,
        skip: int = 0,
        limit: int = 100,
        user_id: Optional[int] = None,
        module_name: Optional[str] = None,
        action: Optional[str] = None,
        resource_type: Optional[str] = None,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
    ) -> Tuple[List[AuditLog], int]:
        """Get audit logs with filters"""
        query = self.db.query(AuditLog)

        if user_id:
            query = query.filter(AuditLog.user_id == user_id)

        if module_name:
            query = query.filter(AuditLog.module_name == module_name)

        if action:
            query = query.filter(AuditLog.action == action)

        if resource_type:
            query = query.filter(AuditLog.resource_type == resource_type)

        if from_date:
            query = query.filter(AuditLog.created_at >= from_date)

        if to_date:
            query = query.filter(AuditLog.created_at <= to_date)

        # Order by most recent first
        query = query.order_by(desc(AuditLog.created_at))

        total = query.count()
        logs = query.offset(skip).limit(limit).all()

        return logs, total

    def delete_old_logs(self, retention_days: int) -> int:
        """Delete audit logs older than retention period"""
        cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
        result = self.db.query(AuditLog).filter(
            AuditLog.created_at < cutoff_date
        ).delete()
        self.db.commit()
        return result


class SystemLogRepository:
    """Repository for system logs operations"""

    def __init__(self, db: Session):
        self.db = db

    def create(self, log: SystemLog) -> SystemLog:
        """Create a new system log entry"""
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        return log

    def get_by_id(self, log_id: int) -> Optional[SystemLog]:
        """Get system log by ID"""
        return self.db.query(SystemLog).filter(SystemLog.id == log_id).first()

    def get_logs(
        self,
        skip: int = 0,
        limit: int = 100,
        log_level: Optional[str] = None,
        module_name: Optional[str] = None,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
    ) -> Tuple[List[SystemLog], int]:
        """Get system logs with filters"""
        query = self.db.query(SystemLog)

        if log_level:
            query = query.filter(SystemLog.log_level == log_level)

        if module_name:
            query = query.filter(SystemLog.module_name == module_name)

        if from_date:
            query = query.filter(SystemLog.created_at >= from_date)

        if to_date:
            query = query.filter(SystemLog.created_at <= to_date)

        # Order by most recent first
        query = query.order_by(desc(SystemLog.created_at))

        total = query.count()
        logs = query.offset(skip).limit(limit).all()

        return logs, total

    def delete_old_logs(self, retention_days: int) -> int:
        """Delete system logs older than retention period"""
        cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
        result = self.db.query(SystemLog).filter(
            SystemLog.created_at < cutoff_date
        ).delete()
        self.db.commit()
        return result
