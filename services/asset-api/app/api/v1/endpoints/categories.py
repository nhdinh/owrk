"""
Category API Endpoints
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status

from app.core.dependencies import get_current_user
from app.core.unit_of_work import UnitOfWork
from app.models.category import AssetCategory
from app.schemas.asset_schema import CategoryCreate, CategoryUpdate, CategoryResponse

router = APIRouter()


@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    category_data: CategoryCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create new category"""
    try:
        with UnitOfWork() as uow:
            # Check if code already exists
            existing = uow.categories.get_by_code(category_data.code)
            if existing:
                raise HTTPException(status_code=400, detail=f"Category code {category_data.code} already exists")

            # Validate parent if provided
            if category_data.parent_id:
                parent = uow.categories.get_by_id(category_data.parent_id)
                if not parent:
                    raise HTTPException(status_code=400, detail="Parent category not found")

            category = AssetCategory(**category_data.model_dump())
            category = uow.categories.create(category)
            uow.commit()

            # Refresh to get the latest data
            uow.session.refresh(category)

            # Return as dict to avoid relationship serialization issues
            return CategoryResponse(
                id=category.id,
                name=category.name,
                code=category.code,
                parent_id=category.parent_id,
                description=category.description,
                is_active=category.is_active,
                created_at=category.created_at,
                updated_at=category.updated_at
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/", response_model=List[CategoryResponse])
async def list_categories(
    active_only: bool = False,
    current_user: dict = Depends(get_current_user)
):
    """List all categories"""
    try:
        with UnitOfWork() as uow:
            if active_only:
                categories = uow.categories.get_active_categories()
            else:
                categories = uow.categories.get_all()
            return categories
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(
    category_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Get category by ID"""
    try:
        with UnitOfWork() as uow:
            category = uow.categories.get_by_id(category_id)
            if not category:
                raise HTTPException(status_code=404, detail="Category not found")
            return category
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.put("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: int,
    category_data: CategoryUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update category"""
    try:
        with UnitOfWork() as uow:
            category = uow.categories.get_by_id(category_id)
            if not category:
                raise HTTPException(status_code=404, detail="Category not found")

            # Update fields
            update_dict = category_data.model_dump(exclude_unset=True)
            for key, value in update_dict.items():
                setattr(category, key, value)

            category = uow.categories.update(category)
            uow.commit()

            # Refresh to get the latest data
            uow.session.refresh(category)

            # Return as dict to avoid relationship serialization issues
            return CategoryResponse(
                id=category.id,
                name=category.name,
                code=category.code,
                parent_id=category.parent_id,
                description=category.description,
                is_active=category.is_active,
                created_at=category.created_at,
                updated_at=category.updated_at
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Delete category"""
    try:
        with UnitOfWork() as uow:
            # Check if category has assets
            assets = uow.assets.get_assets_by_category(category_id)
            if assets:
                raise HTTPException(status_code=400, detail="Cannot delete category with assets")

            success = uow.categories.delete(category_id)
            if not success:
                raise HTTPException(status_code=404, detail="Category not found")

            uow.commit()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
