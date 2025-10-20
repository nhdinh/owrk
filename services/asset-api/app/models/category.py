"""
Asset Category Model
"""

from sqlalchemy import Column, String, Integer, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class AssetCategory(BaseModel):
    """Asset Category model"""

    __tablename__ = "asset_categories"
    __table_args__ = {"schema": "asset_db"}

    name = Column(String(255), nullable=False)
    code = Column(String(50), unique=True, nullable=False, index=True)
    parent_id = Column(Integer, ForeignKey("asset_db.asset_categories.id"), nullable=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    parent = relationship("AssetCategory", remote_side="AssetCategory.id", backref="children")
    assets = relationship("Asset", back_populates="category")

    def __repr__(self):
        return f"<AssetCategory(id={self.id}, code={self.code}, name={self.name})>"
