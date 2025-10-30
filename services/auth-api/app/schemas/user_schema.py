"""
User Pydantic Schemas
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    """Base User schema"""

    email: EmailStr
    full_name: str = Field(..., min_length=1, max_length=255)
    username: Optional[str] = Field(None, min_length=3, max_length=100)
    phone_number: Optional[str] = None
    position: Optional[str] = None
    address: Optional[str] = None
    department_id: Optional[int] = None


class UserCreate(UserBase):
    """Schema for creating a new user"""

    password: str = Field(..., min_length=8)
    role_id: Optional[int] = None
    user_type: str = Field(default="local", pattern="^(local|active_directory)$")

    @validator("password")
    def validate_password(cls, v):
        """Validate password strength"""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not any(char.isupper() for char in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(char.islower() for char in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(char.isdigit() for char in v):
            raise ValueError("Password must contain at least one digit")
        return v


class UserUpdate(BaseModel):
    """Schema for updating user"""

    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, min_length=1, max_length=255)
    username: Optional[str] = Field(None, min_length=3, max_length=100)
    phone_number: Optional[str] = None
    position: Optional[str] = None
    address: Optional[str] = None
    department_id: Optional[int] = None
    is_active: Optional[bool] = None
    role_id: Optional[int] = None


class UserResponse(UserBase):
    """Schema for user response"""

    id: int
    user_type: str
    is_active: bool
    is_superuser: bool
    email_verified: bool
    mfa_enabled: bool
    role_id: Optional[int]
    created_at: datetime
    updated_at: Optional[datetime]
    last_login_at: Optional[datetime]

    class Config:
        from_attributes = True


class UserInDB(UserResponse):
    """Schema for user in database (includes sensitive data)"""

    hashed_password: Optional[str]
    mfa_secret: Optional[str]
    failed_login_attempts: int
    locked_until: Optional[datetime]

    class Config:
        from_attributes = True


class ChangePasswordRequest(BaseModel):
    """Schema for changing password"""

    current_password: str
    new_password: str = Field(..., min_length=8)

    @validator("new_password")
    def validate_password(cls, v):
        """Validate password strength"""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not any(char.isupper() for char in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(char.islower() for char in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(char.isdigit() for char in v):
            raise ValueError("Password must contain at least one digit")
        return v


class PasswordResetRequest(BaseModel):
    """Schema for requesting password reset"""

    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Schema for confirming password reset"""

    token: str
    new_password: str = Field(..., min_length=8)

    @validator("new_password")
    def validate_password(cls, v):
        """Validate password strength"""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not any(char.isupper() for char in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(char.islower() for char in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(char.isdigit() for char in v):
            raise ValueError("Password must contain at least one digit")
        return v
