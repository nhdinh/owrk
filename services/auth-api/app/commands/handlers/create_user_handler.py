"""
CreateUserHandler - Command handler for creating new users
Implements CQRS pattern with versioning and event publishing
"""

import logging
from sqlalchemy.orm import Session
from app.core.message_bus import CommandHandler
from app.schemas.commands.user_commands import CreateUserCommand
from app.models.user import User
from app.models.user_history import UserHistory
from app.core.security import hash_password
from app.core.rabbitmq import publish_event
from app.schemas.user_schema import UserResponse

logger = logging.getLogger(__name__)


class CreateUserHandler(CommandHandler[CreateUserCommand, UserResponse]):
    """
    Handler for CreateUserCommand
    Creates a new user with versioning support
    """

    def __init__(self):
        pass

    async def handle(self, command: CreateUserCommand, db: Session) -> UserResponse:
        """
        Create new user and save initial version to history

        Args:
            command: CreateUserCommand with user data
            db: Database session for this request

        Returns:
            UserResponse: Created user data

        Raises:
            ValueError: If email already exists
        """
        logger.info(f"Creating user: {command.email}")

        # Check if email already exists
        existing_user = db.query(User).filter(User.email == command.email).first()
        if existing_user:
            raise ValueError(f"Email {command.email} already registered")

        # Hash password
        hashed_password = hash_password(command.password)

        # Create new user
        new_user = User(
            email=command.email,
            full_name=command.full_name,
            hashed_password=hashed_password,
            user_type=command.user_type,
            role_id=command.role_id,
            department_id=command.department_id,
            phone_number=command.phone_number,
            position=command.position,
            version=1,  # Initial version
        )

        # Add to database
        db.add(new_user)
        db.flush()  # Flush to get the ID

        # Save initial version to history
        history_entry = UserHistory.from_user(
            user=new_user,
            changed_by=command.created_by,
            change_reason="User created",
            change_type="created",
        )
        db.add(history_entry)

        # Commit transaction
        db.commit()
        db.refresh(new_user)

        logger.info(
            f"User created successfully: ID={new_user.id}, Email={new_user.email}"
        )

        # Publish event to RabbitMQ for read model sync
        try:
            event_data = {
                "id": new_user.id,  # Fixed: changed from user_id to id
                "email": new_user.email,
                "full_name": new_user.full_name,
                "username": new_user.username,
                "phone_number": new_user.phone_number,
                "position": new_user.position,
                "user_type": new_user.user_type,
                "is_active": new_user.is_active,
                "is_superuser": new_user.is_superuser,
                "email_verified": new_user.email_verified,
                "mfa_enabled": new_user.mfa_enabled,
                "role_id": new_user.role_id,
                "department_id": new_user.department_id,
                "version": new_user.version,
                "created_at": (
                    new_user.created_at.isoformat() if new_user.created_at else None
                ),
                "updated_at": (
                    new_user.updated_at.isoformat() if new_user.updated_at else None
                ),
                "last_login_at": (
                    new_user.last_login_at.isoformat()
                    if new_user.last_login_at
                    else None
                ),
            }
            await publish_event("user.created", event_data)
            logger.info(f"Published UserCreated event for user {new_user.id}")
        except Exception as e:
            logger.error(f"Failed to publish UserCreated event: {str(e)}")
            # Don't fail the command if event publishing fails

        # Return response
        return UserResponse.from_orm(new_user)
