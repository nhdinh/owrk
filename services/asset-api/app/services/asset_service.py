"""
Asset Service - Business Logic
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import date

from app.core.unit_of_work import UnitOfWork
from app.core.security import generate_qr_code
from app.models.asset import Asset, AssetStatus, AssetType
from app.models.category import AssetCategory
from app.models.assignment import AssetAssignment, AssignmentStatus
from app.schemas.asset_schema import (
    AssetCreate,
    AssetUpdate,
    AssignmentCreate,
    AssignmentReturn,
)

logger = logging.getLogger(__name__)


class AssetService:
    """Service for asset operations"""

    @staticmethod
    async def create_asset(asset_data: AssetCreate) -> Asset:
        """
        Create new asset

        Args:
            asset_data: Asset creation data

        Returns:
            Created asset

        Raises:
            ValueError: If validation fails
        """
        with UnitOfWork() as uow:
            # Check if asset code already exists
            existing = uow.assets.get_by_code(asset_data.asset_code)
            if existing:
                raise ValueError(f"Asset code {asset_data.asset_code} already exists")

            # Validate category exists
            category = uow.categories.get_by_id(asset_data.category_id)
            if not category:
                raise ValueError(f"Category {asset_data.category_id} not found")

            # Create asset
            asset = Asset(**asset_data.model_dump())

            # Generate QR code
            asset.qr_code = generate_qr_code(asset_data.asset_code)

            # Calculate warranty end date if warranty_months provided
            if asset_data.warranty_months and asset_data.warranty_start_date:
                from dateutil.relativedelta import relativedelta

                asset.warranty_end_date = (
                    asset_data.warranty_start_date
                    + relativedelta(months=asset_data.warranty_months)
                )

            asset = uow.assets.create(asset)
            uow.commit()

            logger.info(f"Asset created: {asset.asset_code}")
            return asset

    @staticmethod
    async def update_asset(asset_id: int, asset_data: AssetUpdate) -> Asset:
        """
        Update asset

        Args:
            asset_id: Asset ID
            asset_data: Update data

        Returns:
            Updated asset

        Raises:
            ValueError: If asset not found
        """
        with UnitOfWork() as uow:
            asset = uow.assets.get_by_id(asset_id)
            if not asset or asset.deleted_at:
                raise ValueError("Asset not found")

            # Update fields
            update_dict = asset_data.model_dump(exclude_unset=True)
            for key, value in update_dict.items():
                setattr(asset, key, value)

            asset = uow.assets.update(asset)
            uow.commit()

            logger.info(f"Asset updated: {asset.asset_code}")
            return asset

    @staticmethod
    async def get_asset(asset_id: int) -> Asset:
        """Get asset by ID"""
        with UnitOfWork() as uow:
            asset = uow.assets.get_by_id(asset_id)
            if not asset or asset.deleted_at:
                raise ValueError("Asset not found")
            return asset

    @staticmethod
    async def delete_asset(asset_id: int) -> bool:
        """
        Soft delete asset

        Args:
            asset_id: Asset ID

        Returns:
            True if successful

        Raises:
            ValueError: If asset not found or has active assignments
        """
        with UnitOfWork() as uow:
            # Check for active assignments
            active_assignment = uow.assignments.get_active_assignment(asset_id)
            if active_assignment:
                raise ValueError("Cannot delete asset with active assignment")

            success = uow.assets.soft_delete(asset_id)
            if not success:
                raise ValueError("Asset not found")

            uow.commit()
            logger.info(f"Asset deleted: {asset_id}")
            return True

    @staticmethod
    async def search_assets(
        search: Optional[str] = None,
        category_id: Optional[int] = None,
        status: Optional[AssetStatus] = None,
        asset_type: Optional[AssetType] = None,
        department_id: Optional[int] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[List[Asset], int]:
        """Search and filter assets"""
        with UnitOfWork() as uow:
            skip = (page - 1) * page_size
            return uow.assets.search_assets(
                search=search,
                category_id=category_id,
                status=status,
                asset_type=asset_type,
                department_id=department_id,
                skip=skip,
                limit=page_size,
            )

    @staticmethod
    async def assign_asset(assignment_data: AssignmentCreate) -> AssetAssignment:
        """
        Assign asset to user

        Args:
            assignment_data: Assignment data

        Returns:
            Created assignment

        Raises:
            ValueError: If validation fails
        """
        with UnitOfWork() as uow:
            asset = uow.assets.get_by_id(assignment_data.asset_id)
            if not asset or asset.deleted_at:
                raise ValueError("Asset not found")

            # Check if asset is available
            if asset.status not in [AssetStatus.NEW, AssetStatus.AVAILABLE]:
                raise ValueError(
                    f"Asset is not available for assignment (status: {asset.status})"
                )

            # Check for existing active assignment
            active_assignment = uow.assignments.get_active_assignment(
                assignment_data.asset_id
            )
            if active_assignment:
                raise ValueError("Asset already has an active assignment")

            # Create assignment
            assignment = AssetAssignment(**assignment_data.model_dump())
            assignment = uow.assignments.create(assignment)

            # Update asset
            uow.assets.assign_to_user(
                assignment_data.asset_id,
                assignment_data.user_id,
                assignment_data.department_id,
            )

            uow.commit()
            logger.info(
                f"Asset {asset.asset_code} assigned to user {assignment_data.user_id}"
            )
            return assignment

    @staticmethod
    async def return_asset(
        asset_id: int, return_data: AssignmentReturn
    ) -> AssetAssignment:
        """
        Return asset from user

        Args:
            asset_id: Asset ID
            return_data: Return data

        Returns:
            Updated assignment

        Raises:
            ValueError: If validation fails
        """
        with UnitOfWork() as uow:
            # Get active assignment
            assignment = uow.assignments.get_active_assignment(asset_id)
            if not assignment:
                raise ValueError("No active assignment found for this asset")

            # Update assignment
            assignment.returned_date = return_data.returned_date
            assignment.returned_by = return_data.returned_by
            assignment.return_condition = return_data.return_condition
            assignment.return_notes = return_data.return_notes
            assignment.status = AssignmentStatus.RETURNED

            assignment = uow.assignments.update(assignment)

            # Update asset
            uow.assets.unassign_from_user(asset_id)

            # Update asset status based on return condition
            asset = uow.assets.get_by_id(asset_id)
            if return_data.return_condition == "BROKEN":
                asset.status = AssetStatus.BROKEN
            elif return_data.return_condition == "DAMAGED":
                asset.status = AssetStatus.MAINTENANCE
            else:
                asset.status = AssetStatus.AVAILABLE

            uow.assets.update(asset)

            uow.commit()
            logger.info(f"Asset {asset.asset_code} returned")
            return assignment

    @staticmethod
    async def get_asset_history(asset_id: int) -> List[AssetAssignment]:
        """Get assignment history for asset"""
        with UnitOfWork() as uow:
            return uow.assignments.get_asset_history(asset_id)

    @staticmethod
    async def get_user_assignments(user_id: int) -> List[AssetAssignment]:
        """Get assignments for user"""
        with UnitOfWork() as uow:
            return uow.assignments.get_user_assignments(user_id)

    @staticmethod
    async def get_statistics() -> Dict[str, Any]:
        """Get asset statistics"""
        with UnitOfWork() as uow:
            return uow.assets.get_statistics()
