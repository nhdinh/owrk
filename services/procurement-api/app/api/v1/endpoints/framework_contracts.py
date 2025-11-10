"""
Framework Contract API Endpoints
RESTful API for framework contract management
"""

from typing import Optional
from datetime import date
from fastapi import APIRouter, Depends, Query, Path
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.framework_contract import ContractStatus
from app.schemas.contract_schema import (
    ContractCreate,
    ContractUpdate,
    ContractResponse,
    ContractListResponse,
    ActivateContractRequest,
    TerminateContractRequest,
)

router = APIRouter(prefix="/framework-contracts", tags=["Framework Contracts"])


@router.post("/", response_model=ContractResponse, status_code=201)
async def create_contract(
    contract_data: ContractCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new framework contract"""
    from app.services.contract_service import ContractService
    from app.repositories.contract_repository import ContractRepository
    from app.repositories.vendor_repository import VendorRepository

    service = ContractService(
        db, ContractRepository(db), VendorRepository(db)
    )
    return service.create_contract(contract_data, current_user["id"])


@router.get("/", response_model=ContractListResponse)
async def list_contracts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    status: Optional[ContractStatus] = Query(None),
    vendor_id: Optional[int] = Query(None),
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List framework contracts with pagination and filters"""
    from app.services.contract_service import ContractService
    from app.repositories.contract_repository import ContractRepository
    from app.repositories.vendor_repository import VendorRepository

    service = ContractService(
        db, ContractRepository(db), VendorRepository(db)
    )

    contracts, total = service.get_contracts(
        skip=skip,
        limit=limit,
        status=status.value if status else None,
        vendor_id=vendor_id,
        from_date=from_date,
        to_date=to_date,
    )

    return ContractListResponse(
        contracts=contracts, total=total, page=skip // limit + 1, page_size=limit
    )


@router.get("/expiring", response_model=list[ContractResponse])
async def list_expiring_contracts(
    days: int = Query(30, ge=1, le=365),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get contracts expiring within specified days"""
    from app.services.contract_service import ContractService
    from app.repositories.contract_repository import ContractRepository
    from app.repositories.vendor_repository import VendorRepository

    service = ContractService(
        db, ContractRepository(db), VendorRepository(db)
    )
    return service.get_expiring_contracts(days)


@router.get("/vendor/{vendor_id}", response_model=list[ContractResponse])
async def list_vendor_contracts(
    vendor_id: int = Path(..., gt=0),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get all active contracts for a vendor"""
    from app.services.contract_service import ContractService
    from app.repositories.contract_repository import ContractRepository
    from app.repositories.vendor_repository import VendorRepository

    service = ContractService(
        db, ContractRepository(db), VendorRepository(db)
    )
    return service.get_active_contracts_by_vendor(vendor_id)


@router.get("/{contract_id}", response_model=ContractResponse)
async def get_contract(
    contract_id: int = Path(..., gt=0),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get framework contract by ID"""
    from app.services.contract_service import ContractService
    from app.repositories.contract_repository import ContractRepository
    from app.repositories.vendor_repository import VendorRepository

    service = ContractService(
        db, ContractRepository(db), VendorRepository(db)
    )
    return service.get_contract(contract_id)


@router.put("/{contract_id}", response_model=ContractResponse)
async def update_contract(
    contract_id: int,
    contract_data: ContractUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update framework contract"""
    from app.services.contract_service import ContractService
    from app.repositories.contract_repository import ContractRepository
    from app.repositories.vendor_repository import VendorRepository

    service = ContractService(
        db, ContractRepository(db), VendorRepository(db)
    )
    return service.update_contract(contract_id, contract_data, current_user["id"])


@router.delete("/{contract_id}", status_code=204)
async def delete_contract(
    contract_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete framework contract (soft delete)"""
    from app.services.contract_service import ContractService
    from app.repositories.contract_repository import ContractRepository
    from app.repositories.vendor_repository import VendorRepository

    service = ContractService(
        db, ContractRepository(db), VendorRepository(db)
    )
    service.delete_contract(contract_id, current_user["id"])
    return None


@router.post("/{contract_id}/activate", response_model=ContractResponse)
async def activate_contract(
    contract_id: int,
    request: ActivateContractRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Activate a framework contract"""
    from app.services.contract_service import ContractService
    from app.repositories.contract_repository import ContractRepository
    from app.repositories.vendor_repository import VendorRepository

    service = ContractService(
        db, ContractRepository(db), VendorRepository(db)
    )
    return service.activate_contract(contract_id, current_user["id"])


@router.post("/{contract_id}/suspend", response_model=ContractResponse)
async def suspend_contract(
    contract_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Suspend a framework contract"""
    from app.services.contract_service import ContractService
    from app.repositories.contract_repository import ContractRepository
    from app.repositories.vendor_repository import VendorRepository

    service = ContractService(
        db, ContractRepository(db), VendorRepository(db)
    )
    return service.suspend_contract(contract_id, current_user["id"])


@router.post("/{contract_id}/terminate", response_model=ContractResponse)
async def terminate_contract(
    contract_id: int,
    request: TerminateContractRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Terminate a framework contract permanently"""
    from app.services.contract_service import ContractService
    from app.repositories.contract_repository import ContractRepository
    from app.repositories.vendor_repository import VendorRepository

    service = ContractService(
        db, ContractRepository(db), VendorRepository(db)
    )
    return service.terminate_contract(contract_id, request.reason, current_user["id"])
