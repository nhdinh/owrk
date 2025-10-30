"""
User Read Model for MongoDB
Denormalized model optimized for query performance
"""
from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, EmailStr


class RoleReadModel(BaseModel):
    """Embedded role information"""
    id: int
    name: str
    display_name: str
    description: Optional[str] = None


class DepartmentReadModel(BaseModel):
    """Embedded department information"""
    id: int
    name: str
    code: Optional[str] = None


class UserReadModel(BaseModel):
    """
    Denormalized User model for fast reads from MongoDB
    Includes embedded related data to avoid joins
    """
    # Primary fields
    id: int
    email: EmailStr
    username: Optional[str] = None
    full_name: str

    # Status
    is_active: bool
    is_superuser: bool
    email_verified: bool
    mfa_enabled: bool

    # User type
    user_type: str = "local"  # 'local' | 'active_directory'

    # Embedded related data (denormalized)
    role: Optional[RoleReadModel] = None
    department: Optional[DepartmentReadModel] = None

    # Contact info
    phone_number: Optional[str] = None
    position: Optional[str] = None
    address: Optional[str] = None

    # Security tracking
    failed_login_attempts: int = 0
    locked_until: Optional[datetime] = None
    last_login_at: Optional[datetime] = None
    last_login_ip: Optional[str] = None
    password_changed_at: Optional[datetime] = None

    # Timestamps
    created_at: datetime
    updated_at: datetime

    # Version for optimistic locking
    version: int = 1

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }
