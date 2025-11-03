"""
Vendor API Endpoints
RESTful API for vendor management
"""

from typing import Optional
from decimal import Decimal
from fastapi import APIRouter, Depends, Query, Path
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, get_current_user_id
from app.services.vendor_service import VendorService
from app.schemas.vendor_schema import (
    VendorCreate,
    VendorUpdate,
    VendorResponse,
    VendorListResponse,
    VendorRatingUpdate,
    VendorBlacklistRequest
)
from app.models.vendor import VendorStatus

router = APIRouter(prefix="/vendors", tags=["Vendors"])


@router.post("/", response_model=VendorResponse, status_code=201)
async def create_vendor(
    vendor_data: VendorCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new vendor

    **Required Fields:**
    - company_name: Company name (1-255 characters)

    **Optional Fields:**
    - tax_code: Tax identification number (10 or 13 digits)
    - contact_person: Contact person name
    - email: Email address
    - phone: Phone number
    - address: Full address
    - website: Website URL
    - notes: Additional notes

    **Returns:**
    - Created vendor with auto-generated vendor_code
    - Initial status: ACTIVE
    - Initial rating: 0.00
    """
    service = VendorService(db)
    return service.create_vendor(vendor_data, current_user["id"])


@router.get("/", response_model=VendorListResponse)
async def list_vendors(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum number of records to return"),
    status: Optional[VendorStatus] = Query(None, description="Filter by vendor status"),
    search: Optional[str] = Query(None, description="Search in company name, vendor code, email"),
    min_rating: Optional[Decimal] = Query(None, ge=0, le=5, description="Minimum rating filter"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List vendors with pagination and filters

    **Query Parameters:**
    - skip: Number of records to skip (default: 0)
    - limit: Maximum records to return (default: 100, max: 100)
    - status: Filter by status (ACTIVE, INACTIVE, BLACKLISTED)
    - search: Search term for company name, vendor code, or email
    - min_rating: Minimum rating (0-5)

    **Returns:**
    - vendors: List of vendors
    - total: Total count matching filters
    - page: Current page number
    - page_size: Records per page
    """
    service = VendorService(db)
    return service.list_vendors(
        skip=skip,
        limit=limit,
        status=status,
        search=search,
        min_rating=min_rating
    )


@router.get("/{vendor_id}", response_model=VendorResponse)
async def get_vendor(
    vendor_id: int = Path(..., gt=0, description="Vendor ID"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get vendor details by ID

    **Path Parameters:**
    - vendor_id: Vendor ID (must be > 0)

    **Returns:**
    - Complete vendor information including:
      - Basic info (code, company name, contact details)
      - Rating and status
      - Timestamps (created_at, updated_at)

    **Errors:**
    - 404: Vendor not found
    """
    service = VendorService(db)
    return service.get_vendor(vendor_id)


@router.put("/{vendor_id}", response_model=VendorResponse)
async def update_vendor(
    vendor_data: VendorUpdate,
    vendor_id: int = Path(..., gt=0, description="Vendor ID"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update vendor information

    **Path Parameters:**
    - vendor_id: Vendor ID

    **Request Body:**
    - All fields are optional
    - Only provided fields will be updated
    - Validates email, phone, and tax code format if provided

    **Returns:**
    - Updated vendor information

    **Errors:**
    - 400: Validation error (invalid email/phone/tax code format, duplicate tax code)
    - 404: Vendor not found
    """
    service = VendorService(db)
    return service.update_vendor(vendor_id, vendor_data, current_user["id"])


@router.delete("/{vendor_id}")
async def delete_vendor(
    vendor_id: int = Path(..., gt=0, description="Vendor ID"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete vendor (soft delete - sets status to INACTIVE)

    **Path Parameters:**
    - vendor_id: Vendor ID

    **Note:**
    - This is a soft delete operation
    - Vendor status will be set to INACTIVE
    - Vendor data is preserved in database
    - Use blacklist endpoint for vendors with serious issues

    **Returns:**
    - Success message

    **Errors:**
    - 404: Vendor not found
    """
    service = VendorService(db)
    return service.delete_vendor(vendor_id, current_user["id"])


@router.post("/{vendor_id}/activate", response_model=VendorResponse)
async def activate_vendor(
    vendor_id: int = Path(..., gt=0, description="Vendor ID"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Activate a vendor

    **Path Parameters:**
    - vendor_id: Vendor ID

    **Business Rules:**
    - Cannot activate a BLACKLISTED vendor
    - Changes status to ACTIVE
    - Logs activation in vendor notes

    **Returns:**
    - Updated vendor with ACTIVE status

    **Errors:**
    - 400: Cannot activate blacklisted vendor
    - 404: Vendor not found
    """
    service = VendorService(db)
    return service.activate_vendor(vendor_id, current_user["id"])


@router.post("/{vendor_id}/deactivate", response_model=VendorResponse)
async def deactivate_vendor(
    vendor_id: int = Path(..., gt=0, description="Vendor ID"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Deactivate a vendor

    **Path Parameters:**
    - vendor_id: Vendor ID

    **Note:**
    - Changes status to INACTIVE
    - Vendor can be reactivated later
    - Use for temporary suspension

    **Returns:**
    - Updated vendor with INACTIVE status

    **Errors:**
    - 404: Vendor not found
    """
    service = VendorService(db)
    return service.deactivate_vendor(vendor_id, current_user["id"])


@router.post("/{vendor_id}/blacklist", response_model=VendorResponse)
async def blacklist_vendor(
    blacklist_data: VendorBlacklistRequest,
    vendor_id: int = Path(..., gt=0, description="Vendor ID"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Blacklist a vendor

    **Path Parameters:**
    - vendor_id: Vendor ID

    **Request Body:**
    - reason: Reason for blacklisting (min 10 characters, required)

    **Business Rules:**
    - Changes status to BLACKLISTED
    - Cannot be reactivated (must be removed from blacklist manually)
    - Reason is logged in vendor notes
    - Use for vendors with serious compliance/quality issues

    **Returns:**
    - Updated vendor with BLACKLISTED status

    **Errors:**
    - 400: Invalid reason (too short)
    - 404: Vendor not found
    """
    service = VendorService(db)
    return service.blacklist_vendor(vendor_id, blacklist_data, current_user["id"])


@router.put("/{vendor_id}/rating", response_model=VendorResponse)
async def update_vendor_rating(
    rating_data: VendorRatingUpdate,
    vendor_id: int = Path(..., gt=0, description="Vendor ID"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update vendor rating

    **Path Parameters:**
    - vendor_id: Vendor ID

    **Request Body:**
    - rating: Rating from 0.00 to 5.00 (max 2 decimal places)

    **Validation:**
    - Rating must be between 0 and 5
    - Maximum 2 decimal places allowed

    **Returns:**
    - Updated vendor with new rating

    **Errors:**
    - 400: Invalid rating (out of range or too many decimal places)
    - 404: Vendor not found
    """
    service = VendorService(db)
    return service.update_rating(vendor_id, rating_data, current_user["id"])


@router.get("/active/list", response_model=list[VendorResponse])
async def get_active_vendors(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all active vendors

    **Use Case:**
    - Populate dropdown lists in forms
    - Get vendors available for quotations/orders

    **Returns:**
    - List of all vendors with ACTIVE status
    """
    service = VendorService(db)
    return service.get_active_vendors()


@router.get("/top-rated/list", response_model=list[VendorResponse])
async def get_top_rated_vendors(
    limit: int = Query(10, ge=1, le=50, description="Number of top vendors to return"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get top-rated active vendors

    **Query Parameters:**
    - limit: Number of vendors to return (default: 10, max: 50)

    **Business Rules:**
    - Only includes ACTIVE vendors
    - Ordered by rating (highest first)

    **Use Case:**
    - Show preferred vendors
    - Suggest vendors for new procurement requests

    **Returns:**
    - List of top-rated vendors
    """
    service = VendorService(db)
    return service.get_top_rated_vendors(limit)
