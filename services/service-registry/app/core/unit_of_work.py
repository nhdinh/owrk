"""
Unit of Work pattern for managing database transactions
"""

from app.core.database import SessionLocal
from app.repositories.reg_service_repository import RegisteredServiceRepository


class UnitOfWork:
    """
    Unit of Work pattern implementation
    Manages database session and repositories
    """

    def __init__(self):
        self.session = SessionLocal()
        self.service = RegisteredServiceRepository(self.session)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.rollback()
        self.session.close()

    def commit(self):
        """Commit the current transaction"""
        self.session.commit()

    def rollback(self):
        """Rollback the current transaction"""
        self.session.rollback()

    def close(self):
        """Close the session"""
        self.session.close()
