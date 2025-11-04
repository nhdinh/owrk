"""User Command DTOs"""

from dataclasses import dataclass
from typing import Optional
from app.core.message_bus import Command


@dataclass
class CreateUserCommand(Command):
    """Command to create a new user"""

    email: str
    full_name: str
    password: str
    role_id: Optional[int] = None
    department_id: Optional[int] = None
    phone_number: Optional[str] = None
    position: Optional[str] = None
    user_type: str = "local"
    created_by: Optional[int] = None  # User ID who created this user


@dataclass
class UpdateUserCommand(Command):
    """Command to update user information"""

    user_id: int
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    position: Optional[str] = None
    department_id: Optional[int] = None
    role_id: Optional[int] = None
    updated_by: Optional[int] = None  # User ID who updated


@dataclass
class DeleteUserCommand(Command):
    """Command to delete a user (soft delete)"""

    user_id: int
    deleted_by: Optional[int] = None  # User ID who deleted


@dataclass
class ActivateUserCommand(Command):
    """Command to activate a user"""

    user_id: int
    activated_by: Optional[int] = None


@dataclass
class DeactivateUserCommand(Command):
    """Command to deactivate a user"""

    user_id: int
    deactivated_by: Optional[int] = None


@dataclass
class ChangePasswordCommand(Command):
    """Command to change user password"""

    user_id: int
    current_password: str
    new_password: str


@dataclass
class ResetPasswordCommand(Command):
    """Command to reset user password"""

    user_id: int
    new_password: str
    reset_by: Optional[int] = None
