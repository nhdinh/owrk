"""
User Management API Endpoints
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from app.schemas.user_schema import (
    UserCreate,
    UserUpdate,
    UserResponse,
    ChangePasswordRequest,
)
from app.core.dependencies import get_current_user, require_permission, require_role
from app.core.unit_of_work import UnitOfWork
from app.core.security import hash_password, verify_password
from app.models.user import User

logger = logging.getLogger(__name__)


router = APIRouter(prefix="/users", tags=["User Management"])


@router.get("")
async def get_users(
    page: int = 1,
    page_size: int = 100,
    skip: int = None,
    limit: int = None,
    current_user: User = Depends(require_permission("user:read")),
):
    """
    Get all users (paginated)
    Requires 'user:read' permission

    Supports both page-based and offset-based pagination:
    - page/page_size: page=1, page_size=10 (returns first 10 items)
    - skip/limit: skip=0, limit=10 (returns first 10 items)
    """
    # Convert page-based to offset-based if using page params
    if skip is None:
        skip = (page - 1) * page_size
    if limit is None:
        limit = page_size

    with UnitOfWork() as uow:
        users = uow.users.get_all(skip=skip, limit=limit)
        total_count = uow.users.count()

        # Serialize data within session context
        result = []
        for user in users:
            # Serialize role if exists
            role_data = None
            if user.role:
                role_data = {
                    "id": user.role.id,
                    "name": user.role.name,
                    "display_name": user.role.display_name,
                }

            result.append(
                {
                    "id": user.id,
                    "email": user.email,
                    "username": user.username,
                    "full_name": user.full_name,
                    "user_type": user.user_type,
                    "phone_number": user.phone_number,
                    "position": user.position,
                    "department_id": user.department_id,
                    "is_active": user.is_active,
                    "is_superuser": user.is_superuser,
                    "email_verified": user.email_verified,
                    "mfa_enabled": user.mfa_enabled,
                    "role_id": user.role_id,
                    "role": role_data,
                    "created_at": (
                        user.created_at.isoformat() if user.created_at else None
                    ),
                    "updated_at": (
                        user.updated_at.isoformat() if user.updated_at else None
                    ),
                    "last_login_at": (
                        user.last_login_at.isoformat() if user.last_login_at else None
                    ),
                }
            )

        return {
            "users": result,
            "total": total_count,
            "page": page,
            "page_size": page_size,
        }


@router.get("/active", response_model=List[UserResponse])
async def get_active_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(require_permission("user:read")),
):
    """
    Get active users only
    Requires 'user:read' permission
    """
    with UnitOfWork() as uow:
        users = uow.users.get_active_users(skip=skip, limit=limit)
        return users


@router.get("/{user_id}")
async def get_user(
    user_id: int, current_user: User = Depends(require_permission("user:read"))
):
    """
    Get user by ID
    Requires 'user:read' permission
    """
    with UnitOfWork() as uow:
        user = uow.users.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        # Serialize data within session context
        # Include role object if exists
        role_data = None
        if user.role:
            role_data = {
                "id": user.role.id,
                "name": user.role.name,
                "display_name": user.role.display_name,
            }

        return {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "full_name": user.full_name,
            "user_type": user.user_type,
            "phone_number": user.phone_number,
            "position": user.position,
            "department_id": user.department_id,
            "is_active": user.is_active,
            "is_superuser": user.is_superuser,
            "email_verified": user.email_verified,
            "mfa_enabled": user.mfa_enabled,
            "role_id": user.role_id,
            "role": role_data,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "updated_at": user.updated_at.isoformat() if user.updated_at else None,
            "last_login_at": (
                user.last_login_at.isoformat() if user.last_login_at else None
            ),
        }


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    current_user: User = Depends(require_permission("user:create")),
):
    """
    Create new user
    Requires 'user:create' permission
    """
    with UnitOfWork() as uow:
        # Check if email already exists
        if uow.users.email_exists(user_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        # Check if username already exists
        if user_data.username and uow.users.username_exists(user_data.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken"
            )

        # Hash password for local users
        hashed_password = None
        if user_data.user_type == "local" and user_data.password:
            hashed_password = hash_password(user_data.password)

        # Create user
        user = User(
            email=user_data.email,
            username=user_data.username,
            full_name=user_data.full_name,
            hashed_password=hashed_password,
            user_type=user_data.user_type,
            department_id=user_data.department_id,
            position=user_data.position,
            phone_number=user_data.phone_number,
            role_id=user_data.role_id,
            is_active=True,
        )

        created_user = uow.users.create(user)
        uow.commit()

        # Serialize data within session context
        return {
            "id": created_user.id,
            "email": created_user.email,
            "username": created_user.username,
            "full_name": created_user.full_name,
            "user_type": created_user.user_type,
            "phone_number": created_user.phone_number,
            "position": created_user.position,
            "department_id": created_user.department_id,
            "is_active": created_user.is_active,
            "is_superuser": created_user.is_superuser,
            "email_verified": created_user.email_verified,
            "mfa_enabled": created_user.mfa_enabled,
            "role_id": created_user.role_id,
            "created_at": (
                created_user.created_at.isoformat() if created_user.created_at else None
            ),
            "updated_at": (
                created_user.updated_at.isoformat() if created_user.updated_at else None
            ),
            "last_login_at": (
                created_user.last_login_at.isoformat()
                if created_user.last_login_at
                else None
            ),
        }


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    current_user: User = Depends(require_permission("user:update")),
):
    """
    Update user
    Requires 'user:update' permission
    """
    with UnitOfWork() as uow:
        user = uow.users.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        # Update fields if provided
        if user_data.email is not None:
            # Check email uniqueness
            existing = uow.users.get_by_email(user_data.email)
            if existing and existing.id != user_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already in use",
                )
            user.email = user_data.email

        if user_data.username is not None:
            # Check username uniqueness
            existing = uow.users.get_by_username(user_data.username)
            if existing and existing.id != user_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already taken",
                )
            user.username = user_data.username

        if user_data.full_name is not None:
            user.full_name = user_data.full_name

        if user_data.department_id is not None:
            user.department_id = user_data.department_id

        if user_data.position is not None:
            user.position = user_data.position

        if user_data.address is not None:
            user.address = user_data.address

        if user_data.phone_number is not None:
            user.phone_number = user_data.phone_number

        if user_data.role_id is not None:
            user.role_id = user_data.role_id

        if user_data.is_active is not None:
            user.is_active = user_data.is_active

        updated_user = uow.users.update(user)
        uow.commit()

        # Serialize data within session context
        # Include role object if exists
        role_data = None
        if updated_user.role:
            role_data = {
                "id": updated_user.role.id,
                "name": updated_user.role.name,
                "display_name": updated_user.role.display_name,
            }

        return {
            "id": updated_user.id,
            "email": updated_user.email,
            "username": updated_user.username,
            "full_name": updated_user.full_name,
            "user_type": updated_user.user_type,
            "phone_number": updated_user.phone_number,
            "position": updated_user.position,
            "address": updated_user.address,
            "department_id": updated_user.department_id,
            "is_active": updated_user.is_active,
            "is_superuser": updated_user.is_superuser,
            "email_verified": updated_user.email_verified,
            "mfa_enabled": updated_user.mfa_enabled,
            "role_id": updated_user.role_id,
            "role": role_data,
            "created_at": (
                updated_user.created_at.isoformat() if updated_user.created_at else None
            ),
            "updated_at": (
                updated_user.updated_at.isoformat() if updated_user.updated_at else None
            ),
            "last_login_at": (
                updated_user.last_login_at.isoformat()
                if updated_user.last_login_at
                else None
            ),
        }


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int, current_user: User = Depends(require_permission("user:delete"))
):
    """
    Delete user (soft delete - set inactive)
    Requires 'user:delete' permission
    """
    with UnitOfWork() as uow:
        user = uow.users.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        # Prevent self-deletion
        current_user_id = getattr(current_user, "_auth_id", None)
        if user.id == current_user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot delete yourself"
            )

        # Soft delete - set inactive
        user.is_active = False
        uow.users.update(user)
        uow.commit()

        return None


@router.post("/{user_id}/activate", response_model=UserResponse)
async def activate_user(
    user_id: int, current_user: User = Depends(require_permission("user:update"))
):
    """
    Activate user account
    Requires 'user:update' permission
    """
    with UnitOfWork() as uow:
        user = uow.users.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        user.is_active = True
        updated_user = uow.users.update(user)
        uow.commit()

        # Serialize data within session context
        role_data = None
        if updated_user.role:
            role_data = {
                "id": updated_user.role.id,
                "name": updated_user.role.name,
                "display_name": updated_user.role.display_name,
            }

        return {
            "id": updated_user.id,
            "email": updated_user.email,
            "username": updated_user.username,
            "full_name": updated_user.full_name,
            "user_type": updated_user.user_type,
            "phone_number": updated_user.phone_number,
            "position": updated_user.position,
            "address": updated_user.address,
            "department_id": updated_user.department_id,
            "is_active": updated_user.is_active,
            "is_superuser": updated_user.is_superuser,
            "email_verified": updated_user.email_verified,
            "mfa_enabled": updated_user.mfa_enabled,
            "role_id": updated_user.role_id,
            "role": role_data,
            "created_at": (
                updated_user.created_at.isoformat() if updated_user.created_at else None
            ),
            "updated_at": (
                updated_user.updated_at.isoformat() if updated_user.updated_at else None
            ),
            "last_login_at": (
                updated_user.last_login_at.isoformat()
                if updated_user.last_login_at
                else None
            ),
        }


@router.post("/{user_id}/deactivate", response_model=UserResponse)
async def deactivate_user(
    user_id: int, current_user: User = Depends(require_permission("user:update"))
):
    """
    Deactivate user account
    Requires 'user:update' permission
    """
    with UnitOfWork() as uow:
        user = uow.users.get_by_id(user_id)
        # Get user_id from cached auth attributes to avoid detached instance error
        current_user_id = getattr(current_user, "_auth_id", None)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        # Prevent self-deactivation
        if user_id == current_user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot deactivate yourself",
            )

        user.is_active = False
        updated_user = uow.users.update(user)
        uow.commit()

        # Serialize data within session context
        role_data = None
        if updated_user.role:
            role_data = {
                "id": updated_user.role.id,
                "name": updated_user.role.name,
                "display_name": updated_user.role.display_name,
            }

        return {
            "id": updated_user.id,
            "email": updated_user.email,
            "username": updated_user.username,
            "full_name": updated_user.full_name,
            "user_type": updated_user.user_type,
            "phone_number": updated_user.phone_number,
            "position": updated_user.position,
            "address": updated_user.address,
            "department_id": updated_user.department_id,
            "is_active": updated_user.is_active,
            "is_superuser": updated_user.is_superuser,
            "email_verified": updated_user.email_verified,
            "mfa_enabled": updated_user.mfa_enabled,
            "role_id": updated_user.role_id,
            "role": role_data,
            "created_at": (
                updated_user.created_at.isoformat() if updated_user.created_at else None
            ),
            "updated_at": (
                updated_user.updated_at.isoformat() if updated_user.updated_at else None
            ),
            "last_login_at": (
                updated_user.last_login_at.isoformat()
                if updated_user.last_login_at
                else None
            ),
        }


@router.post("/{user_id}/unlock", response_model=UserResponse)
async def unlock_user(
    user_id: int, current_user: User = Depends(require_role("admin"))
):
    """
    Unlock user account
    Admin only
    """
    with UnitOfWork() as uow:
        user = uow.users.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        uow.users.unlock_account(user_id)
        uow.commit()

        refreshed_user: User = uow.users.get_by_id(user_id)

        # Serialize data within session context
        role_data = None
        if refreshed_user.role:
            role_data = {
                "id": refreshed_user.role.id,
                "name": refreshed_user.role.name,
                "display_name": refreshed_user.role.display_name,
            }

        return {
            "id": refreshed_user.id,
            "email": refreshed_user.email,
            "username": refreshed_user.username,
            "full_name": refreshed_user.full_name,
            "user_type": refreshed_user.user_type,
            "phone_number": refreshed_user.phone_number,
            "position": refreshed_user.position,
            "address": refreshed_user.address,
            "department_id": refreshed_user.department_id,
            "is_active": refreshed_user.is_active,
            "is_superuser": refreshed_user.is_superuser,
            "email_verified": refreshed_user.email_verified,
            "mfa_enabled": refreshed_user.mfa_enabled,
            "role_id": refreshed_user.role_id,
            "role": role_data,
            "created_at": (
                refreshed_user.created_at.isoformat()
                if refreshed_user.created_at
                else None
            ),
            "updated_at": (
                refreshed_user.updated_at.isoformat()
                if refreshed_user.updated_at
                else None
            ),
            "last_login_at": (
                refreshed_user.last_login_at.isoformat()
                if refreshed_user.last_login_at
                else None
            ),
        }


@router.post("/change-password")
async def change_password(
    request: ChangePasswordRequest, current_user: User = Depends(get_current_user)
):
    """
    Change current user's password
    """
    logger.info("hello")
    current_user_id = getattr(current_user, "_auth_id", None)
    with UnitOfWork() as uow:
        user = uow.users.get_by_id(current_user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        # Only local users can change password
        if user.user_type != "local":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password change not available for Active Directory users",
            )

        # Verify old password
        if not user.hashed_password or not verify_password(
            request.current_password, user.hashed_password
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid current password",
            )

        # Update password
        user.hashed_password = hash_password(request.new_password)
        uow.users.update(user)

        # Revoke all refresh tokens for security
        uow.refresh_tokens.revoke_all_user_tokens(user.id)

        uow.commit()

        return {"message": "Password changed successfully. Please login again."}
