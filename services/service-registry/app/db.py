"""
MongoDB connection for CQRS Read Model
"""

from motor.motor_asyncio import AsyncIOMotorClient
from .config import settings

# Global MongoDB client
mongo_client: AsyncIOMotorClient = None


async def connect_mongo():
    """
    Connect to MongoDB on application startup
    """
    global mongo_client
    mongo_client = AsyncIOMotorClient(settings.MONGODB_URL)


async def close_mongo():
    """
    Close MongoDB connection on application shutdown
    """
    global mongo_client
    if mongo_client:
        mongo_client.close()


def get_mongo_db():
    """
    Get MongoDB database instance
    """
    return mongo_client[settings.MONGODB_DB_NAME]
