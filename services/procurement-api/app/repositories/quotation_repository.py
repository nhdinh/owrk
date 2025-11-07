"""
Quotation Repository
Handles database operations for quotations
"""

from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import datetime

from app.models.quotation import Quotation, QuotationItem, QuotationStatus
from app.models.vendor import Vendor


class QuotationRepository:
    """Repository for Quotation database operations"""

    def __init__(self, db: Session):
        self.db = db

    def create(self, quotation: Quotation) -> Quotation:
        """Create a new quotation"""
        self.db.add(quotation)
        self.db.commit()
        self.db.refresh(quotation)
        return quotation

    def get_by_id(self, quotation_id: int) -> Optional[Quotation]:
        """Get quotation by ID"""
        return (
            self.db.query(Quotation)
            .filter(Quotation.id == quotation_id)
            .first()
        )

    def get_by_code(self, quotation_code: str) -> Optional[Quotation]:
        """Get quotation by code"""
        return (
            self.db.query(Quotation)
            .filter(Quotation.quotation_code == quotation_code)
            .first()
        )

    def get_by_purchase_request(
        self,
        purchase_request_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> list[Quotation]:
        """Get quotations by purchase request ID"""
        return (
            self.db.query(Quotation)
            .filter(Quotation.purchase_request_id == purchase_request_id)
            .order_by(Quotation.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_vendor(
        self,
        vendor_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> list[Quotation]:
        """Get quotations by vendor ID"""
        return (
            self.db.query(Quotation)
            .filter(Quotation.vendor_id == vendor_id)
            .order_by(Quotation.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
        purchase_request_id: Optional[int] = None,
        vendor_id: Optional[int] = None
    ) -> tuple[list[Quotation], int]:
        """Get all quotations with filters"""
        query = self.db.query(Quotation)

        # Apply filters
        if status:
            query = query.filter(Quotation.status == status)
        if purchase_request_id:
            query = query.filter(Quotation.purchase_request_id == purchase_request_id)
        if vendor_id:
            query = query.filter(Quotation.vendor_id == vendor_id)

        # Get total count
        total = query.count()

        # Get paginated results
        quotations = (
            query.order_by(Quotation.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

        return quotations, total

    def update(self, quotation: Quotation) -> Quotation:
        """Update quotation"""
        quotation.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(quotation)
        return quotation

    def update_status(self, quotation_id: int, status: QuotationStatus) -> Optional[Quotation]:
        """Update quotation status"""
        quotation = self.get_by_id(quotation_id)
        if quotation:
            quotation.status = status
            quotation.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(quotation)
        return quotation

    def delete(self, quotation_id: int) -> bool:
        """Delete quotation"""
        quotation = self.get_by_id(quotation_id)
        if quotation:
            self.db.delete(quotation)
            self.db.commit()
            return True
        return False

    def count_by_purchase_request(self, purchase_request_id: int) -> int:
        """Count quotations for a purchase request"""
        return (
            self.db.query(Quotation)
            .filter(Quotation.purchase_request_id == purchase_request_id)
            .count()
        )

    def get_comparison(self, purchase_request_id: int) -> list[dict]:
        """Get quotation comparison for a purchase request"""
        quotations = (
            self.db.query(Quotation, Vendor)
            .join(Vendor, Quotation.vendor_id == Vendor.id)
            .filter(Quotation.purchase_request_id == purchase_request_id)
            .filter(Quotation.status.in_([QuotationStatus.PENDING, QuotationStatus.ACCEPTED]))
            .all()
        )

        result = []
        for quotation, vendor in quotations:
            result.append({
                "quotation": quotation,
                "vendor": vendor
            })

        return result
