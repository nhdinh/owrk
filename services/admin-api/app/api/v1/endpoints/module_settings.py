"""
Module Settings API Endpoints
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_admin, get_client_ip, get_user_agent
from app.repositories.module_setting_repository import ModuleSettingRepository
from app.repositories.audit_log_repository import AuditLogRepository
from app.models.module_setting import ModuleSetting
from app.models.audit_log import AuditLog
from app.schemas.module_setting_schema import (
    ModuleSettingCreate,
    ModuleSettingUpdate,
    ModuleSettingResponse,
    ModuleSettingsListResponse,
)

router = APIRouter(prefix="/module-settings", tags=["Module Settings"])


@router.get("/", response_model=ModuleSettingsListResponse)
async def list_all_settings(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    search: Optional[str] = Query(None),
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """List all module settings across all modules (admin only)"""
    repo = ModuleSettingRepository(db)
    settings, total = repo.get_all_settings(skip=skip, limit=limit, search=search)

    return ModuleSettingsListResponse(
        data=[ModuleSettingResponse.model_validate(s) for s in settings], total=total
    )


@router.get("/module/{module_name}", response_model=ModuleSettingsListResponse)
async def list_module_settings(
    module_name: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    category: Optional[str] = Query(None),
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """List settings for a specific module"""
    repo = ModuleSettingRepository(db)
    settings, total = repo.get_module_settings(
        module_name=module_name, skip=skip, limit=limit, category=category
    )

    return ModuleSettingsListResponse(
        data=[ModuleSettingResponse.model_validate(s) for s in settings], total=total
    )


@router.get("/{setting_id}", response_model=ModuleSettingResponse)
async def get_setting(
    setting_id: int,
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Get a specific module setting by ID"""
    repo = ModuleSettingRepository(db)
    setting = repo.get_by_id(setting_id)

    if not setting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Setting not found"
        )

    return ModuleSettingResponse.model_validate(setting)


@router.post("/", response_model=ModuleSettingResponse, status_code=status.HTTP_201_CREATED)
async def create_setting(
    setting_data: ModuleSettingCreate,
    request: Request,
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Create a new module setting"""
    repo = ModuleSettingRepository(db)

    # Check if setting already exists
    existing = repo.get_by_key(setting_data.module_name, setting_data.setting_key)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Setting {setting_data.setting_key} already exists for module {setting_data.module_name}",
        )

    # Create setting
    setting = ModuleSetting(
        **setting_data.model_dump(),
        updated_by=current_user["id"],
    )
    created_setting = repo.create(setting)

    # Create audit log
    audit_repo = AuditLogRepository(db)
    audit_log = AuditLog(
        user_id=current_user["id"],
        user_email=current_user.get("email"),
        action="CREATE",
        module_name="admin",
        resource_type="module_setting",
        resource_id=str(created_setting.id),
        description=f"Created setting {setting_data.setting_key} for module {setting_data.module_name}",
        changes={"after": setting_data.model_dump()},
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request),
    )
    audit_repo.create(audit_log)

    return ModuleSettingResponse.model_validate(created_setting)


@router.put("/{setting_id}", response_model=ModuleSettingResponse)
async def update_setting(
    setting_id: int,
    setting_data: ModuleSettingUpdate,
    request: Request,
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Update a module setting"""
    repo = ModuleSettingRepository(db)
    setting = repo.get_by_id(setting_id)

    if not setting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Setting not found"
        )

    if not setting.is_editable:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This setting is not editable",
        )

    # Store old values for audit
    old_values = {
        "setting_value": setting.setting_value,
        "display_name": setting.display_name,
        "description": setting.description,
    }

    # Update setting
    update_data = setting_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(setting, key, value)

    setting.updated_by = current_user["id"]
    updated_setting = repo.update(setting)

    # Create audit log
    audit_repo = AuditLogRepository(db)
    audit_log = AuditLog(
        user_id=current_user["id"],
        user_email=current_user.get("email"),
        action="UPDATE",
        module_name="admin",
        resource_type="module_setting",
        resource_id=str(setting_id),
        description=f"Updated setting {setting.setting_key} for module {setting.module_name}",
        changes={"before": old_values, "after": update_data},
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request),
    )
    audit_repo.create(audit_log)

    return ModuleSettingResponse.model_validate(updated_setting)


@router.delete("/{setting_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_setting(
    setting_id: int,
    request: Request,
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Delete a module setting"""
    repo = ModuleSettingRepository(db)
    setting = repo.get_by_id(setting_id)

    if not setting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Setting not found"
        )

    # Store for audit
    setting_info = {
        "module_name": setting.module_name,
        "setting_key": setting.setting_key,
        "setting_value": setting.setting_value,
    }

    repo.delete(setting)

    # Create audit log
    audit_repo = AuditLogRepository(db)
    audit_log = AuditLog(
        user_id=current_user["id"],
        user_email=current_user.get("email"),
        action="DELETE",
        module_name="admin",
        resource_type="module_setting",
        resource_id=str(setting_id),
        description=f"Deleted setting {setting_info['setting_key']} from module {setting_info['module_name']}",
        changes={"before": setting_info},
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request),
    )
    audit_repo.create(audit_log)
