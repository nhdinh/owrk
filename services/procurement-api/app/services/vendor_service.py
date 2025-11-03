"""
Vendor Service
Business logic layer for vendor operations
"""

import logging
from typing import List, Optional
from decimal import Decimal
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.vendor import Vendor, VendorStatus
from app.repositories.vendor_repository import VendorRepository
from app.schemas.vendor_schema import (
    VendorCreate,
    VendorUpdate,
    VendorResponse,
    VendorListResponse,
    VendorRatingUpdate,
    VendorStatusUpdate,
    VendorBlacklistRequest
)
from app.core.events import publish_event, EventTypes
from app.utils.validators import validate_email, validate_phone, validate_tax_code, validate_rating

logger = logging.getLogger(__name__)


class VendorService:
    """Service for vendor business logic"""

    def __init__(self, db: Session):
        self.db = db
        self.repository = VendorRepository(db)

    def create_vendor(self, vendor_data: VendorCreate, created_by: int) -> VendorResponse:
        """
        Create a new vendor

        Args:
            vendor_data: Vendor creation data
            created_by: User ID creating the vendor

        Returns:
            VendorResponse: Created vendor

        Raises:
            HTTPException: If validation fails or tax code already exists
        """
        # Validate email format
        if vendor_data.email:
            try:
                validate_email(vendor_data.email)
            except HTTPException as e:
                raise e

        # Validate phone format
        if vendor_data.phone:
            try:
                validate_phone(vendor_data.phone)
            except HTTPException as e:
                raise e

        # Validate tax code format
        if vendor_data.tax_code:
            try:
                validate_tax_code(vendor_data.tax_code)
            except HTTPException as e:
                raise e

            # Check if tax code already exists
            if not self.repository.is_tax_code_unique(vendor_data.tax_code):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Tax code {vendor_data.tax_code} already exists"
                )

        # Create vendor
        vendor_dict = vendor_data.model_dump(exclude_unset=True)
        vendor_dict['status'] = VendorStatus.ACTIVE
        vendor_dict['rating'] = Decimal("0.00")
        vendor_dict['created_by'] = created_by

        try:
            vendor = self.repository.create(vendor_dict)
            self.db.commit()

            # Publish event
            publish_event(EventTypes.VENDOR_CREATED, {
                "id": vendor.id,
                "vendor_code": vendor.vendor_code,
                "company_name": vendor.company_name,
                "status": vendor.status.value,
                "created_at": str(vendor.created_at)
            })

            logger.info(f"Vendor created: {vendor.vendor_code} by user {created_by}")

            return VendorResponse.model_validate(vendor)

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating vendor: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create vendor"
            )

    def get_vendor(self, vendor_id: int) -> VendorResponse:
        """
        Get vendor by ID

        Args:
            vendor_id: Vendor ID

        Returns:
            VendorResponse: Vendor details

        Raises:
            HTTPException: If vendor not found
        """
        vendor = self.repository.get_by_id(vendor_id)

        if not vendor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Vendor with ID {vendor_id} not found"
            )

        return VendorResponse.model_validate(vendor)

    def get_vendor_by_code(self, vendor_code: str) -> VendorResponse:
        """Get vendor by code"""
        vendor = self.repository.get_by_code(vendor_code)

        if not vendor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Vendor with code {vendor_code} not found"
            )

        return VendorResponse.model_validate(vendor)

    def list_vendors(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[VendorStatus] = None,
        search: Optional[str] = None,
        min_rating: Optional[Decimal] = None
    ) -> VendorListResponse:
        """
        List vendors with pagination and filters

        Args:
            skip: Number of records to skip
            limit: Maximum number of records
            status: Filter by status
            search: Search term
            min_rating: Minimum rating filter

        Returns:
            VendorListResponse: Paginated vendor list
        """
        vendors = self.repository.get_all(
            skip=skip,
            limit=limit,
            status=status,
            search=search,
            min_rating=min_rating
        )

        total = self.repository.count(
            status=status,
            search=search,
            min_rating=min_rating
        )

        vendor_responses = [VendorResponse.model_validate(v) for v in vendors]

        return VendorListResponse(
            vendors=vendor_responses,
            total=total,
            page=skip // limit + 1 if limit > 0 else 1,
            page_size=limit
        )

    def update_vendor(
        self,
        vendor_id: int,
        vendor_data: VendorUpdate,
        updated_by: int
    ) -> VendorResponse:
        """
        Update vendor information

        Args:
            vendor_id: Vendor ID
            vendor_data: Update data
            updated_by: User ID performing update

        Returns:
            VendorResponse: Updated vendor

        Raises:
            HTTPException: If vendor not found or validation fails
        """
        vendor = self.repository.get_by_id(vendor_id)

        if not vendor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Vendor with ID {vendor_id} not found"
            )

        # Validate email if provided
        if vendor_data.email:
            try:
                validate_email(vendor_data.email)
            except HTTPException as e:
                raise e

        # Validate phone if provided
        if vendor_data.phone:
            try:
                validate_phone(vendor_data.phone)
            except HTTPException as e:
                raise e

        # Validate tax code if provided
        if vendor_data.tax_code:
            try:
                validate_tax_code(vendor_data.tax_code)
            except HTTPException as e:
                raise e

            # Check uniqueness
            if not self.repository.is_tax_code_unique(vendor_data.tax_code, exclude_id=vendor_id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Tax code {vendor_data.tax_code} already exists"
                )

        try:
            update_dict = vendor_data.model_dump(exclude_unset=True)
            vendor = self.repository.update(vendor, update_dict)
            self.db.commit()

            # Publish event
            publish_event(EventTypes.VENDOR_UPDATED, {
                "id": vendor.id,
                "vendor_code": vendor.vendor_code,
                "company_name": vendor.company_name,
                "updated_at": str(vendor.updated_at)
            })

            logger.info(f"Vendor updated: {vendor.vendor_code} by user {updated_by}")

            return VendorResponse.model_validate(vendor)

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating vendor: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update vendor"
            )

    def delete_vendor(self, vendor_id: int, deleted_by: int) -> dict:
        """
        Delete vendor (soft delete - set to INACTIVE)

        Args:
            vendor_id: Vendor ID
            deleted_by: User ID performing deletion

        Returns:
            dict: Success message

        Raises:
            HTTPException: If vendor not found
        """
        vendor = self.repository.get_by_id(vendor_id)

        if not vendor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Vendor with ID {vendor_id} not found"
            )

        try:
            self.repository.delete(vendor)
            self.db.commit()

            # Publish event
            publish_event(EventTypes.VENDOR_DELETED, {
                "id": vendor.id,
                "vendor_code": vendor.vendor_code,
                "deleted_at": str(vendor.updated_at)
            })

            logger.info(f"Vendor deleted: {vendor.vendor_code} by user {deleted_by}")

            return {"message": f"Vendor {vendor.vendor_code} deleted successfully"}

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting vendor: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete vendor"
            )

    def activate_vendor(self, vendor_id: int, activated_by: int) -> VendorResponse:
        """
        Activate a vendor

        Args:
            vendor_id: Vendor ID
            activated_by: User ID performing activation

        Returns:
            VendorResponse: Updated vendor

        Raises:
            HTTPException: If vendor not found
        """
        vendor = self.repository.get_by_id(vendor_id)

        if not vendor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Vendor with ID {vendor_id} not found"
            )

        if vendor.status == VendorStatus.BLACKLISTED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot activate a blacklisted vendor"
            )

        try:
            vendor = self.repository.update_status(
                vendor,
                VendorStatus.ACTIVE,
                f"Activated by user {activated_by}"
            )
            self.db.commit()

            # Publish event
            publish_event(EventTypes.VENDOR_ACTIVATED, {
                "id": vendor.id,
                "vendor_code": vendor.vendor_code,
                "status": vendor.status.value,
                "updated_at": str(vendor.updated_at)
            })

            logger.info(f"Vendor activated: {vendor.vendor_code} by user {activated_by}")

            return VendorResponse.model_validate(vendor)

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error activating vendor: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to activate vendor"
            )

    def deactivate_vendor(self, vendor_id: int, deactivated_by: int) -> VendorResponse:
        """Deactivate a vendor"""
        vendor = self.repository.get_by_id(vendor_id)

        if not vendor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Vendor with ID {vendor_id} not found"
            )

        try:
            vendor = self.repository.update_status(
                vendor,
                VendorStatus.INACTIVE,
                f"Deactivated by user {deactivated_by}"
            )
            self.db.commit()

            # Publish event
            publish_event(EventTypes.VENDOR_DEACTIVATED, {
                "id": vendor.id,
                "vendor_code": vendor.vendor_code,
                "status": vendor.status.value,
                "updated_at": str(vendor.updated_at)
            })

            logger.info(f"Vendor deactivated: {vendor.vendor_code} by user {deactivated_by}")

            return VendorResponse.model_validate(vendor)

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deactivating vendor: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to deactivate vendor"
            )

    def blacklist_vendor(
        self,
        vendor_id: int,
        blacklist_data: VendorBlacklistRequest,
        blacklisted_by: int
    ) -> VendorResponse:
        """
        Blacklist a vendor

        Args:
            vendor_id: Vendor ID
            blacklist_data: Blacklist request with reason
            blacklisted_by: User ID performing blacklist

        Returns:
            VendorResponse: Updated vendor

        Raises:
            HTTPException: If vendor not found
        """
        vendor = self.repository.get_by_id(vendor_id)

        if not vendor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Vendor with ID {vendor_id} not found"
            )

        try:
            vendor = self.repository.update_status(
                vendor,
                VendorStatus.BLACKLISTED,
                f"BLACKLISTED by user {blacklisted_by}: {blacklist_data.reason}"
            )
            self.db.commit()

            # Publish event
            publish_event(EventTypes.VENDOR_BLACKLISTED, {
                "id": vendor.id,
                "vendor_code": vendor.vendor_code,
                "status": vendor.status.value,
                "reason": blacklist_data.reason,
                "updated_at": str(vendor.updated_at)
            })

            logger.warning(f"Vendor blacklisted: {vendor.vendor_code} by user {blacklisted_by}")

            return VendorResponse.model_validate(vendor)

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error blacklisting vendor: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to blacklist vendor"
            )

    def update_rating(
        self,
        vendor_id: int,
        rating_data: VendorRatingUpdate,
        updated_by: int
    ) -> VendorResponse:
        """Update vendor rating"""
        vendor = self.repository.get_by_id(vendor_id)

        if not vendor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Vendor with ID {vendor_id} not found"
            )

        # Validate rating
        try:
            validate_rating(rating_data.rating)
        except HTTPException as e:
            raise e

        try:
            vendor = self.repository.update_rating(vendor, rating_data.rating)
            self.db.commit()

            logger.info(f"Vendor rating updated: {vendor.vendor_code} to {rating_data.rating} by user {updated_by}")

            return VendorResponse.model_validate(vendor)

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating vendor rating: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update vendor rating"
            )

    def get_active_vendors(self) -> List[VendorResponse]:
        """Get all active vendors"""
        vendors = self.repository.get_active_vendors()
        return [VendorResponse.model_validate(v) for v in vendors]

    def get_top_rated_vendors(self, limit: int = 10) -> List[VendorResponse]:
        """Get top-rated vendors"""
        vendors = self.repository.get_top_rated_vendors(limit)
        return [VendorResponse.model_validate(v) for v in vendors]
