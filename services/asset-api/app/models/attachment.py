"""
Asset Attachment Model
"""

from sqlalchemy import Column, String, BigInteger, ForeignKey, Enum as SQLEnum, event
from sqlalchemy.orm import relationship
import enum

from app.models.base import BaseModel
from app.core.utils import generate_slug


class FileType(str, enum.Enum):
    """File type enumeration"""

    INVOICE = "INVOICE"
    WARRANTY = "WARRANTY"
    PHOTO = "PHOTO"
    DOCUMENT = "DOCUMENT"


class AssetAttachment(BaseModel):
    """Asset Attachment model - file attachments for assets"""

    __tablename__ = "asset_attachments"
    __table_args__ = {"schema": "asset_db"}

    asset_id = Column(
        String(32),
        ForeignKey("asset_db.assets.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    file_name = Column(String(255), nullable=False)
    file_type = Column(SQLEnum(FileType), nullable=False, index=True)
    file_url = Column(String(500), nullable=False)
    file_size = Column(BigInteger, nullable=True)
    uploaded_by = Column(String(32), nullable=False)  # User UUID

    # Relationships
    asset = relationship("Asset", back_populates="attachments")

    def __repr__(self):
        return f"<AssetAttachment(id={self.id}, asset_id={self.asset_id}, file_name={self.file_name}, type={self.file_type})>"


# Event listener to auto-generate slug from file_name
@event.listens_for(AssetAttachment, "before_insert")
def generate_attachment_slug(mapper, connection, target):
    """Auto-generate slug from file_name if not provided"""
    if not target.slug:
        # Use file name without extension for slug
        base_name = target.file_name.rsplit('.', 1)[0] if '.' in target.file_name else target.file_name
        asset_short = target.asset_id[:8] if target.asset_id else "unknown"
        target.slug = generate_slug(f"{asset_short}-{base_name}")
