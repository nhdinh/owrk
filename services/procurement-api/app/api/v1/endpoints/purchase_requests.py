"""
Purchase Request API Endpoints
RESTful API for purchase request management with multi-level approval workflow
"""

from typing import Optional
from datetime import date
from fastapi import APIRouter, Depends, Query, Path
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, get_current_user_id
from app.services.purchase_request_service import PurchaseRequestService
from app.schemas.purchase_request_schema import (
    PurchaseRequestCreate,
    PurchaseRequestUpdate,
    PurchaseRequestResponse,
    PurchaseRequestListResponse,
    ApprovalRequest,
    RejectionRequest,
    SubmitForApprovalRequest,
)
from app.models.purchase_request import ApprovalStatus, Priority

router = APIRouter(prefix="/purchase-requests", tags=["Purchase Requests"])


@router.post("/", response_model=PurchaseRequestResponse, status_code=201)
async def create_purchase_request(
    request_data: PurchaseRequestCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create a new purchase request in DRAFT status

    **Required Fields:**
    - title: Request title
    - department_id: Department ID
    - priority: LOW, MEDIUM, HIGH, or URGENT
    - request_date: Date of request
    - procurement_type: FRAMEWORK_CONTRACT or ONE_TIME
    - items: List of items (at least 1)

    **Item Fields:**
    - product_name: Product name
    - unit: Unit of measurement
    - quantity: Quantity requested

    **Returns:**
    - Created purchase request with auto-generated request_code
    - Initial status: DRAFT
    """
    service = PurchaseRequestService(db)
    return service.create_purchase_request(request_data, current_user["id"])


@router.get("/", response_model=PurchaseRequestListResponse)
async def list_purchase_requests(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(
        100, ge=1, le=100, description="Maximum number of records to return"
    ),
    status: Optional[ApprovalStatus] = Query(
        None, description="Filter by approval status"
    ),
    priority: Optional[Priority] = Query(None, description="Filter by priority"),
    requested_by: Optional[int] = Query(
        None, description="Filter by requester user ID"
    ),
    department_id: Optional[int] = Query(None, description="Filter by department ID"),
    from_date: Optional[date] = Query(
        None, description="Filter by request date (from)"
    ),
    to_date: Optional[date] = Query(None, description="Filter by request date (to)"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    List purchase requests with pagination and filters

    **Query Parameters:**
    - skip: Number of records to skip (default: 0)
    - limit: Maximum records to return (default: 100, max: 100)
    - status: Filter by approval status (DRAFT, PENDING, LEVEL1_APPROVED, etc.)
    - priority: Filter by priority (LOW, MEDIUM, HIGH, URGENT)
    - requested_by: Filter by requester user ID
    - department_id: Filter by department ID
    - from_date: Filter by request date (from)
    - to_date: Filter by request date (to)

    **Returns:**
    - requests: List of purchase requests with items
    - total: Total count matching filters
    - page: Current page number
    - page_size: Page size
    """
    service = PurchaseRequestService(db)
    return service.list_purchase_requests(
        skip=skip,
        limit=limit,
        status=status,
        priority=priority,
        requested_by=requested_by,
        department_id=department_id,
        from_date=from_date,
        to_date=to_date,
    )


@router.get("/{request_id}", response_model=PurchaseRequestResponse)
async def get_purchase_request(
    request_id: int = Path(..., gt=0, description="Purchase request ID"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get purchase request by ID

    **Returns:**
    - Purchase request details with all items and approval information
    """
    service = PurchaseRequestService(db)
    return service.get_purchase_request(request_id)


@router.put("/{request_id}", response_model=PurchaseRequestResponse)
async def update_purchase_request(
    request_id: int = Path(..., gt=0, description="Purchase request ID"),
    request_data: PurchaseRequestUpdate = ...,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update purchase request (only allowed in DRAFT status)

    **Note:**
    - Only purchase requests in DRAFT status can be updated
    - All fields are optional

    **Returns:**
    - Updated purchase request
    """
    service = PurchaseRequestService(db)
    return service.update_purchase_request(request_id, request_data, current_user["id"])


@router.post("/{request_id}/submit", response_model=PurchaseRequestResponse)
async def submit_for_approval(
    request_id: int = Path(..., gt=0, description="Purchase request ID"),
    submit_data: SubmitForApprovalRequest = ...,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Submit purchase request for approval

    **Workflow:**
    - Status changes from DRAFT to PENDING
    - Only the requester can submit their own request

    **Returns:**
    - Updated purchase request in PENDING status
    """
    service = PurchaseRequestService(db)
    return service.submit_for_approval(request_id, current_user["id"])


@router.post("/{request_id}/approve/level1", response_model=PurchaseRequestResponse)
async def approve_level1(
    request_id: int = Path(..., gt=0, description="Purchase request ID"),
    approval_data: ApprovalRequest = ...,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Level 1 Approval (Department Manager)

    **Workflow:**
    - Status changes from PENDING to LEVEL1_APPROVED
    - Records approver ID, timestamp, and notes

    **Returns:**
    - Updated purchase request in LEVEL1_APPROVED status
    """
    service = PurchaseRequestService(db)
    return service.approve_level1(request_id, approval_data, current_user["id"])


@router.post("/{request_id}/approve/level2", response_model=PurchaseRequestResponse)
async def approve_level2(
    request_id: int = Path(..., gt=0, description="Purchase request ID"),
    approval_data: ApprovalRequest = ...,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Level 2 Approval (HR Manager)

    **Workflow:**
    - Status changes from LEVEL1_APPROVED to LEVEL2_APPROVED
    - Records approver ID, timestamp, and notes

    **Returns:**
    - Updated purchase request in LEVEL2_APPROVED status
    """
    service = PurchaseRequestService(db)
    return service.approve_level2(request_id, approval_data, current_user["id"])


@router.post("/{request_id}/approve/level3", response_model=PurchaseRequestResponse)
async def approve_level3(
    request_id: int = Path(..., gt=0, description="Purchase request ID"),
    approval_data: ApprovalRequest = ...,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Level 3 Approval (Director) - Final Approval

    **Workflow:**
    - Status changes from LEVEL2_APPROVED to APPROVED
    - Records approver ID, timestamp, and notes
    - This is the final approval - request is fully approved

    **Returns:**
    - Updated purchase request in APPROVED status (ready for procurement)
    """
    service = PurchaseRequestService(db)
    return service.approve_level3(request_id, approval_data, current_user["id"])


@router.post("/{request_id}/reject", response_model=PurchaseRequestResponse)
async def reject_purchase_request(
    request_id: int = Path(..., gt=0, description="Purchase request ID"),
    rejection_data: RejectionRequest = ...,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Reject purchase request at any approval level

    **Note:**
    - Can be rejected at any stage except APPROVED, REJECTED, or CANCELLED
    - Requires a reason (minimum 10 characters)
    - Records rejecter ID, timestamp, and reason

    **Returns:**
    - Updated purchase request in REJECTED status
    """
    service = PurchaseRequestService(db)
    return service.reject_purchase_request(
        request_id, rejection_data, current_user["id"]
    )


@router.post("/{request_id}/cancel", response_model=PurchaseRequestResponse)
async def cancel_purchase_request(
    request_id: int = Path(..., gt=0, description="Purchase request ID"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Cancel purchase request

    **Note:**
    - Only the requester can cancel their own request
    - Can only cancel DRAFT or PENDING requests

    **Returns:**
    - Updated purchase request in CANCELLED status
    """
    service = PurchaseRequestService(db)
    return service.cancel_purchase_request(request_id, current_user["id"])


@router.get("/approvals/pending", response_model=list[PurchaseRequestResponse])
async def get_pending_approvals(
    level: int = Query(1, ge=1, le=3, description="Approval level (1, 2, or 3)"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get purchase requests pending approval at a specific level

    **Query Parameters:**
    - level: Approval level (1, 2, or 3)
      - Level 1: Department Manager (PENDING status)
      - Level 2: HR Manager (LEVEL1_APPROVED status)
      - Level 3: Director (LEVEL2_APPROVED status)

    **Returns:**
    - List of purchase requests pending approval at the specified level
    """
    service = PurchaseRequestService(db)
    return service.get_pending_approvals(level)
