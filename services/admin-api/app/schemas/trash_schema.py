"""
Pydantic schemas for Trash/Recycle Bin
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field


# Trash Item Schemas
class TrashItemCreate(BaseModel):
    """Schema for creating a trash item (soft delete)"""

    module_name: str = Field(..., max_length=50)
    resource_type: str = Field(..., max_length=100)
    resource_id: str = Field(..., max_length=100)
    resource_name: str = Field(..., max_length=500)
    resource_data: Dict[str, Any]
    deleted_by: int
    deleted_by_email: Optional[str] = None
    deleted_reason: Optional[str] = None
    is_restorable: bool = True
    permanent_delete_at: Optional[datetime] = None
    restore_dependencies: Optional[List[Dict[str, Any]]] = None
    extra_metadata: Optional[Dict[str, Any]] = None


class TrashItemResponse(BaseModel):
    """Schema for trash item response"""

    id: int
    module_name: str
    resource_type: str
    resource_id: str
    resource_name: str
    resource_data: Dict[str, Any]
    deleted_by: int
    deleted_by_email: Optional[str] = None
    deleted_at: datetime
    deleted_reason: Optional[str] = None
    is_restorable: bool
    permanent_delete_at: Optional[datetime] = None
    restore_dependencies: Optional[List[Dict[str, Any]]] = None
    extra_metadata: Optional[Dict[str, Any]] = None
    restored_at: Optional[datetime] = None
    restored_by: Optional[int] = None
    restored_by_email: Optional[str] = None

    class Config:
        from_attributes = True


class TrashItemsListResponse(BaseModel):
    """Schema for list of trash items"""

    data: list[TrashItemResponse]
    total: int
    by_module: Optional[Dict[str, int]] = None  # Count per module
    by_type: Optional[Dict[str, int]] = None  # Count per resource type


class RestoreRequest(BaseModel):
    """Schema for restoring a trash item"""

    restore_reason: Optional[str] = None
    restore_dependencies: bool = False  # Whether to restore related items


class PermanentDeleteRequest(BaseModel):
    """Schema for permanent deletion"""

    confirmation: str = Field(..., description="Must be 'PERMANENTLY_DELETE' to confirm")
    reason: Optional[str] = None


# Trash Config Schemas
class TrashConfigBase(BaseModel):
    """Base schema for trash configuration"""

    module_name: str = Field(..., max_length=50)
    resource_type: str = Field(..., max_length=100)
    auto_delete_days: int = Field(30, ge=0, description="Days before permanent deletion (0 = never)")
    enable_soft_delete: bool = True
    enable_restore: bool = True
    require_approval: bool = False
    cascade_delete: bool = False


class TrashConfigCreate(TrashConfigBase):
    """Schema for creating trash configuration"""

    pass


class TrashConfigUpdate(BaseModel):
    """Schema for updating trash configuration"""

    auto_delete_days: Optional[int] = Field(None, ge=0)
    enable_soft_delete: Optional[bool] = None
    enable_restore: Optional[bool] = None
    require_approval: Optional[bool] = None
    cascade_delete: Optional[bool] = None


class TrashConfigResponse(TrashConfigBase):
    """Schema for trash configuration response"""

    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TrashStatsResponse(BaseModel):
    """Schema for trash statistics"""

    total_items: int
    total_size_kb: Optional[int] = None  # Estimated size
    by_module: Dict[str, int]
    by_type: Dict[str, int]
    restorable_count: int
    scheduled_for_deletion: int
    oldest_item: Optional[datetime] = None
    newest_item: Optional[datetime] = None
