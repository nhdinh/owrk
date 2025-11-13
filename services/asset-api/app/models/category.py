"""
Asset Category Model
"""

from sqlalchemy import Column, String, Boolean, Text, ForeignKey, event
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
from app.core.utils import generate_slug


class AssetCategory(BaseModel):
    """Asset Category model"""

    __tablename__ = "asset_categories"
    __table_args__ = {"schema": "asset_db"}

    name = Column(String(255), nullable=False)
    code = Column(String(50), unique=True, nullable=False, index=True)
    parent_id = Column(
        String(32), ForeignKey("asset_db.asset_categories.id"), nullable=True
    )
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    parent = relationship(
        "AssetCategory", remote_side="AssetCategory.id", backref="children"
    )
    assets = relationship("Asset", back_populates="category")

    def __repr__(self):
        return f"<AssetCategory(id={self.id}, code={self.code}, name={self.name})>"


# Event listener to auto-generate slug from code or name before insert
@event.listens_for(AssetCategory, "before_insert")
def generate_category_slug(mapper, connection, target):
    """Auto-generate slug from code (preferred) or name if not provided"""
    if not target.slug:
        # Use code if available (cleaner), otherwise use name
        base_text = target.code if target.code else target.name
        target.slug = generate_slug(base_text)
