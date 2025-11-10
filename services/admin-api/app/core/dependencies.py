"""
Core dependencies for dependency injection
"""

from typing import Generator
from fastapi import Depends, HTTPException, status, Request
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
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """
    Extract user information from JWT token

    Args:
        credentials: HTTP Bearer token credentials

    Returns:
        dict: User information including id, email

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
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
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


def require_admin(current_user: dict = Depends(get_current_user)) -> dict:
    """
    Require admin role for accessing endpoint

    Args:
        current_user: Current authenticated user

    Returns:
        dict: User information

    Raises:
        HTTPException: If user is not an admin
    """
    # TODO: Implement role checking with auth service
    # For now, allow all authenticated users
    return current_user


def get_client_ip(request: Request) -> str:
    """
    Extract client IP address from request

    Args:
        request: FastAPI request object

    Returns:
        str: Client IP address
    """
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def get_user_agent(request: Request) -> str:
    """
    Extract user agent from request

    Args:
        request: FastAPI request object

    Returns:
        str: User agent string
    """
    return request.headers.get("User-Agent", "unknown")
