"""
Role Model
"""

from sqlalchemy import Column, String, Text, Boolean, Table, ForeignKey, Integer, JSON, event
from sqlalchemy.orm import relationship
from app.models.base import Base
from app.core.utils import generate_slug


# Association table for many-to-many relationship between roles and permissions
role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column("role_id", String(36), ForeignKey("auth_db.roles.id"), primary_key=True),
    Column("permission_id", String(36), ForeignKey("auth_db.permissions.id"), primary_key=True),
    schema="auth_db",
)


class Role(Base):
    """
    Role model for RBAC (Role-Based Access Control)
    """

    __tablename__ = "roles"
    __table_args__ = {"schema": "auth_db"}

    # Basic Information
    name = Column(String(50), unique=True, nullable=False, index=True)
    display_name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)

    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    is_system_role = Column(Boolean, default=False, nullable=False)  # Cannot be deleted

    # Hierarchy (for role-based access control)
    # Higher level = more privileged. Super Admin: 100, Admin: 90, Manager: 50, User: 10
    hierarchy_level = Column(Integer, default=10, nullable=False)

    # Versioning (for history tracking)
    version = Column(Integer, default=1, nullable=False)  # Incremented on each update

    # Relationships
    users = relationship("User", back_populates="role")
    permissions = relationship(
        "Permission", secondary=role_permissions, back_populates="roles"
    )
    history = relationship(
        "RoleHistory",
        backref="role",
        lazy="dynamic",
        order_by="RoleHistory.version.desc()",
    )

    # Timestamps inherited from Base

    def __repr__(self):
        return f"<Role(id={self.id}, name='{self.name}')>"


class Permission(Base):
    """
    Permission model for fine-grained access control
    """

    __tablename__ = "permissions"
    __table_args__ = {"schema": "auth_db"}

    # Basic Information
    name = Column(String(100), unique=True, nullable=False, index=True)
    resource = Column(String(50), nullable=False)  # e.g., 'asset', 'user', 'report'
    action = Column(
        String(50), nullable=False
    )  # e.g., 'create', 'read', 'update', 'delete'
    description = Column(Text, nullable=True)

    # Service ownership (which microservice owns this permission)
    service = Column(String(50), nullable=True)  # e.g., 'auth-api', 'asset-api', 'procurement-api'

    # Relationships
    roles = relationship(
        "Role", secondary=role_permissions, back_populates="permissions"
    )

    # Timestamps inherited from Base

    def __repr__(self):
        return f"<Permission(id={self.id}, name='{self.name}')>"


# Event listeners for auto-generating slugs
@event.listens_for(Role, "before_insert")
def generate_role_slug(mapper, connection, target):
    """Auto-generate slug from name if not provided"""
    if not target.slug:
        target.slug = generate_slug(target.name)


@event.listens_for(Permission, "before_insert")
def generate_permission_slug(mapper, connection, target):
    """Auto-generate slug from name if not provided"""
    if not target.slug:
        # Use format: resource-action (e.g., "asset-create", "user-read")
        target.slug = generate_slug(f"{target.resource}-{target.action}")
