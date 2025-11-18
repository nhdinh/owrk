"""
Base Repository with generic CRUD operations
"""

from typing import TypeVar, Generic, Type, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.base import Base

T = TypeVar("T", bound=Base)


class BaseRepository(Generic[T]):
    """
    Generic Repository providing CRUD operations
    """

    def __init__(self, model: Type[T], db: Session):
        self.model = model
        self.db = db

    def get_by_id(self, id: str) -> Optional[T]:
        """Get entity by ID"""
        return self.db.query(self.model).filter(self.model.id == id).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        """Get all entities with pagination"""
        return self.db.query(self.model).offset(skip).limit(limit).all()

    def get_by_filter(self, **filters) -> List[T]:
        """Get entities by filters"""
        query = self.db.query(self.model)
        for key, value in filters.items():
            if hasattr(self.model, key):
                query = query.filter(getattr(self.model, key) == value)
        return query.all()

    def get_one_by_filter(self, **filters) -> Optional[T]:
        """Get single entity by filters"""
        query = self.db.query(self.model)
        for key, value in filters.items():
            if hasattr(self.model, key):
                query = query.filter(getattr(self.model, key) == value)
        return query.first()

    def create(self, entity: T) -> T:
        """Create new entity"""
        self.db.add(entity)
        self.db.flush()
        self.db.refresh(entity)
        return entity

    def update(self, entity: T) -> T:
        """Update entity"""
        self.db.merge(entity)
        self.db.flush()
        self.db.refresh(entity)
        return entity

    def delete(self, id: str) -> bool:
        """Delete entity by ID"""
        entity = self.get_by_id(id)
        if entity:
            self.db.delete(entity)
            self.db.flush()
            return True
        return False

    def exists(self, id: str) -> bool:
        """Check if entity exists"""
        return (
            self.db.query(self.model.id).filter(self.model.id == id).scalar()
            is not None
        )

    def count(self, **filters) -> int:
        """Count entities"""
        query = self.db.query(self.model)
        for key, value in filters.items():
            if hasattr(self.model, key):
                query = query.filter(getattr(self.model, key) == value)
        return query.count()
