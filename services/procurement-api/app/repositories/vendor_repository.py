"""
Vendor Repository
Data access layer for vendor operations
"""

from typing import List, Optional
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.models.vendor import Vendor, VendorStatus
from app.utils.code_generator import generate_vendor_code


class VendorRepository:
    """Repository for vendor CRUD operations"""

    def __init__(self, db: Session):
        self.db = db

    def create(self, vendor_data: dict) -> Vendor:
        """
        Create a new vendor

        Args:
            vendor_data: Dictionary with vendor information

        Returns:
            Vendor: Created vendor object
        """
        # Generate vendor code
        vendor_code = generate_vendor_code(self.db)

        # Create vendor object
        vendor = Vendor(vendor_code=vendor_code, **vendor_data)

        self.db.add(vendor)
        self.db.flush()
        self.db.refresh(vendor)

        return vendor

    def get_by_id(self, vendor_id: int) -> Optional[Vendor]:
        """Get vendor by ID"""
        return self.db.query(Vendor).filter(Vendor.id == vendor_id).first()

    def get_by_code(self, vendor_code: str) -> Optional[Vendor]:
        """Get vendor by code"""
        return self.db.query(Vendor).filter(Vendor.vendor_code == vendor_code).first()

    def get_by_tax_code(self, tax_code: str) -> Optional[Vendor]:
        """Get vendor by tax code"""
        return self.db.query(Vendor).filter(Vendor.tax_code == tax_code).first()

    def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[VendorStatus] = None,
        search: Optional[str] = None,
        min_rating: Optional[Decimal] = None,
    ) -> List[Vendor]:
        """
        Get all vendors with optional filtering

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            status: Filter by vendor status
            search: Search in company name, vendor code, email
            min_rating: Minimum rating filter

        Returns:
            List[Vendor]: List of vendors
        """
        query = self.db.query(Vendor)

        # Apply filters
        if status:
            query = query.filter(Vendor.status == status)

        if min_rating is not None:
            query = query.filter(Vendor.rating >= min_rating)

        if search:
            search_filter = or_(
                Vendor.company_name.ilike(f"%{search}%"),
                Vendor.vendor_code.ilike(f"%{search}%"),
                Vendor.email.ilike(f"%{search}%"),
            )
            query = query.filter(search_filter)

        return query.offset(skip).limit(limit).all()

    def count(
        self,
        status: Optional[VendorStatus] = None,
        search: Optional[str] = None,
        min_rating: Optional[Decimal] = None,
    ) -> int:
        """
        Count vendors with optional filtering

        Args:
            status: Filter by vendor status
            search: Search in company name, vendor code, email
            min_rating: Minimum rating filter

        Returns:
            int: Count of vendors
        """
        query = self.db.query(Vendor)

        if status:
            query = query.filter(Vendor.status == status)

        if min_rating is not None:
            query = query.filter(Vendor.rating >= min_rating)

        if search:
            search_filter = or_(
                Vendor.company_name.ilike(f"%{search}%"),
                Vendor.vendor_code.ilike(f"%{search}%"),
                Vendor.email.ilike(f"%{search}%"),
            )
            query = query.filter(search_filter)

        return query.count()

    def update(self, vendor: Vendor, update_data: dict) -> Vendor:
        """
        Update vendor information

        Args:
            vendor: Vendor object to update
            update_data: Dictionary with fields to update

        Returns:
            Vendor: Updated vendor object
        """
        for key, value in update_data.items():
            if hasattr(vendor, key) and value is not None:
                setattr(vendor, key, value)

        self.db.flush()
        self.db.refresh(vendor)

        return vendor

    def delete(self, vendor: Vendor) -> bool:
        """
        Delete a vendor (soft delete by changing status to INACTIVE)

        Args:
            vendor: Vendor object to delete

        Returns:
            bool: True if successful
        """
        vendor.status = VendorStatus.INACTIVE
        self.db.flush()
        return True

    def update_status(
        self, vendor: Vendor, new_status: VendorStatus, reason: Optional[str] = None
    ) -> Vendor:
        """
        Update vendor status

        Args:
            vendor: Vendor object
            new_status: New status
            reason: Reason for status change (added to notes)

        Returns:
            Vendor: Updated vendor object
        """
        vendor.status = new_status

        # Append reason to notes if provided
        if reason:
            if vendor.notes:
                vendor.notes += f"\n\n[{new_status.value}] {reason}"
            else:
                vendor.notes = f"[{new_status.value}] {reason}"

        self.db.flush()
        self.db.refresh(vendor)

        return vendor

    def update_rating(self, vendor: Vendor, rating: Decimal) -> Vendor:
        """
        Update vendor rating

        Args:
            vendor: Vendor object
            rating: New rating (0-5)

        Returns:
            Vendor: Updated vendor object
        """
        vendor.rating = rating
        self.db.flush()
        self.db.refresh(vendor)

        return vendor

    def get_active_vendors(self) -> List[Vendor]:
        """Get all active vendors"""
        return self.db.query(Vendor).filter(Vendor.status == VendorStatus.ACTIVE).all()

    def get_top_rated_vendors(self, limit: int = 10) -> List[Vendor]:
        """
        Get top-rated active vendors

        Args:
            limit: Maximum number of vendors to return

        Returns:
            List[Vendor]: Top rated vendors
        """
        return (
            self.db.query(Vendor)
            .filter(Vendor.status == VendorStatus.ACTIVE)
            .order_by(Vendor.rating.desc())
            .limit(limit)
            .all()
        )

    def search_by_name(self, company_name: str) -> List[Vendor]:
        """
        Search vendors by company name

        Args:
            company_name: Company name to search

        Returns:
            List[Vendor]: Matching vendors
        """
        return (
            self.db.query(Vendor)
            .filter(Vendor.company_name.ilike(f"%{company_name}%"))
            .all()
        )

    def exists(self, vendor_id: int) -> bool:
        """Check if vendor exists"""
        return self.db.query(Vendor).filter(Vendor.id == vendor_id).first() is not None

    def is_tax_code_unique(
        self, tax_code: str, exclude_id: Optional[int] = None
    ) -> bool:
        """
        Check if tax code is unique

        Args:
            tax_code: Tax code to check
            exclude_id: Vendor ID to exclude from check (for updates)

        Returns:
            bool: True if unique
        """
        query = self.db.query(Vendor).filter(Vendor.tax_code == tax_code)

        if exclude_id:
            query = query.filter(Vendor.id != exclude_id)

        return query.first() is None
