"""
FastAPI dependencies for Dashboard API
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.database import get_db
import logging

logger = logging.getLogger(__name__)

security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    """
    Validate JWT token and return current user

    For dashboard service, we just validate the token.
    We don't need to fetch full user details.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        token = credentials.credentials
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        user_id: int = payload.get("sub")
        if user_id is None:
            raise credentials_exception

        # Return a simple dict with user_id
        # Dashboard doesn't need full user object for most operations
        return {"id": user_id}

    except JWTError as e:
        logger.error(f"JWT validation error: {e}")
        raise credentials_exception
