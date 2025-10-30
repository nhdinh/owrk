"""
FastAPI Dependencies for authentication and authorization
"""

import logging
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.security import decode_token
from app.core.unit_of_work import UnitOfWork
from app.core.message_bus import MessageBus, get_message_bus
from app.models.user import User

logger = logging.getLogger(__name__)


# HTTP Bearer token scheme
security = HTTPBearer()


# Export get_message_bus for dependency injection
__all__ = [
    "get_current_user",
    "get_current_active_user",
    "get_optional_user",
    "require_permission",
    "require_role",
    "require_any_role",
    "get_message_bus",
]


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> User:
    """
    Get current authenticated user from JWT token

    Args:
        credentials: HTTP Authorization credentials

    Returns:
        User entity

    Raises:
        HTTPException: If token is invalid or user not found
    """
    token = credentials.credentials

    # Decode token
    payload = decode_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verify token type
    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Get user from database
    with UnitOfWork() as uow:
        user = uow.users.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="User account is inactive"
            )

        # Create a detached copy with accessible ID
        # Store all needed attributes before session closes
        user_dict = {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "is_active": user.is_active,
            "mfa_enabled": user.mfa_enabled,
            "user_type": user.user_type,
            "role_id": user.role_id,
            "department_id": user.department_id,
        }

        # Eager load role to avoid detached instance errors
        if user.role:
            _ = user.role.id  # Access role to load it before session closes
            _ = user.role.name
            _ = user.role.display_name

        # Store attributes as custom _auth properties to avoid SQLAlchemy access
        for key, value in user_dict.items():
            setattr(user, f"_auth_{key}", value)

        return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Get current active user (alias for get_current_user)

    Args:
        current_user: Current user from get_current_user

    Returns:
        User entity
    """
    return current_user


def require_permission(permission_name: str):
    """
    Dependency factory to require specific permission

    Args:
        permission_name: Permission name (e.g., "asset:read", "user:create")

    Returns:
        Dependency function

    Example:
        @router.get("/assets", dependencies=[Depends(require_permission("asset:read"))])
    """

    async def permission_checker(
        current_user: User = Depends(get_current_user),
    ) -> User:
        # Get cached user_id to avoid detached instance error
        user_id = getattr(current_user, "_auth_id", None)
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid user"
            )

        with UnitOfWork() as uow:
            # Get user's role
            user = uow.users.get_by_id(user_id)

            if not user or not user.role:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="User has no role assigned",
                )

            # Check if user's role has the required permission
            has_permission = False
            for perm in user.role.permissions:
                if perm.name == permission_name:
                    has_permission = True
                    break

            if not has_permission:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission denied: {permission_name} required",
                )

            # Cache attributes with _auth_ prefix to avoid detached instance errors
            user_dict = {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "is_active": user.is_active,
                "mfa_enabled": user.mfa_enabled,
                "user_type": user.user_type,
                "role_id": user.role_id,
                "department_id": user.department_id,
            }
            for key, value in user_dict.items():
                setattr(user, f"_auth_{key}", value)

            return user

    return permission_checker


def require_role(role_name: str):
    """
    Dependency factory to require specific role

    Args:
        role_name: Role name (e.g., "admin", "manager")

    Returns:
        Dependency function

    Example:
        @router.get("/admin", dependencies=[Depends(require_role("admin"))])
    """

    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        # Get cached user_id to avoid detached instance error
        user_id = getattr(current_user, "_auth_id", None)
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid user"
            )

        with UnitOfWork() as uow:
            user = uow.users.get_by_id(user_id)
            if not user or not user.role:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="User has no role assigned",
                )

            if user.role.name != role_name:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Role '{role_name}' required",
                )

            # Cache attributes with _auth_ prefix to avoid detached instance errors
            user_dict = {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "is_active": user.is_active,
                "mfa_enabled": user.mfa_enabled,
                "user_type": user.user_type,
                "role_id": user.role_id,
                "department_id": user.department_id,
            }
            for key, value in user_dict.items():
                setattr(user, f"_auth_{key}", value)

            return user

    return role_checker


def require_any_role(*role_names: str):
    """
    Dependency factory to require any of the specified roles

    Args:
        role_names: List of acceptable role names

    Returns:
        Dependency function

    Example:
        @router.get("/dashboard", dependencies=[Depends(require_any_role("admin", "manager"))])
    """

    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        # Get cached user_id to avoid detached instance error
        user_id = getattr(current_user, "_auth_id", None)
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid user"
            )

        with UnitOfWork() as uow:
            user = uow.users.get_by_id(user_id)
            if not user or not user.role:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="User has no role assigned",
                )

            if user.role.name not in role_names:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"One of these roles required: {', '.join(role_names)}",
                )

            # Cache attributes with _auth_ prefix to avoid detached instance errors
            user_dict = {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "is_active": user.is_active,
                "mfa_enabled": user.mfa_enabled,
                "user_type": user.user_type,
                "role_id": user.role_id,
                "department_id": user.department_id,
            }
            for key, value in user_dict.items():
                setattr(user, f"_auth_{key}", value)

            return user

    return role_checker


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(
        HTTPBearer(auto_error=False)
    ),
) -> Optional[User]:
    """
    Get current user if token is provided, otherwise None

    Args:
        credentials: Optional HTTP Authorization credentials

    Returns:
        User entity or None
    """
    if not credentials:
        return None

    try:
        token = credentials.credentials
        payload = decode_token(token)
        if not payload or payload.get("type") != "access":
            return None

        user_id = payload.get("sub")
        if not user_id:
            return None

        with UnitOfWork() as uow:
            user = uow.users.get_by_id(user_id)
            return user if user and user.is_active else None

    except Exception:
        return None
