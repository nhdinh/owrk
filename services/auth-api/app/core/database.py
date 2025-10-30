"""
PostgreSQL database connection and session management
"""

import logging
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

from app.core.config import settings

# Set the SQLAlchemy logger level to ERROR
logging.getLogger("sqlalchemy").setLevel(logging.ERROR)

# Create SQLAlchemy engine for MySQL
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=20,
    max_overflow=40,
    pool_recycle=3600,  # Recycle connections after 1 hour
    echo=settings.ENVIRONMENT == "debug",
    connect_args={"charset": "utf8mb4"},
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for models
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency to get database session
    Use this in FastAPI routes with Depends(get_db)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
