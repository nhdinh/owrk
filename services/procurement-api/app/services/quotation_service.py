"""
Quotation Service
Business logic for quotation management
"""

from typing import Optional
from datetime import datetime
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.quotation import Quotation, QuotationItem, QuotationStatus
from app.repositories.quotation_repository import QuotationRepository
from app.repositories.purchase_request_repository import PurchaseRequestRepository
from app.repositories.vendor_repository import VendorRepository
from app.schemas.quotation_schema import QuotationCreate, QuotationUpdate
from app.utils.code_generator import generate_quotation_code


class QuotationService:
    """Service for quotation business logic"""

    def __init__(
        self,
        db: Session,
        quotation_repo: QuotationRepository,
        purchase_request_repo: PurchaseRequestRepository,
        vendor_repo: VendorRepository
    ):
        self.db = db
        self.quotation_repo = quotation_repo
        self.purchase_request_repo = purchase_request_repo
        self.vendor_repo = vendor_repo

    def create_quotation(
        self,
        quotation_data: QuotationCreate,
        user_id: int
    ) -> Quotation:
        """Create a new quotation"""

        # Validate purchase request exists and is approved
        pr = self.purchase_request_repo.get_by_id(quotation_data.purchase_request_id)
        if not pr:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Purchase request not found"
            )

        if pr.status not in ["approved", "approved_level3"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Purchase request must be fully approved before creating quotations"
            )

        # Validate vendor exists
        vendor = self.vendor_repo.get_by_id(quotation_data.vendor_id)
        if not vendor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vendor not found"
            )

        # Generate quotation code
        quotation_code = generate_quotation_code(
            self.db,
            vendor.vendor_code,
            pr.request_code
        )

        # Create quotation
        quotation = Quotation(
            quotation_code=quotation_code,
            purchase_request_id=quotation_data.purchase_request_id,
            vendor_id=quotation_data.vendor_id,
            quotation_date=quotation_data.quotation_date,
            valid_until=quotation_data.valid_until,
            total_amount=quotation_data.total_amount,
            quotation_file_url=quotation_data.quotation_file_url,
            notes=quotation_data.notes,
            status=QuotationStatus.PENDING,
            created_by=user_id
        )

        # Add quotation items
        for item_data in quotation_data.items:
            item = QuotationItem(
                quotation=quotation,
                item_name=item_data.item_name,
                specification=item_data.specification,
                quantity=item_data.quantity,
                unit_price=item_data.unit_price,
                total_price=item_data.total_price,
                notes=item_data.notes
            )
            quotation.items.append(item)

        return self.quotation_repo.create(quotation)

    def get_quotation(self, quotation_id: int) -> Quotation:
        """Get quotation by ID"""
        quotation = self.quotation_repo.get_by_id(quotation_id)
        if not quotation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Quotation not found"
            )
        return quotation

    def get_quotations(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
        purchase_request_id: Optional[int] = None,
        vendor_id: Optional[int] = None
    ) -> tuple[list[Quotation], int]:
        """Get all quotations with filters"""
        return self.quotation_repo.get_all(
            skip=skip,
            limit=limit,
            status=status,
            purchase_request_id=purchase_request_id,
            vendor_id=vendor_id
        )

    def update_quotation(
        self,
        quotation_id: int,
        quotation_data: QuotationUpdate,
        user_id: int
    ) -> Quotation:
        """Update quotation"""
        quotation = self.get_quotation(quotation_id)

        # Check if quotation can be updated
        if quotation.status in [QuotationStatus.ACCEPTED, QuotationStatus.REJECTED]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot update quotation with status: {quotation.status}"
            )

        # Update fields
        if quotation_data.valid_until is not None:
            quotation.valid_until = quotation_data.valid_until
        if quotation_data.total_amount is not None:
            quotation.total_amount = quotation_data.total_amount
        if quotation_data.quotation_file_url is not None:
            quotation.quotation_file_url = quotation_data.quotation_file_url
        if quotation_data.notes is not None:
            quotation.notes = quotation_data.notes
        if quotation_data.status is not None:
            quotation.status = quotation_data.status

        return self.quotation_repo.update(quotation)

    def accept_quotation(
        self,
        quotation_id: int,
        user_id: int
    ) -> Quotation:
        """Accept a quotation"""
        quotation = self.get_quotation(quotation_id)

        # Check if quotation can be accepted
        if quotation.status != QuotationStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot accept quotation with status: {quotation.status}"
            )

        # Reject all other quotations for the same purchase request
        other_quotations, _ = self.quotation_repo.get_all(
            purchase_request_id=quotation.purchase_request_id,
            status=QuotationStatus.PENDING
        )

        for other in other_quotations:
            if other.id != quotation_id:
                self.quotation_repo.update_status(other.id, QuotationStatus.REJECTED)

        # Accept this quotation
        return self.quotation_repo.update_status(quotation_id, QuotationStatus.ACCEPTED)

    def reject_quotation(
        self,
        quotation_id: int,
        user_id: int
    ) -> Quotation:
        """Reject a quotation"""
        quotation = self.get_quotation(quotation_id)

        # Check if quotation can be rejected
        if quotation.status != QuotationStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot reject quotation with status: {quotation.status}"
            )

        return self.quotation_repo.update_status(quotation_id, QuotationStatus.REJECTED)

    def get_quotation_comparison(self, purchase_request_id: int) -> list[dict]:
        """Get quotation comparison for a purchase request"""
        # Validate purchase request exists
        pr = self.purchase_request_repo.get_by_id(purchase_request_id)
        if not pr:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Purchase request not found"
            )

        return self.quotation_repo.get_comparison(purchase_request_id)

    def delete_quotation(self, quotation_id: int, user_id: int) -> bool:
        """Delete quotation"""
        quotation = self.get_quotation(quotation_id)

        # Only allow deletion of pending quotations
        if quotation.status != QuotationStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot delete quotation with status: {quotation.status}"
            )

        return self.quotation_repo.delete(quotation_id)
