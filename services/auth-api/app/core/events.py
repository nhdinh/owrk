"""
Domain Events for CQRS Pattern
Events published to RabbitMQ when state changes occur
"""

from datetime import datetime
from typing import Dict, Any, Optional
from app.core.rabbitmq import publish_event
import logging

logger = logging.getLogger(__name__)


class DomainEvents:
    """
    Domain events publisher for Auth Service
    Publishes events to RabbitMQ for CQRS synchronization
    """

    EXCHANGE_NAME = "auth.events"

    @staticmethod
    async def publish(event_type: str, data: Dict[str, Any], metadata: Optional[Dict] = None):
        """
        Publish domain event to RabbitMQ

        Args:
            event_type: Event type (e.g., "user.created")
            data: Event payload
            metadata: Optional metadata (user_id, ip, etc.)
        """
        event = {
            "event_type": event_type,
            "timestamp": datetime.utcnow().isoformat(),
            "data": data,
            "metadata": metadata or {},
            "service": "auth-service"
        }

        try:
            await publish_event(
                routing_key=event_type,
                event_data=data,
                exchange_name=DomainEvents.EXCHANGE_NAME
            )
            logger.info(f"📤 Published event: {event_type} for entity ID: {data.get('id')}")
        except Exception as e:
            logger.error(f"❌ Failed to publish event {event_type}: {str(e)}")
            # Don't raise - event publishing failure shouldn't break the operation


class UserEvents:
    """User-related domain events"""

    @staticmethod
    async def user_created(user_data: Dict):
        """
        Publish UserCreated event

        Args:
            user_data: User entity data
        """
        await DomainEvents.publish(
            event_type="user.created",
            data=user_data
        )

    @staticmethod
    async def user_updated(user_data: Dict):
        """
        Publish UserUpdated event

        Args:
            user_data: Updated user data
        """
        await DomainEvents.publish(
            event_type="user.updated",
            data=user_data
        )

    @staticmethod
    async def user_deleted(user_id: int):
        """
        Publish UserDeleted event

        Args:
            user_id: Deleted user ID
        """
        await DomainEvents.publish(
            event_type="user.deleted",
            data={"id": user_id}
        )

    @staticmethod
    async def user_activated(user_id: int, user_email: str):
        """
        Publish UserActivated event

        Args:
            user_id: User ID
            user_email: User email
        """
        await DomainEvents.publish(
            event_type="user.activated",
            data={"id": user_id, "email": user_email}
        )

    @staticmethod
    async def user_deactivated(user_id: int, user_email: str):
        """
        Publish UserDeactivated event

        Args:
            user_id: User ID
            user_email: User email
        """
        await DomainEvents.publish(
            event_type="user.deactivated",
            data={"id": user_id, "email": user_email}
        )

    @staticmethod
    async def user_logged_in(user_id: int, user_email: str, ip_address: str):
        """
        Publish UserLoggedIn event

        Args:
            user_id: User ID
            user_email: User email
            ip_address: Login IP address
        """
        await DomainEvents.publish(
            event_type="user.logged_in",
            data={"id": user_id, "email": user_email},
            metadata={"ip_address": ip_address}
        )

    @staticmethod
    async def mfa_enabled(user_id: int, user_email: str):
        """
        Publish MFAEnabled event

        Args:
            user_id: User ID
            user_email: User email
        """
        await DomainEvents.publish(
            event_type="user.mfa_enabled",
            data={"id": user_id, "email": user_email, "mfa_enabled": True}
        )

    @staticmethod
    async def mfa_disabled(user_id: int, user_email: str):
        """
        Publish MFADisabled event

        Args:
            user_id: User ID
            user_email: User email
        """
        await DomainEvents.publish(
            event_type="user.mfa_disabled",
            data={"id": user_id, "email": user_email, "mfa_enabled": False}
        )

    @staticmethod
    async def password_changed(user_id: int, user_email: str):
        """
        Publish PasswordChanged event

        Args:
            user_id: User ID
            user_email: User email
        """
        await DomainEvents.publish(
            event_type="user.password_changed",
            data={"id": user_id, "email": user_email}
        )


class RoleEvents:
    """Role-related domain events"""

    @staticmethod
    async def role_created(role_data: Dict):
        """
        Publish RoleCreated event

        Args:
            role_data: Role entity data
        """
        await DomainEvents.publish(
            event_type="role.created",
            data=role_data
        )

    @staticmethod
    async def role_updated(role_data: Dict):
        """
        Publish RoleUpdated event

        Args:
            role_data: Updated role data
        """
        await DomainEvents.publish(
            event_type="role.updated",
            data=role_data
        )

    @staticmethod
    async def role_deleted(role_id: int):
        """
        Publish RoleDeleted event

        Args:
            role_id: Deleted role ID
        """
        await DomainEvents.publish(
            event_type="role.deleted",
            data={"id": role_id}
        )


def user_to_event_data(user) -> Dict:
    """
    Convert User model to event data (safe for publishing)
    Excludes sensitive fields like password hashes

    Args:
        user: User model instance

    Returns:
        Safe user data dict
    """
    return {
        "id": user.id,
        "email": user.email,
        "username": user.username,
        "full_name": user.full_name,
        "user_type": user.user_type,
        "ad_sync_id": user.ad_sync_id,
        "is_active": user.is_active,
        "is_superuser": user.is_superuser,
        "email_verified": user.email_verified,
        "mfa_enabled": user.mfa_enabled,
        "failed_login_attempts": user.failed_login_attempts,
        "locked_until": user.locked_until.isoformat() if user.locked_until else None,
        "last_login_at": user.last_login_at.isoformat() if user.last_login_at else None,
        "last_login_ip": user.last_login_ip,
        "password_changed_at": user.password_changed_at.isoformat() if user.password_changed_at else None,
        "department_id": user.department_id,
        "phone_number": user.phone_number,
        "address": user.address,
        "position": user.position,
        "role_id": user.role_id,
        "created_at": user.created_at.isoformat() if user.created_at else None,
        "updated_at": user.updated_at.isoformat() if user.updated_at else None
    }


def role_to_event_data(role) -> Dict:
    """
    Convert Role model to event data

    Args:
        role: Role model instance

    Returns:
        Role data dict
    """
    return {
        "id": role.id,
        "name": role.name,
        "description": role.description,
        "permissions": role.permissions,
        "is_active": role.is_active,
        "created_at": role.created_at.isoformat() if role.created_at else None,
        "updated_at": role.updated_at.isoformat() if role.updated_at else None
    }
