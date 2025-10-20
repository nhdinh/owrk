"""
Asset Attachment Model
"""

from sqlalchemy import Column, String, Integer, BigInteger, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
import enum

from app.models.base import BaseModel


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

    asset_id = Column(Integer, ForeignKey("asset_db.assets.id", ondelete="CASCADE"), nullable=False, index=True)
    file_name = Column(String(255), nullable=False)
    file_type = Column(SQLEnum(FileType), nullable=False, index=True)
    file_url = Column(String(500), nullable=False)
    file_size = Column(BigInteger, nullable=True)
    uploaded_by = Column(Integer, nullable=False)

    # Relationships
    asset = relationship("Asset", back_populates="attachments")

    def __repr__(self):
        return f"<AssetAttachment(id={self.id}, asset_id={self.asset_id}, file_name={self.file_name}, type={self.file_type})>"
