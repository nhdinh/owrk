"""
Database connections for Dashboard API
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Generator
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

# MySQL/SQLAlchemy
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=settings.DEBUG,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# MongoDB client
mongo_client: AsyncIOMotorClient = None
mongo_db = None


def get_db() -> Generator[Session, None, None]:
    """Get MySQL database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def connect_mongodb():
    """Connect to MongoDB"""
    global mongo_client, mongo_db
    try:
        mongo_client = AsyncIOMotorClient(settings.MONGODB_URL)
        mongo_db = mongo_client[settings.MONGODB_DATABASE]
        # Test connection
        await mongo_client.admin.command("ping")
        logger.info("✅ Connected to MongoDB")
    except Exception as e:
        logger.error(f"❌ Failed to connect to MongoDB: {e}")
        mongo_db = None


async def close_mongodb():
    """Close MongoDB connection"""
    global mongo_client
    if mongo_client:
        mongo_client.close()
        logger.info("✅ MongoDB connection closed")


def get_mongo_db():
    """Get MongoDB database"""
    return mongo_db
