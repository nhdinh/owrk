"""
Role Management API Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.dependencies import require_permission
from app.core.unit_of_work import UnitOfWork
from app.models.user import User


router = APIRouter(prefix="/roles", tags=["Role Management"])


@router.get("")
async def get_roles(
    current_user: User = Depends(require_permission("role:read"))
):
    """
    Get all roles
    Requires 'role:read' permission
    """
    with UnitOfWork() as uow:
        roles = uow.roles.get_all()

        # Serialize data within session context
        result = []
        for role in roles:
            result.append({
                "id": role.id,
                "name": role.name,
                "display_name": role.display_name,
                "description": role.description,
                "is_active": role.is_active,
                "created_at": role.created_at.isoformat() if role.created_at else None,
                "updated_at": role.updated_at.isoformat() if role.updated_at else None,
            })

        return result


@router.get("/{role_id}")
async def get_role(
    role_id: int,
    current_user: User = Depends(require_permission("role:read"))
):
    """
    Get role by ID
    Requires 'role:read' permission
    """
    with UnitOfWork() as uow:
        role = uow.roles.get_by_id(role_id)
        if not role:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")

        # Serialize data within session context
        return {
            "id": role.id,
            "name": role.name,
            "display_name": role.display_name,
            "description": role.description,
            "is_active": role.is_active,
            "created_at": role.created_at.isoformat() if role.created_at else None,
            "updated_at": role.updated_at.isoformat() if role.updated_at else None,
        }
