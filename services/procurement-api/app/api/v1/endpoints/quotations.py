"""
Quotation API Endpoints
RESTful API for quotation management
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query, Path
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.quotation import QuotationStatus
from app.schemas.quotation_schema import (
    QuotationCreate,
    QuotationUpdate,
    QuotationResponse,
    QuotationListResponse,
    QuotationComparison,
    AcceptQuotationRequest,
    RejectQuotationRequest,
)

router = APIRouter(prefix="/quotations", tags=["Quotations"])


@router.post("/", response_model=QuotationResponse, status_code=201)
async def create_quotation(
    quotation_data: QuotationCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new quotation"""
    from app.services.quotation_service import QuotationService
    from app.repositories.quotation_repository import QuotationRepository
    from app.repositories.purchase_request_repository import PurchaseRequestRepository
    from app.repositories.vendor_repository import VendorRepository

    service = QuotationService(
        db,
        QuotationRepository(db),
        PurchaseRequestRepository(db),
        VendorRepository(db)
    )
    return service.create_quotation(quotation_data, current_user["id"])


@router.get("/", response_model=QuotationListResponse)
async def list_quotations(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    status: Optional[QuotationStatus] = Query(None),
    purchase_request_id: Optional[int] = Query(None),
    vendor_id: Optional[int] = Query(None),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List quotations with pagination and filters"""
    from app.services.quotation_service import QuotationService
    from app.repositories.quotation_repository import QuotationRepository
    from app.repositories.purchase_request_repository import PurchaseRequestRepository
    from app.repositories.vendor_repository import VendorRepository

    service = QuotationService(
        db,
        QuotationRepository(db),
        PurchaseRequestRepository(db),
        VendorRepository(db)
    )

    quotations, total = service.get_quotations(
        skip=skip,
        limit=limit,
        status=status.value if status else None,
        purchase_request_id=purchase_request_id,
        vendor_id=vendor_id
    )

    return QuotationListResponse(
        quotations=quotations,
        total=total,
        page=skip // limit + 1,
        page_size=limit
    )


@router.get("/{quotation_id}", response_model=QuotationResponse)
async def get_quotation(
    quotation_id: int = Path(..., gt=0),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get quotation by ID"""
    from app.services.quotation_service import QuotationService
    from app.repositories.quotation_repository import QuotationRepository
    from app.repositories.purchase_request_repository import PurchaseRequestRepository
    from app.repositories.vendor_repository import VendorRepository

    service = QuotationService(
        db,
        QuotationRepository(db),
        PurchaseRequestRepository(db),
        VendorRepository(db)
    )
    return service.get_quotation(quotation_id)


@router.put("/{quotation_id}", response_model=QuotationResponse)
async def update_quotation(
    quotation_id: int,
    quotation_data: QuotationUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update quotation"""
    from app.services.quotation_service import QuotationService
    from app.repositories.quotation_repository import QuotationRepository
    from app.repositories.purchase_request_repository import PurchaseRequestRepository
    from app.repositories.vendor_repository import VendorRepository

    service = QuotationService(
        db,
        QuotationRepository(db),
        PurchaseRequestRepository(db),
        VendorRepository(db)
    )
    return service.update_quotation(quotation_id, quotation_data, current_user["id"])


@router.delete("/{quotation_id}", status_code=204)
async def delete_quotation(
    quotation_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete quotation"""
    from app.services.quotation_service import QuotationService
    from app.repositories.quotation_repository import QuotationRepository
    from app.repositories.purchase_request_repository import PurchaseRequestRepository
    from app.repositories.vendor_repository import VendorRepository

    service = QuotationService(
        db,
        QuotationRepository(db),
        PurchaseRequestRepository(db),
        VendorRepository(db)
    )
    service.delete_quotation(quotation_id, current_user["id"])
    return None


@router.post("/{quotation_id}/accept", response_model=QuotationResponse)
async def accept_quotation(
    quotation_id: int,
    request: AcceptQuotationRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Accept a quotation"""
    from app.services.quotation_service import QuotationService
    from app.repositories.quotation_repository import QuotationRepository
    from app.repositories.purchase_request_repository import PurchaseRequestRepository
    from app.repositories.vendor_repository import VendorRepository

    service = QuotationService(
        db,
        QuotationRepository(db),
        PurchaseRequestRepository(db),
        VendorRepository(db)
    )
    return service.accept_quotation(quotation_id, current_user["id"])


@router.post("/{quotation_id}/reject", response_model=QuotationResponse)
async def reject_quotation(
    quotation_id: int,
    request: RejectQuotationRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Reject a quotation"""
    from app.services.quotation_service import QuotationService
    from app.repositories.quotation_repository import QuotationRepository
    from app.repositories.purchase_request_repository import PurchaseRequestRepository
    from app.repositories.vendor_repository import VendorRepository

    service = QuotationService(
        db,
        QuotationRepository(db),
        PurchaseRequestRepository(db),
        VendorRepository(db)
    )
    return service.reject_quotation(quotation_id, current_user["id"])


@router.get("/comparison/{purchase_request_id}", response_model=QuotationComparison)
async def get_quotation_comparison(
    purchase_request_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get quotation comparison for a purchase request"""
    from app.services.quotation_service import QuotationService
    from app.repositories.quotation_repository import QuotationRepository
    from app.repositories.purchase_request_repository import PurchaseRequestRepository
    from app.repositories.vendor_repository import VendorRepository

    service = QuotationService(
        db,
        QuotationRepository(db),
        PurchaseRequestRepository(db),
        VendorRepository(db)
    )
    return service.get_quotation_comparison(purchase_request_id)
