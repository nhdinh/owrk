"""ActivateUserHandler - Activate user account"""
import logging
from sqlalchemy.orm import Session
from app.core.message_bus import CommandHandler
from app.schemas.commands.user_commands import ActivateUserCommand
from app.models.user import User
from app.models.user_history import UserHistory
from app.core.rabbitmq import publish_event
from app.schemas.user_schema import UserResponse

logger = logging.getLogger(__name__)


class ActivateUserHandler(CommandHandler[ActivateUserCommand, UserResponse]):
    def __init__(self):
        pass

    async def handle(self, command: ActivateUserCommand, db: Session) -> UserResponse:
        user = db.query(User).filter(User.id == command.user_id).first()
        if not user:
            raise ValueError(f"User with ID {command.user_id} not found")

        # Save history
        history_entry = UserHistory.from_user(
            user=user,
            changed_by=command.activated_by,
            change_reason="User activated",
            change_type="activated"
        )
        db.add(history_entry)

        user.is_active = True
        user.version += 1

        db.commit()
        db.refresh(user)

        # Publish event
        try:
            event_data = {"id": user.id, "email": user.email, "is_active": True}
            await publish_event("user.activated", event_data)
        except Exception as e:
            logger.error(f"Failed to publish UserActivated event: {str(e)}")

        return UserResponse.from_orm(user)
