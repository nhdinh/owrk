"""
Asset Pydantic Schemas
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal

from app.models.asset import AssetType, AssetStatus, DepreciationMethod


class PermissionBase:
    name: str
    code: str
    description: Optional[str] = None
    is_active: bool = True


class PermissionResponse(PermissionBase):
    pass


# Category Schemas
class CategoryBase(BaseModel):
    name: str
    code: str
    parent_id: Optional[int] = None
    description: Optional[str] = None
    is_active: bool = True


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    parent_id: Optional[int] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class CategoryResponse(CategoryBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Asset Schemas
class AssetBase(BaseModel):
    asset_code: str
    name: str
    category_id: int
    asset_type: AssetType
    description: Optional[str] = None
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    serial_number: Optional[str] = None
    purchase_price: Decimal
    purchase_date: date
    purchase_order_id: Optional[int] = None


class AssetCreate(AssetBase):
    # Depreciation fields (for Fixed Assets)
    depreciation_rate: Optional[Decimal] = None
    depreciation_method: Optional[DepreciationMethod] = None
    useful_life_months: Optional[int] = None
    residual_value: Optional[Decimal] = None

    # Warranty
    warranty_months: Optional[int] = None
    warranty_start_date: Optional[date] = None
    warranty_end_date: Optional[date] = None
    warranty_provider: Optional[str] = None

    # Location
    location: Optional[str] = None
    department_id: Optional[int] = None

    # Created by (from JWT token)
    created_by: int


class AssetUpdate(BaseModel):
    name: Optional[str] = None
    category_id: Optional[int] = None
    description: Optional[str] = None
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    serial_number: Optional[str] = None
    status: Optional[AssetStatus] = None
    location: Optional[str] = None
    department_id: Optional[int] = None
    depreciation_rate: Optional[Decimal] = None
    depreciation_method: Optional[DepreciationMethod] = None
    useful_life_months: Optional[int] = None
    residual_value: Optional[Decimal] = None
    warranty_months: Optional[int] = None
    warranty_provider: Optional[str] = None


class AssetResponse(AssetBase):
    id: int
    status: AssetStatus
    location: Optional[str] = None
    department_id: Optional[int] = None
    current_user_id: Optional[int] = None
    qr_code: Optional[str] = None
    depreciation_rate: Optional[Decimal] = None
    depreciation_method: Optional[DepreciationMethod] = None
    useful_life_months: Optional[int] = None
    residual_value: Optional[Decimal] = None
    warranty_months: Optional[int] = None
    warranty_start_date: Optional[date] = None
    warranty_end_date: Optional[date] = None
    warranty_provider: Optional[str] = None
    created_by: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AssetListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    assets: List[AssetResponse]


# Assignment Schemas
class AssignmentCreate(BaseModel):
    asset_id: int
    user_id: int
    department_id: int
    assigned_date: date
    notes: Optional[str] = None
    assigned_by: int


class AssignmentReturn(BaseModel):
    returned_date: date
    return_condition: str
    return_notes: Optional[str] = None
    returned_by: int


class AssignmentResponse(BaseModel):
    id: int
    asset_id: int
    user_id: int
    department_id: int
    assigned_date: date
    assigned_by: int
    notes: Optional[str] = None
    returned_date: Optional[date] = None
    returned_by: Optional[int] = None
    return_condition: Optional[str] = None
    return_notes: Optional[str] = None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


# Attachment Schemas
class AttachmentCreate(BaseModel):
    asset_id: int
    file_name: str
    file_type: str
    file_url: str
    file_size: Optional[int] = None
    uploaded_by: int


class AttachmentResponse(BaseModel):
    id: int
    asset_id: int
    file_name: str
    file_type: str
    file_url: str
    file_size: Optional[int] = None
    uploaded_by: int
    created_at: datetime

    class Config:
        from_attributes = True


# Depreciation Schemas
class DepreciationRecordResponse(BaseModel):
    id: int
    asset_id: int
    period_month: int
    opening_value: Decimal
    depreciation_amount: Decimal
    closing_value: Decimal
    accumulated_depreciation: Decimal
    created_at: datetime

    class Config:
        from_attributes = True


# Maintenance Schemas
class MaintenanceCreate(BaseModel):
    asset_id: int
    maintenance_type: str  # routine, preventive, corrective, emergency
    maintenance_date: date
    description: Optional[str] = None
    cost: Optional[Decimal] = None
    technician: Optional[str] = None
    notes: Optional[str] = None


class MaintenanceUpdate(BaseModel):
    maintenance_type: Optional[str] = None
    maintenance_date: Optional[date] = None
    completed_date: Optional[date] = None
    cost: Optional[Decimal] = None
    technician: Optional[str] = None
    description: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[str] = None  # pending, in_progress, completed, cancelled


class MaintenanceResponse(BaseModel):
    id: int
    asset_id: int
    asset_code: Optional[str] = None
    asset_name: Optional[str] = None
    maintenance_type: str
    maintenance_date: date
    completed_date: Optional[date] = None
    cost: Decimal
    technician: Optional[str] = None
    description: Optional[str] = None
    notes: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
