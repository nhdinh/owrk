"""
Core dependencies for dependency injection
Handles authentication, database sessions, and service initialization
"""

from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import SessionLocal

# Security scheme for Bearer token
security = HTTPBearer()


def get_db() -> Generator:
    """
    Database session dependency
    Creates a new database session for each request
    and closes it when done
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> int:
    """
    Extract and validate user ID from JWT token

    Args:
        credentials: HTTP Bearer token credentials

    Returns:
        int: User ID from token

    Raises:
        HTTPException: If token is invalid or expired
    """
    token = credentials.credentials
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        return int(user_id)
    except (JWTError, ValueError):
        raise credentials_exception


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """
    Extract full user information from JWT token

    Args:
        credentials: HTTP Bearer token credentials

    Returns:
        dict: User information including id, email, role

    Raises:
        HTTPException: If token is invalid or expired
    """
    token = credentials.credentials
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        email: str = payload.get("email")

        if user_id is None:
            raise credentials_exception

        return {
            "id": int(user_id),
            "email": email,
            "type": payload.get("type"),
        }
    except (JWTError, ValueError):
        raise credentials_exception


def require_role(required_roles: list[str]):
    """
    Dependency to check if user has required role

    Args:
        required_roles: List of acceptable role names

    Returns:
        Dependency function that validates user role

    Example:
        @router.post("/purchase-orders", dependencies=[Depends(require_role(["admin", "procurement_manager"]))])
    """
    async def role_checker(
        current_user: dict = Depends(get_current_user)
    ) -> dict:
        user_role = current_user.get("role", "").lower()
        if user_role not in [r.lower() for r in required_roles]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required roles: {', '.join(required_roles)}"
            )
        return current_user

    return role_checker


class CommonQueryParams:
    """
    Common query parameters for list endpoints
    Provides pagination, search, and filtering
    """
    def __init__(
        self,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        sort_by: Optional[str] = None,
        sort_order: str = "asc"
    ):
        self.skip = skip
        self.limit = min(limit, 100)  # Max 100 items per page
        self.search = search
        self.sort_by = sort_by
        self.sort_order = sort_order.lower() if sort_order else "asc"


# Utility function to verify token for inter-service communication
def verify_service_token(token: str) -> bool:
    """
    Verify token from another service
    Used for inter-service authentication

    Args:
        token: JWT token from calling service

    Returns:
        bool: True if token is valid
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload.get("type") == "access"
    except JWTError:
        return False
