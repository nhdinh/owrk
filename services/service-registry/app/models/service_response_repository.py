from typing import Dict, List
from motor.motor_asyncio import AsyncIOMotorDatabase


class ServiceResponseRepository:
    """
    Read-only repository for ServiceResponse queries from MongoDB
    """

    def __init__(self, mongo_db: AsyncIOMotorDatabase) -> None:
        self.db = mongo_db
        self.collection = mongo_db.service_response_logs

    async def get_by_service_name(self, service_name: str) -> List[Dict]:
        cursor = self.collection.find({"service_name": service_name})
        return await cursor.to_list()

    async def upsert_log(self, response_log: Dict) -> bool:
        """
        Insert log in MongoDB
        """

        await self.collection.update_one({"$set"})
        return True

    async def prune(self) -> bool:
        return False
