"""
Attachment Repository
"""

from typing import List
from sqlalchemy.orm import Session
from app.models.attachment import AssetAttachment, FileType
from app.repositories.base_repository import BaseRepository


class AttachmentRepository(BaseRepository[AssetAttachment]):
    """Repository for AssetAttachment operations"""

    def __init__(self, session: Session):
        super().__init__(AssetAttachment, session)

    def get_asset_attachments(self, asset_id: int) -> List[AssetAttachment]:
        """Get all attachments for an asset"""
        return self.session.query(AssetAttachment).filter(
            AssetAttachment.asset_id == asset_id
        ).order_by(AssetAttachment.created_at.desc()).all()

    def get_attachments_by_type(self, asset_id: int, file_type: FileType) -> List[AssetAttachment]:
        """Get attachments of specific type for an asset"""
        return self.session.query(AssetAttachment).filter(
            AssetAttachment.asset_id == asset_id,
            AssetAttachment.file_type == file_type
        ).all()

    def delete_asset_attachments(self, asset_id: int) -> int:
        """Delete all attachments for an asset"""
        count = self.session.query(AssetAttachment).filter(
            AssetAttachment.asset_id == asset_id
        ).delete()
        self.session.flush()
        return count
