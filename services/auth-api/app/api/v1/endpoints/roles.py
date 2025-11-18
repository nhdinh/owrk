"""
Role Management API Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.dependencies import require_permission
from app.core.unit_of_work import UnitOfWork
from app.models.user import User
from app.models.role import Role
from app.schemas.role_schema import RoleCreate, RoleUpdate, RoleResponse


router = APIRouter(prefix="/roles", tags=["Role Management"])


@router.get("")
async def get_roles(current_user: User = Depends(require_permission("role:read"))):
    """
    Get all roles
    Requires 'role:read' permission
    """
    with UnitOfWork() as uow:
        roles = uow.roles.get_all()
        total_count = uow.roles.count()

        # Serialize data within session context
        result = []
        for role in roles:
            # Include permissions array for frontend
            permissions_data = []
            if role.permissions:
                for perm in role.permissions:
                    permissions_data.append(
                        {
                            "id": perm.id,
                            "name": perm.name,
                            "code": perm.name,
                            "resource": perm.resource,
                            "action": perm.action,
                            "description": perm.description,
                        }
                    )

            result.append(
                {
                    "id": role.id,
                    "name": role.name,
                    "display_name": role.display_name,
                    "description": role.description,
                    "is_active": role.is_active,
                    "permissions": permissions_data,
                    "created_at": (
                        role.created_at.isoformat() if role.created_at else None
                    ),
                    "updated_at": (
                        role.updated_at.isoformat() if role.updated_at else None
                    ),
                }
            )

        return {"roles": result, "total": total_count}


@router.get("/{role_id}")
async def get_role(
    role_id: str, current_user: User = Depends(require_permission("role:read"))
):
    """
    Get role by ID
    Requires 'role:read' permission
    """
    with UnitOfWork() as uow:
        role = uow.roles.get_by_id(role_id)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Role not found"
            )

        # Serialize data within session context
        # Include permissions array
        permissions_data = []
        if role.permissions:
            for perm in role.permissions:
                permissions_data.append(
                    {
                        "id": perm.id,
                        "name": perm.name,
                        "code": perm.name,  # Alias for frontend compatibility
                        "resource": perm.resource,
                        "action": perm.action,
                        "description": perm.description,
                    }
                )

        return {
            "id": role.id,
            "name": role.name,
            "display_name": role.display_name,
            "description": role.description,
            "is_active": role.is_active,
            "permissions": permissions_data,
            "created_at": role.created_at.isoformat() if role.created_at else None,
            "updated_at": role.updated_at.isoformat() if role.updated_at else None,
        }


@router.get("/permissions/all")
async def get_all_permissions(
    current_user: User = Depends(require_permission("role:read")),
):
    """
    Get all available permissions
    Requires 'role:read' permission
    """
    with UnitOfWork() as uow:
        permissions = uow.permissions.get_all()

        # Serialize data within session context
        result = []
        for permission in permissions:
            result.append(
                {
                    "id": permission.id,
                    "name": permission.name,
                    "code": permission.name,  # Alias for frontend compatibility
                    "resource": permission.resource,
                    "action": permission.action,
                    "description": permission.description,
                    "created_at": (
                        permission.created_at.isoformat()
                        if permission.created_at
                        else None
                    ),
                    "updated_at": (
                        permission.updated_at.isoformat()
                        if permission.updated_at
                        else None
                    ),
                }
            )

        return result


@router.post("", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
async def create_role(
    role_data: RoleCreate,
    current_user: User = Depends(require_permission("role:create")),
):
    """
    Create a new role
    Requires 'role:create' permission
    """
    with UnitOfWork() as uow:
        # Check if role name already exists
        existing = uow.roles.get_by_name(role_data.name)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Role with name '{role_data.name}' already exists",
            )

        # Create new role
        new_role = Role(
            name=role_data.name,
            display_name=role_data.display_name,
            description=role_data.description,
            is_active=role_data.is_active,
        )

        created_role = uow.roles.create(new_role)
        uow.commit()

        # Serialize data within session context
        return {
            "id": created_role.id,
            "name": created_role.name,
            "display_name": created_role.display_name,
            "description": created_role.description,
            "is_active": created_role.is_active,
            "created_at": (
                created_role.created_at.isoformat() if created_role.created_at else None
            ),
            "updated_at": (
                created_role.updated_at.isoformat() if created_role.updated_at else None
            ),
        }


@router.put("/{role_id}", response_model=RoleResponse)
async def update_role(
    role_id: int,
    role_data: RoleUpdate,
    current_user: User = Depends(require_permission("role:update")),
):
    """
    Update role
    Requires 'role:update' permission
    """
    with UnitOfWork() as uow:
        role = uow.roles.get_by_id(role_id)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Role not found"
            )

        # Update fields if provided
        if role_data.name is not None:
            # Check name uniqueness
            existing = uow.roles.get_by_name(role_data.name)
            if existing and existing.id != role_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Role with name '{role_data.name}' already exists",
                )
            role.name = role_data.name

        if role_data.display_name is not None:
            role.display_name = role_data.display_name

        if role_data.description is not None:
            role.description = role_data.description

        if role_data.is_active is not None:
            role.is_active = role_data.is_active

        updated_role = uow.roles.update(role)
        uow.commit()

        # Serialize data within session context
        return {
            "id": updated_role.id,
            "name": updated_role.name,
            "display_name": updated_role.display_name,
            "description": updated_role.description,
            "is_active": updated_role.is_active,
            "created_at": (
                updated_role.created_at.isoformat() if updated_role.created_at else None
            ),
            "updated_at": (
                updated_role.updated_at.isoformat() if updated_role.updated_at else None
            ),
        }


@router.delete("/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_role(
    role_id: int, current_user: User = Depends(require_permission("role:delete"))
):
    """
    Delete role (soft delete - set inactive)
    Requires 'role:delete' permission
    """
    with UnitOfWork() as uow:
        role = uow.roles.get_by_id(role_id)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Role not found"
            )

        # Check if role is assigned to any users
        users_with_role = uow.users.get_by_role_id(role_id)
        if users_with_role:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot delete role. {len(users_with_role)} user(s) still have this role assigned.",
            )

        # Soft delete - set inactive
        role.is_active = False
        uow.roles.update(role)
        uow.commit()

        return None


@router.post(
    "/{role_id}/permissions/{permission_id}", status_code=status.HTTP_201_CREATED
)
async def add_permission_to_role(
    role_id: int,
    permission_id: int,
    current_user: User = Depends(require_permission("role:update")),
):
    """
    Add permission to role
    Requires 'role:update' permission
    """
    with UnitOfWork() as uow:
        role = uow.roles.get_by_id(role_id)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Role not found"
            )

        permission = uow.permissions.get_by_id(permission_id)
        if not permission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Permission not found"
            )

        # Check if permission already assigned
        if permission in role.permissions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Permission already assigned to this role",
            )

        # Add permission
        role.permissions.append(permission)
        uow.commit()

        return {"message": "Permission added successfully"}


@router.delete(
    "/{role_id}/permissions/{permission_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def remove_permission_from_role(
    role_id: int,
    permission_id: int,
    current_user: User = Depends(require_permission("role:update")),
):
    """
    Remove permission from role
    Requires 'role:update' permission
    """
    with UnitOfWork() as uow:
        role = uow.roles.get_by_id(role_id)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Role not found"
            )

        permission = uow.permissions.get_by_id(permission_id)
        if not permission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Permission not found"
            )

        # Check if permission is assigned
        if permission not in role.permissions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Permission not assigned to this role",
            )

        # Remove permission
        role.permissions.remove(permission)
        uow.commit()

        return None
