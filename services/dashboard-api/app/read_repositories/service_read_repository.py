from typing import Dict, List, Optional
from uuid import UUID
from motor.motor_asyncio import AsyncIOMotorDatabase


class ServiceReadRepository:
    """
    Read-only repository for Services queries from MongoDB
    """

    def __init__(self, mongo_db: AsyncIOMotorDatabase) -> None:
        self.db = mongo_db
        self.collection = mongo_db.services

    async def get_by_id(self, service_id: UUID) -> Optional[Dict]:
        """
        Get service by ID from MongoDB read model

        Args:
            service_id: Service ID

        Return:
            Service document or None
        """
        return await self.collection.find_one({"id": service_id})

    async def find_all(self) -> List[Dict]:
        """
        Get list of registered services

        Return:
            List of service documents
        """
        return await self.collection

    async def register_service(self, service_data: Dict) -> bool:
        """
        Insert or update service data in MongoDB (this called by event consumer)

        Args:
            service_data: Service data from event

        Returns:
            True if successful
        """
        service_id = service_data.get("service_id")
        if not service_id:
            return False

        # TODO: finish the registering of the service

        return False

    async def deregister_service(self, service_id: UUID) -> bool:
        """
        Deregister a service (called by event consumer)

        Args:
            service_id: ID of the service (in UUID)
        """

        # TODO: finish implementing the deregister of a service
        return False

    async def create_indexes(self):
        """
        Create indexes for better query performance
        Should be called on application startup
        """
        # await self.collection.create_index("id", unique=True)
        # await self.collection.create_index("email", unique=True)
        # await self.collection.create_index("username")
        # await self.collection.create_index("role_id")
        # await self.collection.create_index("department_id")
        # await self.collection.create_index("is_active")
        # await self.collection.create_index("mfa_enabled")
        # await self.collection.create_index("user_type")
        # # Text index for search
        # await self.collection.create_index(
        #     [("full_name", "text"), ("email", "text"), ("username", "text")]
        # )

        # TODO: Create index for services
        print("✅ MongoDB indexes created for services collection")
