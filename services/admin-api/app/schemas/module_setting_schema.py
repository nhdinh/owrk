"""
Pydantic schemas for Module Settings
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field
from app.models.module_setting import SettingType, ModuleStatus


# Module Setting Schemas
class ModuleSettingBase(BaseModel):
    """Base schema for module settings"""

    module_name: str = Field(..., max_length=50)
    setting_key: str = Field(..., max_length=100)
    setting_value: Optional[str] = None
    setting_type: SettingType = SettingType.STRING
    display_name: str = Field(..., max_length=200)
    description: Optional[str] = None
    category: Optional[str] = Field(None, max_length=100)
    is_public: bool = False
    is_editable: bool = True
    default_value: Optional[str] = None
    validation_rules: Optional[str] = None


class ModuleSettingCreate(ModuleSettingBase):
    """Schema for creating a module setting"""

    pass


class ModuleSettingUpdate(BaseModel):
    """Schema for updating a module setting"""

    setting_value: Optional[str] = None
    display_name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    is_public: Optional[bool] = None
    is_editable: Optional[bool] = None
    default_value: Optional[str] = None
    validation_rules: Optional[str] = None


class ModuleSettingResponse(ModuleSettingBase):
    """Schema for module setting response"""

    id: int
    created_at: datetime
    updated_at: datetime
    updated_by: Optional[int] = None

    class Config:
        from_attributes = True


class ModuleSettingsListResponse(BaseModel):
    """Schema for list of module settings"""

    data: list[ModuleSettingResponse]
    total: int


# System Module Schemas
class SystemModuleBase(BaseModel):
    """Base schema for system modules"""

    module_name: str = Field(..., max_length=50)
    display_name: str = Field(..., max_length=200)
    description: Optional[str] = None
    version: Optional[str] = Field(None, max_length=20)
    status: ModuleStatus = ModuleStatus.ACTIVE
    api_endpoint: Optional[str] = Field(None, max_length=500)
    frontend_endpoint: Optional[str] = Field(None, max_length=500)
    icon: Optional[str] = Field(None, max_length=50)
    sort_order: int = 0
    requires_auth: bool = True
    allowed_roles: Optional[str] = None
    is_system_module: bool = False


class SystemModuleCreate(SystemModuleBase):
    """Schema for creating a system module"""

    pass


class SystemModuleUpdate(BaseModel):
    """Schema for updating a system module"""

    display_name: Optional[str] = None
    description: Optional[str] = None
    version: Optional[str] = None
    status: Optional[ModuleStatus] = None
    api_endpoint: Optional[str] = None
    frontend_endpoint: Optional[str] = None
    icon: Optional[str] = None
    sort_order: Optional[int] = None
    requires_auth: Optional[bool] = None
    allowed_roles: Optional[str] = None


class SystemModuleResponse(SystemModuleBase):
    """Schema for system module response"""

    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SystemModulesListResponse(BaseModel):
    """Schema for list of system modules"""

    data: list[SystemModuleResponse]
    total: int
