"""
Framework Contract Pydantic Schemas
Request and response models for contract operations
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator

from app.models.framework_contract import ContractStatus


# ===== Contract Schemas =====

class ContractBase(BaseModel):
    """Base contract schema"""

    contract_name: str = Field(..., min_length=1, max_length=255)
    vendor_id: int = Field(..., gt=0)
    contract_value: Decimal = Field(..., ge=0)
    start_date: date
    end_date: date
    terms_and_conditions: Optional[str] = None
    payment_terms: Optional[str] = None
    delivery_terms: Optional[str] = None
    contract_file_url: Optional[str] = Field(None, max_length=500)

    @field_validator("end_date")
    @classmethod
    def validate_end_date(cls, v, info):
        """Validate that end_date is after start_date"""
        if "start_date" in info.data and v < info.data["start_date"]:
            raise ValueError("end_date must be after start_date")
        return v


class ContractCreate(ContractBase):
    """Schema for creating contract"""

    pass


class ContractUpdate(BaseModel):
    """Schema for updating contract"""

    contract_name: Optional[str] = Field(None, min_length=1, max_length=255)
    contract_value: Optional[Decimal] = Field(None, ge=0)
    end_date: Optional[date] = None
    terms_and_conditions: Optional[str] = None
    payment_terms: Optional[str] = None
    delivery_terms: Optional[str] = None
    contract_file_url: Optional[str] = Field(None, max_length=500)
    status: Optional[ContractStatus] = None


class VendorBasic(BaseModel):
    """Vendor basic info for contract response"""

    id: int
    vendor_code: str
    name: str

    class Config:
        from_attributes = True


class ContractResponse(ContractBase):
    """Schema for contract response"""

    id: int
    contract_code: str
    vendor: Optional[VendorBasic] = None
    status: ContractStatus
    created_by: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ContractListResponse(BaseModel):
    """Schema for paginated contract list"""

    contracts: List[ContractResponse]
    total: int
    page: int
    page_size: int


class ActivateContractRequest(BaseModel):
    """Schema for activating a contract"""

    reason: Optional[str] = Field(None, max_length=500)


class TerminateContractRequest(BaseModel):
    """Schema for terminating a contract"""

    reason: str = Field(..., min_length=1, max_length=1000)
    termination_date: Optional[date] = None
