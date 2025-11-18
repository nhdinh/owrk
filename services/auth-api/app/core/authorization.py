"""
Authorization and Role Hierarchy Utilities
"""

from fastapi import HTTPException, status
from app.models.user import User


def check_role_hierarchy(current_user: User, target_user: User, operation: str = "modify") -> None:
    """
    Check if current_user has sufficient role hierarchy to perform operation on target_user.

    Args:
        current_user: The user performing the operation
        target_user: The user being operated on
        operation: Description of the operation (for error message)

    Raises:
        HTTPException: If current_user's role hierarchy is not higher than target_user's
    """
    # Superusers bypass hierarchy checks
    if current_user.is_superuser:
        return

    # Both users must have roles
    if not current_user.role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have a role assigned"
        )

    if not target_user.role:
        # Target user has no role, allow operation
        return

    current_level = current_user.role.hierarchy_level
    target_level = target_user.role.hierarchy_level

    # Current user must have HIGHER hierarchy level (strictly greater)
    if current_level <= target_level:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Insufficient privileges to {operation} user with role '{target_user.role.display_name}'. "
                   f"Your role hierarchy level ({current_level}) must be higher than theirs ({target_level})."
        )


def check_role_assignment_hierarchy(current_user: User, new_role_id: str, uow) -> None:
    """
    Check if current_user can assign a specific role to another user.
    Users can only assign roles with lower or equal hierarchy to their own.

    Args:
        current_user: The user performing the role assignment
        new_role_id: ID of the role being assigned
        uow: Unit of Work instance for database access

    Raises:
        HTTPException: If current_user cannot assign this role
    """
    # Superusers bypass hierarchy checks
    if current_user.is_superuser:
        return

    if not current_user.role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have a role assigned"
        )

    # Get the role being assigned
    new_role = uow.session.query(uow.roles.model).filter_by(id=new_role_id).first()
    if not new_role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )

    current_level = current_user.role.hierarchy_level
    new_role_level = new_role.hierarchy_level

    # Current user must have HIGHER hierarchy level than the role being assigned
    if current_level <= new_role_level:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Insufficient privileges to assign role '{new_role.display_name}'. "
                   f"Your role hierarchy level ({current_level}) must be higher than the role you're assigning ({new_role_level})."
        )
