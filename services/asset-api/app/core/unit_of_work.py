"""
Unit of Work pattern for managing database transactions
"""

from app.core.database import SessionLocal
from app.repositories.asset_repository import AssetRepository
from app.repositories.category_repository import CategoryRepository
from app.repositories.assignment_repository import AssignmentRepository
from app.repositories.attachment_repository import AttachmentRepository
from app.repositories.depreciation_repository import DepreciationRepository


class UnitOfWork:
    """
    Unit of Work pattern implementation
    Manages database session and repositories
    """

    def __init__(self):
        self.session = SessionLocal()
        self.assets = AssetRepository(self.session)
        self.categories = CategoryRepository(self.session)
        self.assignments = AssignmentRepository(self.session)
        self.attachments = AttachmentRepository(self.session)
        self.depreciations = DepreciationRepository(self.session)

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
