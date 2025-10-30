"""Authentication Command DTOs"""
from dataclasses import dataclass
from typing import Optional
from app.core.message_bus import Command


@dataclass
class LoginCommand(Command):
    """Command for user login (Step 1)"""
    email: str
    password: str
    ip_address: str


@dataclass
class VerifyOTPCommand(Command):
    """Command to verify OTP (Step 2)"""
    temp_token: str
    otp_code: str
    ip_address: str
    user_agent: str


@dataclass
class RefreshTokenCommand(Command):
    """Command to refresh access token"""
    refresh_token: str


@dataclass
class LogoutCommand(Command):
    """Command to logout user"""
    user_id: int
    refresh_token: Optional[str] = None


@dataclass
class EnableMFACommand(Command):
    """Command to enable MFA for user"""
    user_id: int
    otp_code: str


@dataclass
class DisableMFACommand(Command):
    """Command to disable MFA for user"""
    user_id: int
