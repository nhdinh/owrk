"""
Role Pydantic Schemas
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class RoleBase(BaseModel):
    """Base Role schema"""
    name: str = Field(..., min_length=1, max_length=100, pattern="^[a-z0-9_]+$")
    display_name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None


class RoleCreate(RoleBase):
    """Schema for creating a new role"""
    is_active: bool = True


class RoleUpdate(BaseModel):
    """Schema for updating role"""
    name: Optional[str] = Field(None, min_length=1, max_length=100, pattern="^[a-z0-9_]+$")
    display_name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    is_active: Optional[bool] = None


class RoleResponse(RoleBase):
    """Schema for role response"""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
