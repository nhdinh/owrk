"""
Trash Management Endpoints
Handles soft-delete, restore, and permanent delete operations
"""

from typing import Optional, List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, require_admin, get_client_ip, get_user_agent
from app.repositories.trash_repository import TrashRepository
from app.repositories.audit_log_repository import AuditLogRepository
from app.models.trash import TrashItem, TrashConfig
from app.models.audit_log import AuditLog
from app.schemas.trash_schema import (
    TrashItemCreate,
    TrashItemResponse,
    TrashItemsListResponse,
    RestoreRequest,
    PermanentDeleteRequest,
    TrashConfigCreate,
    TrashConfigUpdate,
    TrashConfigResponse,
    TrashStatsResponse,
)

router = APIRouter()


@router.get("/", response_model=TrashItemsListResponse)
async def list_trash_items(
    module_name: Optional[str] = Query(None, description="Filter by module"),
    resource_type: Optional[str] = Query(None, description="Filter by resource type"),
    deleted_by: Optional[int] = Query(None, description="Filter by user who deleted"),
    start_date: Optional[datetime] = Query(None, description="Filter by start date"),
    end_date: Optional[datetime] = Query(None, description="Filter by end date"),
    is_restorable: Optional[bool] = Query(None, description="Filter by restorable status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """
    List trash items with filters and pagination

    Requires admin privileges.
    """
    repo = TrashRepository(db)
    items, total = repo.get_trash_items(
        module_name=module_name,
        resource_type=resource_type,
        deleted_by=deleted_by,
        start_date=start_date,
        end_date=end_date,
        is_restorable=is_restorable,
        skip=skip,
        limit=limit,
    )

    # Get aggregated counts
    stats = repo.get_trash_stats()

    return TrashItemsListResponse(
        data=[TrashItemResponse.model_validate(item) for item in items],
        total=total,
        by_module=stats["by_module"],
        by_type=stats["by_type"],
    )


@router.get("/stats", response_model=TrashStatsResponse)
async def get_trash_stats(
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """
    Get trash statistics for dashboard

    Requires admin privileges.
    """
    repo = TrashRepository(db)
    stats = repo.get_trash_stats()

    return TrashStatsResponse(**stats)


@router.get("/{trash_id}", response_model=TrashItemResponse)
async def get_trash_item(
    trash_id: int,
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """
    Get a specific trash item by ID

    Requires admin privileges.
    """
    repo = TrashRepository(db)
    trash_item = repo.get_trash_by_id(trash_id)

    if not trash_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Trash item with ID {trash_id} not found",
        )

    return TrashItemResponse.model_validate(trash_item)


@router.post("/", response_model=TrashItemResponse, status_code=status.HTTP_201_CREATED)
async def create_trash_item(
    trash_data: TrashItemCreate,
    request: Request,
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """
    Soft delete an item by adding it to trash

    This endpoint is typically called by other services when deleting items.
    Requires admin privileges.
    """
    repo = TrashRepository(db)

    # Check if item already in trash
    existing = repo.get_trash_by_resource(
        trash_data.module_name,
        trash_data.resource_type,
        trash_data.resource_id,
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Item already in trash (ID: {existing.id})",
        )

    # Create trash item
    trash_item = TrashItem(**trash_data.model_dump())
    created_item = repo.create_trash_item(trash_item)

    # Create audit log
    audit_repo = AuditLogRepository(db)
    audit_log = AuditLog(
        user_id=current_user["id"],
        user_email=current_user.get("email"),
        action="SOFT_DELETE",
        module_name=trash_data.module_name,
        resource_type=trash_data.resource_type,
        resource_id=trash_data.resource_id,
        description=f"Soft deleted {trash_data.resource_type}: {trash_data.resource_name}",
        changes={"trash_id": created_item.id, "reason": trash_data.deleted_reason},
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request),
    )
    audit_repo.create(audit_log)

    return TrashItemResponse.model_validate(created_item)


@router.post("/{trash_id}/restore", response_model=TrashItemResponse)
async def restore_trash_item(
    trash_id: int,
    restore_request: RestoreRequest,
    request: Request,
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """
    Restore an item from trash

    This will mark the item as restored. The calling service is responsible
    for actually restoring the data in their database.

    Requires admin privileges.
    """
    repo = TrashRepository(db)

    # Get trash item
    trash_item = repo.get_trash_by_id(trash_id)
    if not trash_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Trash item with ID {trash_id} not found",
        )

    # Check if already restored
    if trash_item.restored_at:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Item already restored at {trash_item.restored_at}",
        )

    # Check if restorable
    if not trash_item.is_restorable:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This item is marked as non-restorable",
        )

    # Restore item
    restored_item = repo.restore_item(
        trash_id=trash_id,
        restored_by=current_user["id"],
        restored_by_email=current_user.get("email"),
    )

    # Create audit log
    audit_repo = AuditLogRepository(db)
    audit_log = AuditLog(
        user_id=current_user["id"],
        user_email=current_user.get("email"),
        action="RESTORE",
        module_name=trash_item.module_name,
        resource_type=trash_item.resource_type,
        resource_id=trash_item.resource_id,
        description=f"Restored {trash_item.resource_type}: {trash_item.resource_name}",
        changes={
            "trash_id": trash_id,
            "reason": restore_request.restore_reason,
            "restore_dependencies": restore_request.restore_dependencies,
        },
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request),
    )
    audit_repo.create(audit_log)

    return TrashItemResponse.model_validate(restored_item)


@router.delete("/{trash_id}", status_code=status.HTTP_204_NO_CONTENT)
async def permanent_delete_trash_item(
    trash_id: int,
    delete_request: PermanentDeleteRequest,
    request: Request,
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """
    Permanently delete an item from trash

    This action is irreversible. Requires confirmation string.
    Requires admin privileges.
    """
    # Validate confirmation
    if delete_request.confirmation != "PERMANENTLY_DELETE":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid confirmation. Must be 'PERMANENTLY_DELETE'",
        )

    repo = TrashRepository(db)

    # Get trash item for audit log
    trash_item = repo.get_trash_by_id(trash_id)
    if not trash_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Trash item with ID {trash_id} not found",
        )

    # Create audit log before deletion
    audit_repo = AuditLogRepository(db)
    audit_log = AuditLog(
        user_id=current_user["id"],
        user_email=current_user.get("email"),
        action="PERMANENT_DELETE",
        module_name=trash_item.module_name,
        resource_type=trash_item.resource_type,
        resource_id=trash_item.resource_id,
        description=f"Permanently deleted {trash_item.resource_type}: {trash_item.resource_name}",
        changes={
            "trash_id": trash_id,
            "reason": delete_request.reason,
            "resource_snapshot": trash_item.resource_data,
        },
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request),
    )
    audit_repo.create(audit_log)

    # Permanently delete
    success = repo.permanent_delete(trash_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete trash item",
        )

    return None


# Trash Config Endpoints
@router.get("/config/", response_model=List[TrashConfigResponse])
async def list_trash_configs(
    module_name: Optional[str] = Query(None, description="Filter by module"),
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """
    List trash configurations

    Requires admin privileges.
    """
    repo = TrashRepository(db)
    configs = repo.get_all_trash_configs(module_name=module_name)

    return [TrashConfigResponse.model_validate(config) for config in configs]


@router.get("/config/{module_name}/{resource_type}", response_model=TrashConfigResponse)
async def get_trash_config(
    module_name: str,
    resource_type: str,
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """
    Get trash configuration for a specific module/resource

    Requires admin privileges.
    """
    repo = TrashRepository(db)
    config = repo.get_trash_config(module_name, resource_type)

    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Trash config not found for {module_name}/{resource_type}",
        )

    return TrashConfigResponse.model_validate(config)


@router.post("/config/", response_model=TrashConfigResponse, status_code=status.HTTP_201_CREATED)
async def create_trash_config(
    config_data: TrashConfigCreate,
    request: Request,
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """
    Create trash configuration

    Requires admin privileges.
    """
    repo = TrashRepository(db)

    # Check if config already exists
    existing = repo.get_trash_config(config_data.module_name, config_data.resource_type)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Config already exists for {config_data.module_name}/{config_data.resource_type}",
        )

    # Create config
    config = TrashConfig(**config_data.model_dump())
    created_config = repo.create_trash_config(config)

    # Create audit log
    audit_repo = AuditLogRepository(db)
    audit_log = AuditLog(
        user_id=current_user["id"],
        user_email=current_user.get("email"),
        action="CREATE",
        module_name="admin",
        resource_type="trash_config",
        resource_id=str(created_config.id),
        description=f"Created trash config for {config_data.module_name}/{config_data.resource_type}",
        changes={"after": config_data.model_dump()},
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request),
    )
    audit_repo.create(audit_log)

    return TrashConfigResponse.model_validate(created_config)


@router.put("/config/{config_id}", response_model=TrashConfigResponse)
async def update_trash_config(
    config_id: int,
    config_update: TrashConfigUpdate,
    request: Request,
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """
    Update trash configuration

    Requires admin privileges.
    """
    repo = TrashRepository(db)

    # Get existing config for audit
    existing_config = db.query(TrashConfig).filter(TrashConfig.id == config_id).first()
    if not existing_config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Trash config with ID {config_id} not found",
        )

    # Prepare update data
    update_data = config_update.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update",
        )

    # Update config
    updated_config = repo.update_trash_config(config_id, update_data)

    # Create audit log
    audit_repo = AuditLogRepository(db)
    audit_log = AuditLog(
        user_id=current_user["id"],
        user_email=current_user.get("email"),
        action="UPDATE",
        module_name="admin",
        resource_type="trash_config",
        resource_id=str(config_id),
        description=f"Updated trash config for {existing_config.module_name}/{existing_config.resource_type}",
        changes={
            "before": TrashConfigResponse.model_validate(existing_config).model_dump(),
            "after": update_data,
        },
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request),
    )
    audit_repo.create(audit_log)

    return TrashConfigResponse.model_validate(updated_config)


@router.delete("/config/{config_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_trash_config(
    config_id: int,
    request: Request,
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """
    Delete trash configuration

    Requires admin privileges.
    """
    repo = TrashRepository(db)

    # Get config for audit log
    config = db.query(TrashConfig).filter(TrashConfig.id == config_id).first()
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Trash config with ID {config_id} not found",
        )

    # Create audit log
    audit_repo = AuditLogRepository(db)
    audit_log = AuditLog(
        user_id=current_user["id"],
        user_email=current_user.get("email"),
        action="DELETE",
        module_name="admin",
        resource_type="trash_config",
        resource_id=str(config_id),
        description=f"Deleted trash config for {config.module_name}/{config.resource_type}",
        changes={"before": TrashConfigResponse.model_validate(config).model_dump()},
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request),
    )
    audit_repo.create(audit_log)

    # Delete config
    success = repo.delete_trash_config(config_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete trash config",
        )

    return None


@router.post("/cleanup/scheduled", status_code=status.HTTP_200_OK)
async def cleanup_scheduled_items(
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """
    Run cleanup for items with permanent_delete_at <= now

    This endpoint is typically called by a scheduled task.
    Requires admin privileges.
    """
    repo = TrashRepository(db)
    deleted_count = repo.cleanup_scheduled_items()

    return {
        "success": True,
        "deleted_count": deleted_count,
        "message": f"Cleaned up {deleted_count} scheduled items",
    }


@router.post("/cleanup/{module_name}/{resource_type}", status_code=status.HTTP_200_OK)
async def cleanup_old_items(
    module_name: str,
    resource_type: str,
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """
    Run cleanup for old items based on trash config

    Requires admin privileges.
    """
    repo = TrashRepository(db)
    deleted_count = repo.cleanup_old_items(module_name, resource_type)

    return {
        "success": True,
        "deleted_count": deleted_count,
        "message": f"Cleaned up {deleted_count} old items for {module_name}/{resource_type}",
    }
