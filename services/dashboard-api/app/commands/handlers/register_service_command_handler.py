import logging
from app.core.message_bus import CommandHandler
from app.schemas.commands.service_commands import RegisterServiceCommand
from app.schemas.registry import ServiceResponse

logger = logging.getLogger(__name__)


class RegisterServiceCommandHandler(
    CommandHandler[RegisterServiceCommand, ServiceResponse]
):
    def __init__(self):
        super().__init__()

    async def handle(self, command: RegisterServiceCommand) -> ServiceResponse:
        """
        Register service and save previous versions to history

        Raises:
            ValueError: If ServiceCreate.validator false
        """
        logger.info(f"Registering service: {command.name}")

        try:
            ...
        except Exception as e:
            logger.error(f"Failed to register service: {str(e)}")
