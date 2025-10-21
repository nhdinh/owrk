"""
Authentication API Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPAuthorizationCredentials
from typing import Optional
import logging
import traceback

from app.schemas.auth_schema import (
    LoginRequest,
    LoginResponse,
    MFAVerifyRequest,
    TokenResponse,
    RefreshTokenRequest,
    LogoutRequest,
    MFASetupResponse,
    MFAEnableRequest,
    MFADisableRequest,
    ADSyncRequest,
)
from app.schemas.user_schema import PasswordResetRequest, PasswordResetConfirm
from app.services.auth_service import AuthService
from app.core.dependencies import get_current_user, require_role, security
from app.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=LoginResponse)
async def login_step1(request: LoginRequest, http_request: Request):
    """
    Step 1: Login with email and password
    Returns temp token for MFA verification
    """
    try:
        ip_address = http_request.client.host if http_request.client else "unknown"
        result = await AuthService.login_step1(
            email=request.email, password=request.password, ip_address=ip_address
        )
        return result
    except ValueError as e:
        logger.error(f"Login authentication failed for {request.email}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except Exception as e:
        logger.error(f"Login error for {request.email}: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}",
        )


@router.post("/verify-otp", response_model=TokenResponse)
async def verify_otp(request: MFAVerifyRequest, http_request: Request):
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
            user_agent=user_agent,
        )
        return result
    except ValueError as e:
        logger.error(f"OTP verification failed: {str(e)}")
        logger.error(traceback.format_exc()) 
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except Exception as e:
        logger.error(f"OTP verification failed: {str(e)}")
        logger.error(traceback.format_exc()) 
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="OTP verification failed",
        )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(request: RefreshTokenRequest):
    """
    Refresh access token using refresh token
    """
    try:
        result = await AuthService.refresh_access_token(request.refresh_token)
        return result
    except ValueError as e:
        logger.error(f"Token refresh authentication failed: {str(e)}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except Exception as e:
        logger.error(f"Token refresh error: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed",
        )


@router.post("/logout")
async def logout(
    request: LogoutRequest, current_user: User = Depends(get_current_user)
):
    """
    Logout user by revoking refresh token
    """
    try:
        if request.refresh_token:
            await AuthService.logout(request.refresh_token)
        return {"message": "Logged out successfully"}
    except Exception as e:
        logger.error(f"Logout error for user {current_user.email}: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Logout failed"
        )


# ==================== MFA ENDPOINTS ====================


@router.get("/mfa/setup", response_model=MFASetupResponse)
async def setup_mfa(current_user: User = Depends(get_current_user)):
    """
    Setup MFA for current user
    Returns QR code and backup codes
    """
    try:
        # Use cached user_id to avoid detached instance error
        user_id = getattr(current_user, '_cached_id', None)
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid user session")

        result = await AuthService.setup_mfa(user_id)
        return result
    except ValueError as e:
        user_id = getattr(current_user, '_cached_id', None)
        logger.error(f"MFA setup validation failed for user {user_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        user_id = getattr(current_user, '_cached_id', None)
        logger.error(f"MFA setup error for user {user_id}: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="MFA setup failed"
        )


@router.post("/mfa/enable")
async def enable_mfa(
    request: MFAEnableRequest, current_user: User = Depends(get_current_user)
):
    """
    Enable MFA after verifying OTP code
    """
    try:
        # Use cached user_id to avoid detached instance error
        user_id = getattr(current_user, '_cached_id', None)
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid user session")

        await AuthService.enable_mfa(user_id, request.otp_code)
        return {"message": "MFA enabled successfully"}
    except ValueError as e:
        user_id = getattr(current_user, '_cached_id', None)
        logger.error(f"MFA enable validation failed for user {user_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        user_id = getattr(current_user, '_cached_id', None)
        logger.error(f"MFA enable error for user {user_id}: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="MFA enable failed",
        )


@router.post("/mfa/disable")
async def disable_mfa(
    request: MFADisableRequest, current_user: User = Depends(get_current_user)
):
    """
    Disable MFA for current user
    """
    try:
        # Use cached user_id to avoid detached instance error
        user_id = getattr(current_user, '_cached_id', None)
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid user session")

        await AuthService.disable_mfa(
            user_id=user_id,
            password=request.password,
            otp_code=request.otp_code,
            backup_code=request.backup_code,
        )
        return {"message": "MFA disabled successfully"}
    except ValueError as e:
        user_id = getattr(current_user, '_cached_id', None)
        logger.error(f"MFA disable validation failed for user {user_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        user_id = getattr(current_user, '_cached_id', None)
        logger.error(f"MFA disable error for user {user_id}: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="MFA disable failed",
        )


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
        logger.warning(f"Password reset requested for non-existent email: {request.email}")
        return {"message": "If email exists, reset instructions have been sent"}
    except Exception as e:
        logger.error(f"Password reset request error for {request.email}: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password reset request failed",
        )


@router.post("/reset-password")
async def reset_password(request: PasswordResetConfirm):
    """
    Confirm password reset with token
    """
    try:
        await AuthService.confirm_password_reset(request.token, request.new_password)
        return {"message": "Password reset successfully"}
    except ValueError as e:
        logger.error(f"Password reset validation failed: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Password reset error: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password reset failed",
        )


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
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail="Bulk sync not implemented yet",
            )
        else:
            user = await AuthService.sync_ad_user(request.username)
            return {
                "message": f"User {request.username} synced successfully",
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "username": user.username,
                    "full_name": user.full_name,
                },
            }
    except ValueError as e:
        logger.error(f"AD sync validation failed for username {request.username}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"AD sync error for username {request.username}: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="AD sync failed"
        )


# ==================== USER INFO ====================


@router.get("/me")
async def get_current_user_info(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Get current user information
    """
    # Decode token and get user_id
    from app.core.security import decode_token
    from app.core.unit_of_work import UnitOfWork

    token = credentials.credentials
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    # Get user from database within session context
    with UnitOfWork() as uow:
        user = uow.users.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        result = {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "full_name": user.full_name,
            "user_type": user.user_type,
            "department_id": user.department_id,
            "position": user.position,
            "phone_number": user.phone_number,
            "mfa_enabled": user.mfa_enabled,
            "is_active": user.is_active,
            "role": {
                "id": user.role.id,
                "name": user.role.name,
                "display_name": user.role.display_name,
            }
            if user.role
            else None,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "last_login_at": user.last_login_at.isoformat() if user.last_login_at else None,
        }
        return result


# ==================== DEBUG ENDPOINTS (Development Only) ====================


@router.post("/debug/test-otp")
async def debug_test_otp(email: str, otp_code: str):
    """
    DEBUG ONLY: Test OTP validation for a user
    This endpoint should be removed or disabled in production!

    Args:
        email: User email
        otp_code: OTP code to test

    Returns:
        Detailed debug information about OTP validation
    """
    from app.core.unit_of_work import UnitOfWork
    from app.core.security import verify_totp, verify_backup_code
    import pyotp
    from datetime import datetime

    try:
        with UnitOfWork() as uow:
            user = uow.users.get_by_email(email)
            if not user:
                raise HTTPException(status_code=404, detail="User not found")

            # Get current server time
            server_time = datetime.utcnow()

            # Basic user info
            result = {
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "mfa_enabled": user.mfa_enabled,
                    "has_mfa_secret": bool(user.mfa_secret),
                    "mfa_secret_length": len(user.mfa_secret) if user.mfa_secret else 0,
                },
                "server_time": {
                    "utc": server_time.isoformat(),
                    "timestamp": int(server_time.timestamp()),
                },
                "otp_test": {
                    "provided_code": otp_code,
                    "code_length": len(otp_code),
                }
            }

            if not user.mfa_enabled:
                result["status"] = "MFA_DISABLED"
                result["message"] = "MFA is not enabled for this user"
                return result

            if not user.mfa_secret:
                result["status"] = "NO_SECRET"
                result["message"] = "User has MFA enabled but no secret key configured"
                return result

            # Test TOTP validation
            try:
                # Generate expected codes for current time window
                totp = pyotp.TOTP(user.mfa_secret)

                # Current valid code
                current_code = totp.now()

                # Previous and next codes (for time drift tolerance)
                prev_code = totp.at(datetime.utcnow().timestamp() - 30)
                next_code = totp.at(datetime.utcnow().timestamp() + 30)

                # Test provided code
                is_valid = verify_totp(user.mfa_secret, otp_code)

                result["totp_analysis"] = {
                    "is_valid": is_valid,
                    "expected_codes": {
                        "previous_window": prev_code,
                        "current_window": current_code,
                        "next_window": next_code,
                    },
                    "provided_code_matches": {
                        "previous": otp_code == prev_code,
                        "current": otp_code == current_code,
                        "next": otp_code == next_code,
                    },
                    "secret_key_preview": f"{user.mfa_secret[:8]}...{user.mfa_secret[-4:]}" if len(user.mfa_secret) > 12 else "***",
                }

                if is_valid:
                    result["status"] = "OTP_VALID"
                    result["message"] = "OTP code is VALID!"
                else:
                    result["status"] = "OTP_INVALID"
                    result["message"] = f"OTP code is INVALID. Expected one of: {prev_code}, {current_code}, {next_code}"
                    result["debugging_tips"] = [
                        "Check if device time is synchronized (automatic time)",
                        "Verify you're using the correct account in authenticator app",
                        "Try waiting for next OTP code (30 seconds)",
                        "Check if secret key matches what was displayed during setup",
                    ]

            except Exception as e:
                result["totp_analysis"] = {
                    "error": str(e),
                    "error_type": type(e).__name__,
                }
                result["status"] = "TOTP_ERROR"
                result["message"] = f"Error testing TOTP: {str(e)}"

            # Check backup codes
            backup_codes = uow.mfa_backup_codes.get_unused_codes(user.id)
            result["backup_codes"] = {
                "total_unused": len(backup_codes),
                "has_unused_codes": len(backup_codes) > 0,
            }

            # Test if provided code is a backup code
            is_backup_code = False
            for backup_code in backup_codes:
                if verify_backup_code(otp_code, backup_code.code_hash):
                    is_backup_code = True
                    result["backup_code_match"] = {
                        "is_backup_code": True,
                        "code_id": backup_code.id,
                        "message": "Provided code matches an unused backup code!",
                    }
                    break

            if not is_backup_code and len(backup_codes) > 0:
                result["backup_code_match"] = {
                    "is_backup_code": False,
                    "message": "Provided code does not match any backup codes",
                }

            return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Debug OTP test error: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Debug test failed: {str(e)}",
        )


@router.post("/debug/get-mfa-secret")
async def debug_get_mfa_secret(email: str):
    """
    DEBUG ONLY: Get MFA secret and QR code for a user
    This endpoint should be removed or disabled in production!

    Args:
        email: User email

    Returns:
        Secret key and QR code URL for re-setup
    """
    from app.core.unit_of_work import UnitOfWork
    import pyotp
    import urllib.parse

    try:
        with UnitOfWork() as uow:
            user = uow.users.get_by_email(email)
            if not user:
                raise HTTPException(status_code=404, detail="User not found")

            if not user.mfa_secret:
                return {
                    "status": "NO_SECRET",
                    "message": "User has no MFA secret configured",
                    "email": user.email,
                }

            # Generate QR code URL
            totp = pyotp.TOTP(user.mfa_secret)
            provisioning_uri = totp.provisioning_uri(
                name=user.email,
                issuer_name="Asset Management"
            )

            # Generate QR code URL (using Google Charts API)
            qr_code_url = f"https://chart.googleapis.com/chart?chs=200x200&chld=M|0&cht=qr&chl={urllib.parse.quote(provisioning_uri)}"

            # Generate current valid code for verification
            current_code = totp.now()

            return {
                "status": "SUCCESS",
                "user": {
                    "email": user.email,
                    "mfa_enabled": user.mfa_enabled,
                },
                "mfa_setup": {
                    "secret_key": user.mfa_secret,
                    "qr_code_url": qr_code_url,
                    "provisioning_uri": provisioning_uri,
                    "current_valid_code": current_code,
                },
                "instructions": [
                    "1. Delete the OLD entry in your authenticator app",
                    "2. Scan the QR code OR manually enter the secret key",
                    "3. Verify the code matches 'current_valid_code' shown above",
                    "4. Try logging in again",
                ],
            }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Debug get MFA secret error: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Debug failed: {str(e)}",
        )


@router.post("/debug/disable-mfa")
async def debug_disable_mfa(email: str):
    """
    DEBUG ONLY: Disable MFA for a user without requiring password/OTP
    This endpoint should be removed or disabled in production!

    Args:
        email: User email

    Returns:
        Confirmation message
    """
    from app.core.unit_of_work import UnitOfWork

    try:
        with UnitOfWork() as uow:
            user = uow.users.get_by_email(email)
            if not user:
                raise HTTPException(status_code=404, detail="User not found")

            was_enabled = user.mfa_enabled

            # Disable MFA
            user.mfa_enabled = False
            user.mfa_secret = None
            uow.users.update(user)

            # Delete all backup codes
            uow.mfa_backup_codes.delete_all_for_user(user.id)

            uow.commit()

            return {
                "status": "SUCCESS",
                "message": f"MFA disabled for {email}",
                "user": {
                    "email": user.email,
                    "mfa_was_enabled": was_enabled,
                    "mfa_now_enabled": False,
                },
                "next_steps": [
                    "1. You can now login without OTP",
                    "2. To re-enable MFA, login and go to Security Settings",
                    "3. Setup MFA again with a fresh QR code",
                ],
            }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Debug disable MFA error: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Debug failed: {str(e)}",
        )
