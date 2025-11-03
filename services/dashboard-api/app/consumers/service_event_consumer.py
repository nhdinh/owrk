import logging
from typing import Dict

from app.core.database import get_mongo_db
from app.read_repositories import ServiceReadRepository

logger = logging.getLogger(__name__)


class ServiceEventConsumer:
    """
    Consumer for registry-related events
    """

    def __init__(self) -> None:
        self.service_read_repo = None

    async def initialize(self):
        """Initialize repositories"""
        mongo_db = get_mongo_db()
        self.service_read_repo = ServiceReadRepository(mongo_db)
        await self.service_read_repo.create_indexes()
        logger.info("✅ ServiceEventConsumer initialized")

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
            if event_type == "service.registered":
                await self._handle_service_registered(event_data)
            elif event_type == "service.deregistered":
                await self._handle_service_deregistered(event_data)

                # TODO: implements services event
        except Exception as e:
            logger.error(f"❌ Error processing event {event_type}: {str(e)}")
            # In production, you might want to:
            # - Send to dead letter queue
            # - Retry with exponential backoff
            # - Alert monitoring system
            raise

    async def _handle_service_registered(self, service_data: Dict):
        """Handle ServiceRegistered event"""
        await self.service_read_repo.register_service(service_data)
        logger.info(f"✅ Service created in read model: {service_data.get('name')}")

    async def _handle_service_deregistered(self, service_data: Dict):
        service_id = service_data.get("service_id")
        if service_id:
            await self.service_read_repo.deregister_service(service_id)
        logger.info(f"✅ Service created in read model: {service_data.get('name')}")


service_event_consumer = ServiceEventConsumer()
