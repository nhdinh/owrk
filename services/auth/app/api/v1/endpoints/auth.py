"""
Authentication API Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from typing import Optional

from app.schemas.auth_schema import (
    LoginRequest, LoginResponse,
    MFAVerifyRequest, TokenResponse,
    RefreshTokenRequest, LogoutRequest,
    MFASetupResponse, MFAEnableRequest, MFADisableRequest,
    ADSyncRequest
)
from app.schemas.user_schema import PasswordResetRequest, PasswordResetConfirm
from app.services.auth_service import AuthService
from app.core.dependencies import get_current_user, require_role
from app.models.user import User


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=LoginResponse)
async def login_step1(
    request: LoginRequest,
    http_request: Request
):
    """
    Step 1: Login with email and password
    Returns temp token for MFA verification
    """
    try:
        ip_address = http_request.client.host if http_request.client else "unknown"
        result = await AuthService.login_step1(
            email=request.email,
            password=request.password,
            ip_address=ip_address
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Login failed")


@router.post("/verify-otp", response_model=TokenResponse)
async def verify_otp(
    request: MFAVerifyRequest,
    http_request: Request
):
    """
    Step 2: Verify OTP code and get final tokens
    """
    try:
        ip_address = http_request.client.host if http_request.client else "unknown"
        user_agent = http_request.headers.get("user-agent", "unknown")

        result = await AuthService.login_step2_mfa(
            temp_token=request.temp_token,
            otp_code=request.otp_code,
            ip_address=ip_address,
            user_agent=user_agent
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="OTP verification failed")


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(request: RefreshTokenRequest):
    """
    Refresh access token using refresh token
    """
    try:
        result = await AuthService.refresh_access_token(request.refresh_token)
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Token refresh failed")


@router.post("/logout")
async def logout(
    request: LogoutRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Logout user by revoking refresh token
    """
    try:
        if request.refresh_token:
            await AuthService.logout(request.refresh_token)
        return {"message": "Logged out successfully"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Logout failed")


# ==================== MFA ENDPOINTS ====================

@router.get("/mfa/setup", response_model=MFASetupResponse)
async def setup_mfa(current_user: User = Depends(get_current_user)):
    """
    Setup MFA for current user
    Returns QR code and backup codes
    """
    try:
        result = await AuthService.setup_mfa(current_user.id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="MFA setup failed")


@router.post("/mfa/enable")
async def enable_mfa(
    request: MFAEnableRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Enable MFA after verifying OTP code
    """
    try:
        await AuthService.enable_mfa(current_user.id, request.otp_code)
        return {"message": "MFA enabled successfully"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="MFA enable failed")


@router.post("/mfa/disable")
async def disable_mfa(
    request: MFADisableRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Disable MFA for current user
    """
    try:
        await AuthService.disable_mfa(
            user_id=current_user.id,
            password=request.password,
            otp_code=request.otp_code,
            backup_code=request.backup_code
        )
        return {"message": "MFA disabled successfully"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="MFA disable failed")


# ==================== PASSWORD RESET ENDPOINTS ====================

@router.post("/forgot-password")
async def forgot_password(request: PasswordResetRequest):
    """
    Request password reset
    Sends email with reset token
    """
    try:
        token = await AuthService.request_password_reset(request.email)
        # TODO: Send email with token
        # For now, return token in response (INSECURE - for development only)
        return {"message": "Password reset instructions sent", "token": token}
    except ValueError as e:
        # Don't reveal if email exists
        return {"message": "If email exists, reset instructions have been sent"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Password reset request failed")


@router.post("/reset-password")
async def reset_password(request: PasswordResetConfirm):
    """
    Confirm password reset with token
    """
    try:
        await AuthService.confirm_password_reset(request.token, request.new_password)
        return {"message": "Password reset successfully"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Password reset failed")


# ==================== ACTIVE DIRECTORY SYNC ====================

@router.post("/sync-ad", dependencies=[Depends(require_role("admin"))])
async def sync_active_directory(request: ADSyncRequest):
    """
    Sync users from Active Directory
    Admin only
    """
    try:
        if request.sync_all:
            # TODO: Implement bulk sync
            raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Bulk sync not implemented yet")
        else:
            user = await AuthService.sync_ad_user(request.username)
            return {
                "message": f"User {request.username} synced successfully",
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "username": user.username,
                    "full_name": user.full_name
                }
            }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="AD sync failed")


# ==================== USER INFO ====================

@router.get("/me")
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Get current user information
    """
    return {
        "id": current_user.id,
        "email": current_user.email,
        "username": current_user.username,
        "full_name": current_user.full_name,
        "user_type": current_user.user_type,
        "department": current_user.department,
        "position": current_user.position,
        "phone_number": current_user.phone_number,
        "mfa_enabled": current_user.mfa_enabled,
        "is_active": current_user.is_active,
        "role": {
            "id": current_user.role.id,
            "name": current_user.role.name,
            "display_name": current_user.role.display_name
        } if current_user.role else None,
        "created_at": current_user.created_at,
        "last_login_at": current_user.last_login_at
    }
