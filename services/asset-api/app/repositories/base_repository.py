"""
Base Repository - Generic CRUD operations
"""

from typing import TypeVar, Generic, Type, List, Optional, Any, Dict
from sqlalchemy.orm import Session
from app.models.base import BaseModel

ModelType = TypeVar("ModelType", bound=BaseModel)


class BaseRepository(Generic[ModelType]):
    """
    Base repository with common CRUD operations
    """

    def __init__(self, model: Type[ModelType], session: Session):
        self.model = model
        self.session = session

    def get_by_id(self, id: int) -> Optional[ModelType]:
        """Get entity by ID"""
        return self.session.query(self.model).filter(self.model.id == id).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """Get all entities with pagination"""
        return self.session.query(self.model).offset(skip).limit(limit).all()

    def create(self, entity: ModelType) -> ModelType:
        """Create new entity"""
        self.session.add(entity)
        self.session.flush()
        self.session.refresh(entity)
        return entity

    def update(self, entity: ModelType) -> ModelType:
        """Update existing entity"""
        self.session.merge(entity)
        self.session.flush()
        self.session.refresh(entity)
        return entity

    def delete(self, id: int) -> bool:
        """Delete entity by ID"""
        entity = self.get_by_id(id)
        if entity:
            self.session.delete(entity)
            self.session.flush()
            return True
        return False

    def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count entities with optional filters"""
        query = self.session.query(self.model)
        if filters:
            for key, value in filters.items():
                if hasattr(self.model, key):
                    query = query.filter(getattr(self.model, key) == value)
        return query.count()

    def exists(self, filters: Dict[str, Any]) -> bool:
        """Check if entity exists with given filters"""
        query = self.session.query(self.model)
        for key, value in filters.items():
            if hasattr(self.model, key):
                query = query.filter(getattr(self.model, key) == value)
        return query.first() is not None
