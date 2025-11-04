"""
Asset API Endpoints
"""

from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.core.dependencies import get_current_user, Pagination
from app.models.asset import AssetStatus, AssetType
from app.schemas.asset_schema import (
    AssetCreate,
    AssetUpdate,
    AssetResponse,
    AssetListResponse,
    AssignmentCreate,
    AssignmentReturn,
    AssignmentResponse,
    DepreciationRecordResponse,
    MaintenanceCreate,
    MaintenanceUpdate,
    MaintenanceResponse,
)
from app.services.asset_service import AssetService
from app.services.depreciation_service import DepreciationService
from app.api.v1.endpoints import categories

router = APIRouter()

# Include categories as a sub-router to ensure /categories comes before /{asset_id}
router.include_router(categories.router, prefix="/categories", tags=["categories"])


@router.post("/", response_model=AssetResponse, status_code=status.HTTP_201_CREATED)
async def create_asset(
    asset_data: AssetCreate, current_user: dict = Depends(get_current_user)
):
    """Create new asset"""
    try:
        # Set created_by from current user
        asset_data.created_by = current_user["sub"]
        asset = await AssetService.create_asset(asset_data)
        return asset
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/", response_model=AssetListResponse)
async def list_assets(
    search: Optional[str] = Query(
        None, description="Search by code, name, manufacturer, model"
    ),
    category_id: Optional[int] = Query(None, description="Filter by category"),
    status: Optional[str] = Query(None, description="Filter by status"),
    asset_type: Optional[str] = Query(None, description="Filter by asset type"),
    department_id: Optional[int] = Query(None, description="Filter by department"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: dict = Depends(get_current_user),
):
    """List assets with search and filters"""
    try:
        # Convert empty strings to None and parse enums
        parsed_status = None
        if status and status.strip():
            try:
                parsed_status = AssetStatus(status)
            except ValueError:
                raise HTTPException(
                    status_code=400, detail=f"Invalid status value: {status}"
                )

        parsed_asset_type = None
        if asset_type and asset_type.strip():
            try:
                parsed_asset_type = AssetType(asset_type)
            except ValueError:
                raise HTTPException(
                    status_code=400, detail=f"Invalid asset_type value: {asset_type}"
                )

        assets, total = await AssetService.search_assets(
            search=search,
            category_id=category_id,
            status=parsed_status,
            asset_type=parsed_asset_type,
            department_id=department_id,
            page=page,
            page_size=page_size,
        )
        return AssetListResponse(
            total=total,
            page=page,
            page_size=page_size,
            assets=assets,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/{asset_id}", response_model=AssetResponse)
async def get_asset(asset_id: int, current_user: dict = Depends(get_current_user)):
    """Get asset by ID"""
    try:
        asset = await AssetService.get_asset(asset_id)
        return asset
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.put("/{asset_id}", response_model=AssetResponse)
async def update_asset(
    asset_id: int,
    asset_data: AssetUpdate,
    current_user: dict = Depends(get_current_user),
):
    """Update asset"""
    try:
        asset = await AssetService.update_asset(asset_id, asset_data)
        return asset
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.delete("/{asset_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_asset(asset_id: int, current_user: dict = Depends(get_current_user)):
    """Delete asset (soft delete)"""
    try:
        await AssetService.delete_asset(asset_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/assignments/", response_model=List[AssignmentResponse])
async def list_assignments(
    status: Optional[str] = Query(
        None, description="Filter by status (active/returned)"
    ),
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    current_user: dict = Depends(get_current_user),
):
    """List all assignments with optional filters"""
    try:
        from app.core.unit_of_work import UnitOfWork

        with UnitOfWork() as uow:
            if user_id:
                if status and status.lower() == "active":
                    assignments = uow.assignments.get_active_user_assignments(user_id)
                else:
                    assignments = uow.assignments.get_user_assignments(user_id)
            else:
                # Get all assignments
                if status and status.lower() == "active":
                    from app.models.assignment import AssignmentStatus

                    assignments = (
                        uow.session.query(uow.assignments.model)
                        .filter(uow.assignments.model.status == AssignmentStatus.ACTIVE)
                        .order_by(uow.assignments.model.assigned_date.desc())
                        .all()
                    )
                else:
                    assignments = uow.assignments.get_all()

            return assignments
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post(
    "/{asset_id}/assign",
    response_model=AssignmentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def assign_asset(
    asset_id: int,
    assignment_data: AssignmentCreate,
    current_user: dict = Depends(get_current_user),
):
    """Assign asset to user"""
    try:
        # Ensure asset_id matches
        assignment_data.asset_id = asset_id
        assignment_data.assigned_by = current_user["sub"]

        assignment = await AssetService.assign_asset(assignment_data)
        return assignment
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/{asset_id}/return", response_model=AssignmentResponse)
async def return_asset(
    asset_id: int,
    return_data: AssignmentReturn,
    current_user: dict = Depends(get_current_user),
):
    """Return asset from user"""
    try:
        return_data.returned_by = current_user["sub"]
        assignment = await AssetService.return_asset(asset_id, return_data)
        return assignment
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/{asset_id}/history", response_model=List[AssignmentResponse])
async def get_asset_history(
    asset_id: int, current_user: dict = Depends(get_current_user)
):
    """Get assignment history for asset"""
    try:
        history = await AssetService.get_asset_history(asset_id)
        return history
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/{asset_id}/depreciation", response_model=List[DepreciationRecordResponse])
async def get_asset_depreciation(
    asset_id: int, current_user: dict = Depends(get_current_user)
):
    """Get depreciation history for asset"""
    try:
        records = await DepreciationService.get_asset_depreciation_history(asset_id)
        return records
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/statistics/summary")
async def get_statistics(current_user: dict = Depends(get_current_user)):
    """Get asset statistics"""
    try:
        stats = await AssetService.get_statistics()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/{asset_id}/qrcode")
async def get_asset_qrcode(
    asset_id: int, current_user: dict = Depends(get_current_user)
):
    """Get QR code for asset"""
    try:
        from app.core.security import generate_qr_code

        asset = await AssetService.get_asset(asset_id)
        if not asset.qr_code:
            # Generate QR code if not exists
            qr_code = generate_qr_code(asset.asset_code)
            return {"qr_code": qr_code, "asset_code": asset.asset_code}
        return {"qr_code": asset.qr_code, "asset_code": asset.asset_code}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


# ==================== MAINTENANCE ENDPOINTS ====================


@router.get("/maintenance/", response_model=List[MaintenanceResponse])
async def list_maintenance(
    status: Optional[str] = Query(None, description="Filter by status"),
    asset_id: Optional[int] = Query(None, description="Filter by asset ID"),
    current_user: dict = Depends(get_current_user),
):
    """List all maintenance records with optional filters"""
    try:
        from app.core.unit_of_work import UnitOfWork
        from app.models.asset import Asset

        with UnitOfWork() as uow:
            if asset_id and status:
                records = uow.maintenance.get_by_asset_and_status(asset_id, status)
            elif asset_id:
                records = uow.maintenance.get_by_asset(asset_id)
            elif status:
                records = uow.maintenance.get_by_status(status)
            else:
                # Get all with asset details
                records_with_details = uow.maintenance.get_all_with_details()
                return records_with_details

            # Enrich with asset details
            result = []
            for record in records:
                asset = uow.assets.get_by_id(record.asset_id)
                record_dict = record.__dict__.copy()
                if asset:
                    record_dict["asset_code"] = asset.asset_code
                    record_dict["asset_name"] = asset.name
                result.append(record_dict)

            return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/maintenance/{maintenance_id}", response_model=MaintenanceResponse)
async def get_maintenance(
    maintenance_id: int, current_user: dict = Depends(get_current_user)
):
    """Get a specific maintenance record"""
    try:
        from app.core.unit_of_work import UnitOfWork

        with UnitOfWork() as uow:
            record = uow.maintenance.get_by_id(maintenance_id)
            if not record:
                raise HTTPException(
                    status_code=404, detail="Maintenance record not found"
                )

            # Enrich with asset details
            asset = uow.assets.get_by_id(record.asset_id)
            record_dict = record.__dict__.copy()
            if asset:
                record_dict["asset_code"] = asset.asset_code
                record_dict["asset_name"] = asset.name

            return record_dict
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post(
    "/maintenance/",
    response_model=MaintenanceResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_maintenance(
    data: MaintenanceCreate, current_user: dict = Depends(get_current_user)
):
    """Create a new maintenance record"""
    try:
        from app.core.unit_of_work import UnitOfWork
        from app.models.maintenance import MaintenanceRecord

        with UnitOfWork() as uow:
            # Verify asset exists
            asset = uow.assets.get_by_id(data.asset_id)
            if not asset:
                raise HTTPException(status_code=404, detail="Asset not found")

            # Create maintenance record
            maintenance_data = data.model_dump()
            maintenance_data["status"] = "pending"  # Default status

            record = MaintenanceRecord(**maintenance_data)
            created_record = uow.maintenance.create(record)
            uow.commit()

            # Enrich with asset details
            record_dict = created_record.__dict__.copy()
            record_dict["asset_code"] = asset.asset_code
            record_dict["asset_name"] = asset.name

            return record_dict
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.put("/maintenance/{maintenance_id}", response_model=MaintenanceResponse)
async def update_maintenance(
    maintenance_id: int,
    data: MaintenanceUpdate,
    current_user: dict = Depends(get_current_user),
):
    """Update a maintenance record"""
    try:
        from app.core.unit_of_work import UnitOfWork

        with UnitOfWork() as uow:
            record = uow.maintenance.get_by_id(maintenance_id)
            if not record:
                raise HTTPException(
                    status_code=404, detail="Maintenance record not found"
                )

            # Update fields
            update_data = data.model_dump(exclude_unset=True)
            updated_record = uow.maintenance.update(maintenance_id, update_data)
            uow.commit()

            # Enrich with asset details
            asset = uow.assets.get_by_id(updated_record.asset_id)
            record_dict = updated_record.__dict__.copy()
            if asset:
                record_dict["asset_code"] = asset.asset_code
                record_dict["asset_name"] = asset.name

            return record_dict
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.delete("/maintenance/{maintenance_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_maintenance(
    maintenance_id: int, current_user: dict = Depends(get_current_user)
):
    """Delete a maintenance record"""
    try:
        from app.core.unit_of_work import UnitOfWork

        with UnitOfWork() as uow:
            record = uow.maintenance.get_by_id(maintenance_id)
            if not record:
                raise HTTPException(
                    status_code=404, detail="Maintenance record not found"
                )

            uow.maintenance.delete(maintenance_id)
            uow.commit()

            return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
