"""
Role Repository with role and permission operations
"""

from typing import Optional, List
from sqlalchemy.orm import Session

from app.repositories.base_repository import BaseRepository
from app.models.role import Role, Permission


class RoleRepository(BaseRepository[Role]):
    """
    Repository for Role entity
    """

    def __init__(self, db: Session):
        super().__init__(Role, db)

    def get_by_name(self, name: str) -> Optional[Role]:
        """Get role by name"""
        return self.db.query(Role).filter(Role.name == name).first()

    def get_active_roles(self, skip: int = 0, limit: int = 100) -> List[Role]:
        """Get all active roles"""
        return (
            self.db.query(Role)
            .filter(Role.is_active == True)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def add_permission_to_role(self, role_id: int, permission_id: int) -> bool:
        """Add permission to role"""
        role = self.get_by_id(role_id)
        if not role:
            return False

        permission = (
            self.db.query(Permission).filter(Permission.id == permission_id).first()
        )
        if not permission:
            return False

        if permission not in role.permissions:
            role.permissions.append(permission)
            self.db.flush()

        return True

    def remove_permission_from_role(self, role_id: int, permission_id: int) -> bool:
        """Remove permission from role"""
        role = self.get_by_id(role_id)
        if not role:
            return False

        permission = (
            self.db.query(Permission).filter(Permission.id == permission_id).first()
        )
        if not permission:
            return False

        if permission in role.permissions:
            role.permissions.remove(permission)
            self.db.flush()

        return True

    def get_role_permissions(self, role_id: int) -> List[Permission]:
        """Get all permissions for a role"""
        role = self.get_by_id(role_id)
        if not role:
            return []
        return role.permissions

    def role_has_permission(self, role_id: int, permission_name: str) -> bool:
        """Check if role has specific permission"""
        role = self.get_by_id(role_id)
        if not role:
            return False

        return any(p.name == permission_name for p in role.permissions)


class PermissionRepository(BaseRepository[Permission]):
    """
    Repository for Permission entity
    """

    def __init__(self, db: Session):
        super().__init__(Permission, db)

    def get_by_name(self, name: str) -> Optional[Permission]:
        """Get permission by name"""
        return self.db.query(Permission).filter(Permission.name == name).first()

    def get_by_resource_action(
        self, resource: str, action: str
    ) -> Optional[Permission]:
        """Get permission by resource and action"""
        return (
            self.db.query(Permission)
            .filter(Permission.resource == resource, Permission.action == action)
            .first()
        )

    def get_by_resource(self, resource: str) -> List[Permission]:
        """Get all permissions for a resource"""
        return self.db.query(Permission).filter(Permission.resource == resource).all()

    def get_by_action(self, action: str) -> List[Permission]:
        """Get all permissions for an action"""
        return self.db.query(Permission).filter(Permission.action == action).all()
