"""
Authentication Pydantic Schemas
"""

from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class LoginRequest(BaseModel):
    """Schema for login request (Step 1)"""

    email: EmailStr
    password: str
    remember_me: bool = False


class LoginResponse(BaseModel):
    """Schema for login response (Step 1) - Returns temp token for MFA"""

    temp_token: str
    requires_mfa: bool
    message: str


class MFAVerifyRequest(BaseModel):
    """Schema for MFA verification (Step 2)"""

    temp_token: str
    otp_code: str


class TokenResponse(BaseModel):
    """Schema for final token response (Step 2 complete)"""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: dict


class RefreshTokenRequest(BaseModel):
    """Schema for refresh token request"""

    refresh_token: str


class MFASetupResponse(BaseModel):
    """Schema for MFA setup response"""

    secret: str
    qr_code_url: str
    backup_codes: list[str]


class MFAEnableRequest(BaseModel):
    """Schema for enabling MFA"""

    otp_code: str


class MFADisableRequest(BaseModel):
    """Schema for disabling MFA"""

    password: str
    otp_code: Optional[str] = None
    backup_code: Optional[str] = None


class ADSyncRequest(BaseModel):
    """Schema for Active Directory sync request"""

    username: str
    sync_all: bool = False


class LogoutRequest(BaseModel):
    """Schema for logout request"""

    refresh_token: Optional[str] = None


class TokenPayload(BaseModel):
    """Schema for JWT token payload"""

    sub: int  # user_id
    email: str
    type: str  # 'access' or 'refresh' or 'temp'
    exp: datetime
    iat: datetime


class RoleResponse(BaseModel):
    """Schema for role response"""

    id: int
    name: str
    display_name: str
    description: Optional[str]
    is_active: bool

    class Config:
        from_attributes = True


class PermissionResponse(BaseModel):
    """Schema for permission response"""

    id: int
    name: str
    resource: str
    action: str
    description: Optional[str]

    class Config:
        from_attributes = True
