"""
User Event Consumer - CQRS Read Model Updater
Listens to user events and updates MongoDB
"""

import logging
from typing import Dict
from app.core.mongo_db import get_mongo_db
from app.repositories.user_read_repository import UserReadRepository

logger = logging.getLogger(__name__)


class UserEventConsumer:
    """
    Consumer for user-related events
    Updates MongoDB read model when user state changes
    """

    def __init__(self):
        self.user_read_repo = None

    async def initialize(self):
        """Initialize repositories"""
        mongo_db = get_mongo_db()
        self.user_read_repo = UserReadRepository(mongo_db)
        await self.user_read_repo.create_indexes()
        logger.info("✅ UserEventConsumer initialized")

    async def handle_event(self, event: Dict):
        """
        Handle incoming event from RabbitMQ

        Args:
            event: Event data with event_type, timestamp, data
        """
        event_type = event.get("event_type")
        event_data = event.get("data", {})

        logger.info(f"📥 Processing event: {event_type}")

        try:
            if event_type == "user.created":
                await self._handle_user_created(event_data)
            elif event_type == "user.updated":
                await self._handle_user_updated(event_data)
            elif event_type == "user.deleted":
                await self._handle_user_deleted(event_data)
            elif event_type == "user.activated":
                await self._handle_user_status_changed(event_data, is_active=True)
            elif event_type == "user.deactivated":
                await self._handle_user_status_changed(event_data, is_active=False)
            elif event_type == "user.mfa_enabled":
                await self._handle_mfa_changed(event_data, mfa_enabled=True)
            elif event_type == "user.mfa_disabled":
                await self._handle_mfa_changed(event_data, mfa_enabled=False)
            elif event_type == "user.logged_in":
                await self._handle_user_logged_in(event_data, event.get("metadata", {}))
            elif event_type == "user.password_changed":
                await self._handle_password_changed(event_data)
            else:
                logger.warning(f"⚠️ Unhandled event type: {event_type}")

            logger.info(f"✅ Event processed successfully: {event_type}")

        except Exception as e:
            logger.error(f"❌ Error processing event {event_type}: {str(e)}")
            # In production, you might want to:
            # - Send to dead letter queue
            # - Retry with exponential backoff
            # - Alert monitoring system
            raise

    async def _handle_user_created(self, user_data: Dict):
        """Handle UserCreated event"""
        await self.user_read_repo.upsert_user(user_data)
        logger.info(f"✅ User created in read model: {user_data.get('email')}")

    async def _handle_user_updated(self, user_data: Dict):
        """Handle UserUpdated event"""
        await self.user_read_repo.upsert_user(user_data)
        logger.info(f"✅ User updated in read model: {user_data.get('email')}")

    async def _handle_user_deleted(self, data: Dict):
        """Handle UserDeleted event"""
        user_id = data.get("id")
        if user_id:
            await self.user_read_repo.delete_user(user_id)
            logger.info(f"✅ User deleted from read model: ID {user_id}")

    async def _handle_user_status_changed(self, data: Dict, is_active: bool):
        """Handle user activation/deactivation"""
        user_id = data.get("id")
        if user_id:
            # Get existing user and update is_active field
            existing_user = await self.user_read_repo.get_by_id(user_id)
            if existing_user:
                existing_user["is_active"] = is_active
                await self.user_read_repo.upsert_user(existing_user)
                status = "activated" if is_active else "deactivated"
                logger.info(f"✅ User {status} in read model: {data.get('email')}")

    async def _handle_mfa_changed(self, data: Dict, mfa_enabled: bool):
        """Handle MFA enabled/disabled"""
        user_id = data.get("id")
        if user_id:
            existing_user = await self.user_read_repo.get_by_id(user_id)
            if existing_user:
                existing_user["mfa_enabled"] = mfa_enabled
                await self.user_read_repo.upsert_user(existing_user)
                status = "enabled" if mfa_enabled else "disabled"
                logger.info(f"✅ MFA {status} for user: {data.get('email')}")

    async def _handle_user_logged_in(self, data: Dict, metadata: Dict):
        """Handle UserLoggedIn event"""
        user_id = data.get("id")
        if user_id:
            existing_user = await self.user_read_repo.get_by_id(user_id)
            if existing_user:
                # Update last login info
                from datetime import datetime

                existing_user["last_login_at"] = datetime.utcnow().isoformat()
                existing_user["last_login_ip"] = metadata.get("ip_address")
                await self.user_read_repo.upsert_user(existing_user)
                logger.info(f"✅ Login recorded for user: {data.get('email')}")

    async def _handle_password_changed(self, data: Dict):
        """Handle PasswordChanged event"""
        user_id = data.get("id")
        if user_id:
            existing_user = await self.user_read_repo.get_by_id(user_id)
            if existing_user:
                from datetime import datetime

                existing_user["password_changed_at"] = datetime.utcnow().isoformat()
                await self.user_read_repo.upsert_user(existing_user)
                logger.info(f"✅ Password change recorded for user: {data.get('email')}")


# Global instance
user_event_consumer = UserEventConsumer()
