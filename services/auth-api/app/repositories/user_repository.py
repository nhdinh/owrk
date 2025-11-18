"""
User Repository with specific user-related operations
WRITE Repository for CQRS Pattern - handles Commands (MySQL)
"""

from typing import Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import asyncio

from app.repositories.base_repository import BaseRepository
from app.models.user import User
from app.core.events import UserEvents, user_to_event_data


class UserRepository(BaseRepository[User]):
    """
    WRITE Repository for User entity with specific user operations
    Part of CQRS Pattern - handles Commands and publishes events
    """

    def __init__(self, db: Session):
        super().__init__(User, db)

    def create(self, entity: User) -> User:
        """
        Create user and publish UserCreated event

        Args:
            entity: User entity to create

        Returns:
            Created user
        """
        user = super().create(entity)
        self.db.flush()  # Ensure ID is generated

        # Publish event asynchronously
        try:
            asyncio.create_task(UserEvents.user_created(user_to_event_data(user)))
        except RuntimeError:
            # If no event loop, skip event publishing (e.g., in tests)
            pass

        return user

    def update(self, entity: User) -> User:
        """
        Update user and publish UserUpdated event

        Args:
            entity: User entity to update

        Returns:
            Updated user
        """
        user = super().update(entity)
        self.db.flush()

        # Publish event asynchronously
        try:
            asyncio.create_task(UserEvents.user_updated(user_to_event_data(user)))
        except RuntimeError:
            pass

        return user

    def delete(self, entity_id: int) -> bool:
        """
        Delete user and publish UserDeleted event

        Args:
            entity_id: User ID to delete

        Returns:
            True if successful
        """
        result = super().delete(entity_id)

        if result:
            try:
                asyncio.create_task(UserEvents.user_deleted(entity_id))
            except RuntimeError:
                pass

        return result

    def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        return (
            self.db.query(User)
            .filter(User.email == email)
            .order_by(User.version.desc())
            .first()
        )

    def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        return (
            self.db.query(User)
            .filter(User.username == username)
            .order_by(User.version.desc())
            .first()
        )

    def get_by_ad_sync_id(self, ad_sync_id: str) -> Optional[User]:
        """Get user by Active Directory sync ID"""
        return self.db.query(User).filter(User.ad_sync_id == ad_sync_id).first()

    def get_by_role_id(self, role_id: int) -> list[User]:
        """Get all users with a specific role"""
        return self.db.query(User).filter(User.role_id == role_id).all()

    def increment_failed_attempts(self, user_id: int) -> None:
        """Increment failed login attempts for user"""
        user = self.get_by_id(user_id)
        if user:
            user.failed_login_attempts += 1
            user.last_failed_login_at = datetime.utcnow()
            self.db.flush()

    def reset_failed_attempts(self, user_id: int) -> None:
        """Reset failed login attempts to 0"""
        user = self.get_by_id(user_id)
        if user:
            user.failed_login_attempts = 0
            user.last_failed_login_at = None
            self.db.flush()

    def lock_account(self, user_id: int, duration_minutes: int = 30) -> None:
        """Lock user account for specified duration"""
        user = self.get_by_id(user_id)
        if user:
            user.locked_until = datetime.utcnow() + timedelta(minutes=duration_minutes)
            self.db.flush()

    def unlock_account(self, user_id: int) -> None:
        """Unlock user account"""
        user = self.get_by_id(user_id)
        if user:
            user.locked_until = None
            user.failed_login_attempts = 0
            self.db.flush()

    def update_last_login(self, user_id: int, ip_address: Optional[str] = None) -> None:
        """Update last login timestamp and IP"""
        user = self.get_by_id(user_id)
        if user:
            user.last_login_at = datetime.utcnow()
            if ip_address:
                user.last_login_ip = ip_address
            self.db.flush()

    def get_active_users(self, skip: int = 0, limit: int = 100) -> list[User]:
        """Get all active users"""
        return (
            self.db.query(User)
            .filter(User.is_active == True)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_users_by_type(
        self, user_type: str, skip: int = 0, limit: int = 100
    ) -> list[User]:
        """Get users by type (local or active_directory)"""
        return (
            self.db.query(User)
            .filter(User.user_type == user_type)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_users_with_mfa_enabled(self, skip: int = 0, limit: int = 100) -> list[User]:
        """Get users with MFA enabled"""
        return (
            self.db.query(User)
            .filter(User.mfa_enabled == True)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def email_exists(self, email: str) -> bool:
        """Check if email already exists"""
        return self.db.query(User.id).filter(User.email == email).scalar() is not None

    def username_exists(self, username: str) -> bool:
        """Check if username already exists"""
        return (
            self.db.query(User.id).filter(User.username == username).scalar()
            is not None
        )
