"""
UpdateUserHandler - Command handler for updating users
Implements versioning by incrementing version and saving history
"""

import logging
from sqlalchemy.orm import Session
from app.core.message_bus import CommandHandler
from app.schemas.commands.user_commands import UpdateUserCommand
from app.models.user import User
from app.models.user_history import UserHistory
from app.core.rabbitmq import publish_event
from app.schemas.user_schema import UserResponse

logger = logging.getLogger(__name__)


class UpdateUserHandler(CommandHandler[UpdateUserCommand, UserResponse]):
    """
    Handler for UpdateUserCommand
    Updates user and saves version to history
    """

    def __init__(self):
        pass

    async def handle(self, command: UpdateUserCommand, db: Session) -> UserResponse:
        """
        Update user and increment version

        Args:
            command: UpdateUserCommand with updated data

        Returns:
            UserResponse: Updated user data

        Raises:
            ValueError: If user not found
        """
        logger.info(f"Updating user ID: {command.user_id}")

        # Get existing user
        user = db.query(User).filter(User.id == command.user_id).first()
        if not user:
            raise ValueError(f"User with ID {command.user_id} not found")

        # Save current version to history BEFORE updating
        history_entry = UserHistory.from_user(
            user=user,
            changed_by=command.updated_by,
            change_reason="User updated",
            change_type="updated",
        )
        db.add(history_entry)

        # Update user fields
        if command.full_name is not None:
            user.full_name = command.full_name
        if command.phone_number is not None:
            user.phone_number = command.phone_number
        if command.position is not None:
            user.position = command.position
        if command.department_id is not None:
            user.department_id = command.department_id
        if command.role_id is not None:
            user.role_id = command.role_id

        # Increment version
        user.version += 1

        # Commit transaction
        db.commit()
        db.refresh(user)

        logger.info(f"User updated successfully: ID={user.id}, Version={user.version}")

        # Publish event to RabbitMQ
        try:
            event_data = {
                "id": user.id,  # Fixed: changed from user_id to id
                "email": user.email,
                "full_name": user.full_name,
                "username": user.username,
                "phone_number": user.phone_number,
                "position": user.position,
                "user_type": user.user_type,
                "is_active": user.is_active,
                "is_superuser": user.is_superuser,
                "email_verified": user.email_verified,
                "mfa_enabled": user.mfa_enabled,
                "role_id": user.role_id,
                "department_id": user.department_id,
                "version": user.version,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "updated_at": user.updated_at.isoformat() if user.updated_at else None,
                "last_login_at": (
                    user.last_login_at.isoformat() if user.last_login_at else None
                ),
            }
            await publish_event("user.updated", event_data)
            logger.info(f"Published UserUpdated event for user {user.id}")
        except Exception as e:
            logger.error(f"Failed to publish UserUpdated event: {str(e)}")

        return UserResponse.from_orm(user)
