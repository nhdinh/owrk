"""User Query DTOs"""

from dataclasses import dataclass
from typing import Optional
from app.core.message_bus import Query


@dataclass
class GetUserByIdQuery(Query):
    """Query to get user by ID"""

    user_id: int


@dataclass
class GetUserByEmailQuery(Query):
    """Query to get user by email"""

    email: str


@dataclass
class GetUsersListQuery(Query):
    """Query to get list of users with pagination and filters"""

    skip: int = 0
    limit: int = 100
    search: Optional[str] = None
    role_id: Optional[int] = None
    is_active: Optional[bool] = None
    department_id: Optional[int] = None


@dataclass
class GetCurrentUserQuery(Query):
    """Query to get current authenticated user"""

    user_id: int


@dataclass
class GetUserHistoryQuery(Query):
    """Query to get user version history"""

    user_id: int
    skip: int = 0
    limit: int = 50
