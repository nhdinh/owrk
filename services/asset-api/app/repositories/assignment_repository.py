"""
Assignment Repository
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.assignment import AssetAssignment, AssignmentStatus
from app.repositories.base_repository import BaseRepository


class AssignmentRepository(BaseRepository[AssetAssignment]):
    """Repository for AssetAssignment operations"""

    def __init__(self, session: Session):
        super().__init__(AssetAssignment, session)

    def get_asset_history(self, asset_id: int) -> List[AssetAssignment]:
        """Get assignment history for an asset"""
        return self.session.query(AssetAssignment).filter(
            AssetAssignment.asset_id == asset_id
        ).order_by(AssetAssignment.assigned_date.desc()).all()

    def get_user_assignments(self, user_id: int) -> List[AssetAssignment]:
        """Get all assignments for a user"""
        return self.session.query(AssetAssignment).filter(
            AssetAssignment.user_id == user_id
        ).order_by(AssetAssignment.assigned_date.desc()).all()

    def get_active_assignment(self, asset_id: int) -> Optional[AssetAssignment]:
        """Get current active assignment for an asset"""
        return self.session.query(AssetAssignment).filter(
            AssetAssignment.asset_id == asset_id,
            AssetAssignment.status == AssignmentStatus.ACTIVE
        ).first()

    def get_active_user_assignments(self, user_id: int) -> List[AssetAssignment]:
        """Get active assignments for a user"""
        return self.session.query(AssetAssignment).filter(
            AssetAssignment.user_id == user_id,
            AssetAssignment.status == AssignmentStatus.ACTIVE
        ).all()

    def mark_as_returned(self, assignment_id: int) -> bool:
        """Mark assignment as returned"""
        assignment = self.get_by_id(assignment_id)
        if assignment:
            assignment.status = AssignmentStatus.RETURNED
            self.session.flush()
            return True
        return False
