"""
Pydantic schemas for Audit Logs
"""

from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class AuditLogCreate(BaseModel):
    """Schema for creating an audit log entry"""

    user_id: Optional[int] = None
    user_email: Optional[str] = None
    action: str = Field(..., max_length=50)
    module_name: str = Field(..., max_length=50)
    resource_type: str = Field(..., max_length=100)
    resource_id: Optional[str] = Field(None, max_length=100)
    description: str
    changes: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = Field(None, max_length=45)
    user_agent: Optional[str] = Field(None, max_length=500)


class AuditLogResponse(BaseModel):
    """Schema for audit log response"""

    id: int
    user_id: Optional[int] = None
    user_email: Optional[str] = None
    action: str
    module_name: str
    resource_type: str
    resource_id: Optional[str] = None
    description: str
    changes: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class AuditLogsListResponse(BaseModel):
    """Schema for list of audit logs"""

    data: list[AuditLogResponse]
    total: int


class SystemLogCreate(BaseModel):
    """Schema for creating a system log entry"""

    log_level: str = Field(..., max_length=20)
    module_name: str = Field(..., max_length=50)
    message: str
    details: Optional[Dict[str, Any]] = None
    stack_trace: Optional[str] = None


class SystemLogResponse(BaseModel):
    """Schema for system log response"""

    id: int
    log_level: str
    module_name: str
    message: str
    details: Optional[Dict[str, Any]] = None
    stack_trace: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class SystemLogsListResponse(BaseModel):
    """Schema for list of system logs"""

    data: list[SystemLogResponse]
    total: int
