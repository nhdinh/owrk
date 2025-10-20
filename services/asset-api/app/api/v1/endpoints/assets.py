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
)
from app.services.asset_service import AssetService
from app.services.depreciation_service import DepreciationService

router = APIRouter()


@router.post("/", response_model=AssetResponse, status_code=status.HTTP_201_CREATED)
async def create_asset(
    asset_data: AssetCreate,
    current_user: dict = Depends(get_current_user)
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
    search: Optional[str] = Query(None, description="Search by code, name, manufacturer, model"),
    category_id: Optional[int] = Query(None, description="Filter by category"),
    status: Optional[AssetStatus] = Query(None, description="Filter by status"),
    asset_type: Optional[AssetType] = Query(None, description="Filter by asset type"),
    department_id: Optional[int] = Query(None, description="Filter by department"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: dict = Depends(get_current_user)
):
    """List assets with search and filters"""
    try:
        assets, total = await AssetService.search_assets(
            search=search,
            category_id=category_id,
            status=status,
            asset_type=asset_type,
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
async def get_asset(
    asset_id: int,
    current_user: dict = Depends(get_current_user)
):
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
    current_user: dict = Depends(get_current_user)
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
async def delete_asset(
    asset_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Delete asset (soft delete)"""
    try:
        await AssetService.delete_asset(asset_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/{asset_id}/assign", response_model=AssignmentResponse, status_code=status.HTTP_201_CREATED)
async def assign_asset(
    asset_id: int,
    assignment_data: AssignmentCreate,
    current_user: dict = Depends(get_current_user)
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
    current_user: dict = Depends(get_current_user)
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
    asset_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Get assignment history for asset"""
    try:
        history = await AssetService.get_asset_history(asset_id)
        return history
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/{asset_id}/depreciation", response_model=List[DepreciationRecordResponse])
async def get_asset_depreciation(
    asset_id: int,
    current_user: dict = Depends(get_current_user)
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
