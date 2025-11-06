"""
Service Repository
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from app.repositories.base_repository import BaseRepository
from app.models.reg_service import RegisteredService, RegisteredServiceStatus


class RegisteredServiceRepository(BaseRepository[RegisteredService]):
    """Repository for RegisteredService operations"""

    def __init__(self, session: Session):
        super().__init__(RegisteredService, session)

    def get_by_name(self, name: str) -> Optional[RegisteredService]:
        """Get service by code"""
        return (
            self.session.query(RegisteredService)
            .filter(RegisteredService.name == name)
            .first()
        )

    def get_healthy_categories(self) -> List[RegisteredService]:
        """Get all active categories"""
        return (
            self.session.query(RegisteredService)
            .filter(RegisteredService.status == RegisteredServiceStatus.HEALTHY)
            .all()
        )
