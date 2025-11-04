"""DeleteUserHandler - Soft delete user"""

import logging
from sqlalchemy.orm import Session
from app.core.message_bus import CommandHandler
from app.schemas.commands.user_commands import DeleteUserCommand
from app.models.user import User
from app.models.user_history import UserHistory
from app.core.rabbitmq import publish_event

logger = logging.getLogger(__name__)


class DeleteUserHandler(CommandHandler[DeleteUserCommand, bool]):
    def __init__(self):
        pass

    async def handle(self, command: DeleteUserCommand, db: Session) -> bool:
        user = db.query(User).filter(User.id == command.user_id).first()
        if not user:
            raise ValueError(f"User with ID {command.user_id} not found")

        # Save history before deleting
        history_entry = UserHistory.from_user(
            user=user,
            changed_by=command.deleted_by,
            change_reason="User deleted",
            change_type="deleted",
        )
        db.add(history_entry)

        # Soft delete (deactivate)
        user.is_active = False
        user.version += 1

        db.commit()

        # Publish event
        try:
            event_data = {"id": user.id, "email": user.email}
            await publish_event("user.deleted", event_data)
        except Exception as e:
            logger.error(f"Failed to publish UserDeleted event: {str(e)}")

        return True
