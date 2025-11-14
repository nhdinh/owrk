"""
Base model with common fields using UUID and slug
"""

from sqlalchemy import Column, String, DateTime, Index
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declared_attr
from app.core.database import Base
from app.core.utils import generate_uuid


class BaseModel(Base):
    """
    Base model with UUID primary key and slug for URL-friendly identifiers
    """

    __abstract__ = True

    # UUID as primary key (stored as CHAR(32) without dashes for efficiency)
    id = Column(
        String(36),
        primary_key=True,
        index=True,
        default=generate_uuid,
        nullable=False
    )

    # Slug for URL-friendly identifiers (must be unique per table)
    slug = Column(String(100), unique=True, index=True, nullable=False)

    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    @declared_attr
    def __table_args__(cls):
        """Add composite index on slug for faster lookups"""
        return (
            Index(f'ix_{cls.__tablename__}_slug', 'slug'),
        )
