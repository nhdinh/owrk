from uuid import UUID
from app.core.message_bus import Query


class GetServicesListQuery(Query):
    service_id: UUID
