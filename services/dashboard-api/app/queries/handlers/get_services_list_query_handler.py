import logging
from typing import Dict
from app.core.message_bus import QueryHandler
from app.read_repositories import ServiceReadRepository

from app.schemas.queries import GetServicesListQuery

logger = logging.getLogger(__name__)


class GetServicesListQueryHandler(QueryHandler[GetServicesListQuery, Dict]):
    """
    Handler for GetServicesListQuery
    """

    def __init__(self, service_read_repo: ServiceReadRepository) -> None:
        self.service_read_repo = service_read_repo

    async def handle(self, query: GetServicesListQuery) -> Dict:
        services = await self.service_read_repo.find_all()

        return {"services": services, "total": len(services)}
