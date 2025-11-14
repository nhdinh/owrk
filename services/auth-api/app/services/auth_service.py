"""
Authentication Service - Business Logic for Authentication
"""

import logging
from typing import Optional
from datetime import datetime, timedelta

from app.core.unit_of_work import UnitOfWork
from app.core.security import (
    verify_password,
    hash_password,
    create_access_token,
    create_refresh_token,
    create_temp_token,
    decode_token,
    generate_totp_secret,
    generate_totp_uri,
    generate_qr_code,
    verify_totp,
    generate_backup_codes,
    hash_backup_code,
    verify_backup_code,
    generate_reset_token,
)
from app.core.active_directory import ad_service
from app.core.config import settings
from app.models.user import User
from app.models.refresh_token import RefreshToken, PasswordResetToken, MFABackupCode
from app.schemas.auth_schema import LoginResponse, TokenResponse, MFASetupResponse
from app.services.email_service import EmailService


logger = logging.getLogger("AuthService")


class AuthService:
    """
    Service for authentication operations
    """

    MAX_FAILED_ATTEMPTS = 5
    LOCKOUT_DURATION_MINUTES = 30

    @staticmethod
    async def login_step1(email: str, password: str, ip_address: str) -> LoginResponse:
        """
        Step 1 of login: Validate email and password
        Returns temp token for MFA verification if MFA is enabled

        Args:
            email: User email
            password: User password
            ip_address: Client IP address

        Returns:
            LoginResponse with temp_token and requires_mfa flag

        Raises:
            ValueError: If credentials are invalid or account is locked
        """
        with UnitOfWork() as uow:
            # Get user by email
            user = uow.users.get_by_email(email)
            if not user:
                raise ValueError("Invalid email or password")

            # Check if account is locked
            if user.locked_until and user.locked_until > datetime.utcnow():
                raise ValueError(f"Account is locked until {user.locked_until}")

            # Check if account is active
            if not user.is_active:
                raise ValueError("Account is deactivated")

            # Authenticate based on user type
            if user.user_type == "local":
                # Local user: verify password hash
                if not user.hashed_password or not verify_password(
                    password, user.hashed_password
                ):
                    uow.users.increment_failed_attempts(user.id)

                    # Lock account if too many failed attempts
                    if (
                        user.failed_login_attempts + 1
                        >= AuthService.MAX_FAILED_ATTEMPTS
                    ):
                        uow.users.lock_account(
                            user.id, AuthService.LOCKOUT_DURATION_MINUTES
                        )
                        uow.commit()
                        raise ValueError(
                            f"Too many failed attempts. Account locked for {AuthService.LOCKOUT_DURATION_MINUTES} minutes"
                        )

                    uow.commit()
                    raise ValueError("Invalid email or password")

            elif user.user_type == "active_directory":
                # AD user: authenticate via LDAP
                ad_user = ad_service.authenticate_user(user.username, password)
                if not ad_user:
                    uow.users.increment_failed_attempts(user.id)

                    if (
                        user.failed_login_attempts + 1
                        >= AuthService.MAX_FAILED_ATTEMPTS
                    ):
                        uow.users.lock_account(
                            user.id, AuthService.LOCKOUT_DURATION_MINUTES
                        )
                        uow.commit()
                        raise ValueError(
                            f"Too many failed attempts. Account locked for {AuthService.LOCKOUT_DURATION_MINUTES} minutes"
                        )

                    uow.commit()
                    raise ValueError("Active Directory authentication failed")

            else:
                raise ValueError("Invalid user type")

            # Authentication successful - reset failed attempts
            uow.users.reset_failed_attempts(user.id)

            # Generate temporary token for MFA step
            temp_token = create_temp_token({"sub": str(user.id), "email": user.email})

            uow.commit()

            return LoginResponse(
                temp_token=temp_token,
                requires_mfa=user.mfa_enabled,
                message="OTP required" if user.mfa_enabled else "Login successful",
            )

    @staticmethod
    async def login_step2_mfa(
        temp_token: str, otp_code: str, ip_address: str, user_agent: str
    ) -> TokenResponse:
        """
        Step 2 of login: Verify MFA OTP code
        Returns final access and refresh tokens

        Args:
            temp_token: Temporary token from step 1
            otp_code: OTP code from authenticator app or backup code
            ip_address: Client IP address
            user_agent: Client user agent

        Returns:
            TokenResponse with access_token and refresh_token

        Raises:
            ValueError: If temp token or OTP is invalid
        """
        # Decode temp token
        logger.info(f"Decoding temp_token: {temp_token[:20]}...")
        payload = decode_token(temp_token)
        logger.info(f"Decoded payload = {payload}")

        if not payload:
            logger.error("Token decoding failed - payload is None")
            raise ValueError("Invalid or expired temporary token")

        if payload.get("type") != "temp":
            logger.error(
                f"Token type mismatch. Expected 'temp', got '{payload.get('type')}'"
            )
            raise ValueError("Invalid or expired temporary token")

        user_id = payload.get("sub")
        if not user_id:
            logger.error("Token payload missing 'sub' field")
            raise ValueError("Invalid token payload")

        with UnitOfWork() as uow:
            user = uow.users.get_by_id(user_id)
            if not user or not user.is_active:
                raise ValueError("User not found or inactive")

            # If MFA is not enabled, skip verification
            if not user.mfa_enabled:
                return await AuthService._generate_tokens(
                    user, ip_address, user_agent, uow
                )

            # Verify TOTP code
            if user.mfa_secret and verify_totp(user.mfa_secret, otp_code):
                uow.users.update_last_login(user.id, ip_address)
                tokens = await AuthService._generate_tokens(
                    user, ip_address, user_agent, uow
                )
                uow.commit()
                return tokens

            # If TOTP fails, try backup codes
            backup_codes = uow.mfa_backup_codes.get_unused_codes(user_id)
            for backup_code in backup_codes:
                if verify_backup_code(otp_code, backup_code.code_hash):
                    # Mark backup code as used
                    uow.mfa_backup_codes.mark_code_as_used(
                        user_id, backup_code.code_hash
                    )
                    uow.users.update_last_login(user.id, ip_address)
                    tokens = await AuthService._generate_tokens(
                        user, ip_address, user_agent, uow
                    )
                    uow.commit()
                    return tokens

            raise ValueError("Invalid OTP code")

    @staticmethod
    async def _generate_tokens(
        user: User, ip_address: str, user_agent: str, uow: UnitOfWork
    ) -> TokenResponse:
        """
        Generate access and refresh tokens for user

        Args:
            user: User entity
            ip_address: Client IP
            user_agent: Client user agent
            uow: Unit of Work instance

        Returns:
            TokenResponse with tokens and user info
        """
        # Create access token
        access_token = create_access_token(
            {"sub": str(user.id), "email": user.email, "type": "access"}
        )

        # Create refresh token
        refresh_token_str = create_refresh_token(
            {"sub": str(user.id), "email": user.email, "type": "refresh"}
        )

        # Store refresh token in database
        refresh_token = RefreshToken(
            user_id=user.id,
            token=refresh_token_str,
            expires_at=datetime.utcnow()
            + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
            ip_address=ip_address,
            user_agent=user_agent,
        )
        uow.refresh_tokens.create(refresh_token)

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token_str,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user={
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "user_type": user.user_type,
                "mfa_enabled": user.mfa_enabled,
            },
        )

    @staticmethod
    async def refresh_access_token(refresh_token: str) -> TokenResponse:
        """
        Refresh access token using refresh token

        Args:
            refresh_token: Refresh token string

        Returns:
            New TokenResponse with new access token

        Raises:
            ValueError: If refresh token is invalid
        """
        with UnitOfWork() as uow:
            # Verify token exists and is valid
            if not uow.refresh_tokens.is_token_valid(refresh_token):
                raise ValueError("Invalid or expired refresh token")

            # Decode token
            payload = decode_token(refresh_token)
            if not payload or payload.get("type") != "refresh":
                raise ValueError("Invalid refresh token")

            user_id = payload.get("sub")
            user = uow.users.get_by_id(user_id)
            if not user or not user.is_active:
                raise ValueError("User not found or inactive")

            # Create new access token
            access_token = create_access_token(
                {"sub": str(user.id), "email": user.email, "type": "access"}
            )

            return TokenResponse(
                access_token=access_token,
                refresh_token=refresh_token,  # Return same refresh token
                token_type="bearer",
                expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                user={
                    "id": user.id,
                    "email": user.email,
                    "full_name": user.full_name,
                    "user_type": user.user_type,
                    "mfa_enabled": user.mfa_enabled,
                },
            )

    @staticmethod
    async def logout(refresh_token: str) -> bool:
        """
        Logout user by revoking refresh token

        Args:
            refresh_token: Refresh token to revoke

        Returns:
            True if successful
        """
        with UnitOfWork() as uow:
            result = uow.refresh_tokens.revoke_token(refresh_token)
            uow.commit()
            return result

    @staticmethod
    async def setup_mfa(user_id: int) -> MFASetupResponse:
        """
        Setup MFA for user - generates secret and QR code

        Args:
            user_id: User ID

        Returns:
            MFASetupResponse with secret, QR code, and backup codes

        Raises:
            ValueError: If user not found
        """
        with UnitOfWork() as uow:
            user = uow.users.get_by_id(user_id)
            if not user:
                raise ValueError("User not found")

            # Generate TOTP secret
            secret = generate_totp_secret()

            # Generate TOTP URI for QR code
            uri = generate_totp_uri(secret, user.email)

            # Generate QR code image
            qr_code_url = generate_qr_code(uri)

            # Generate backup codes
            backup_codes_plain = generate_backup_codes(10)

            # Store secret temporarily (not enabled yet)
            user.mfa_secret = secret
            uow.users.update(user)

            # Store backup codes
            uow.mfa_backup_codes.delete_all_user_codes(user_id)
            for code in backup_codes_plain:
                backup_code = MFABackupCode(
                    user_id=user_id, code_hash=hash_backup_code(code)
                )
                uow.mfa_backup_codes.create(backup_code)

            uow.commit()

            return MFASetupResponse(
                secret=secret, qr_code_url=qr_code_url, backup_codes=backup_codes_plain
            )

    @staticmethod
    async def enable_mfa(user_id: int, otp_code: str) -> bool:
        """
        Enable MFA for user after verifying OTP code

        Args:
            user_id: User ID
            otp_code: OTP code from authenticator app

        Returns:
            True if successful

        Raises:
            ValueError: If OTP is invalid
        """
        with UnitOfWork() as uow:
            user = uow.users.get_by_id(user_id)
            if not user or not user.mfa_secret:
                raise ValueError("MFA not set up")

            # Verify OTP code
            if not verify_totp(user.mfa_secret, otp_code):
                raise ValueError("Invalid OTP code")

            # Enable MFA
            user.mfa_enabled = True
            uow.users.update(user)
            uow.commit()

            return True

    @staticmethod
    async def disable_mfa(
        user_id: int,
        password: str,
        otp_code: Optional[str] = None,
        backup_code: Optional[str] = None,
    ) -> bool:
        """
        Disable MFA for user

        Args:
            user_id: User ID
            password: User password for verification
            otp_code: OTP code (optional)
            backup_code: Backup code (optional)

        Returns:
            True if successful

        Raises:
            ValueError: If verification fails
        """
        with UnitOfWork() as uow:
            user = uow.users.get_by_id(user_id)
            if not user:
                raise ValueError("User not found")

            # Verify password
            if user.user_type == "local":
                if not user.hashed_password or not verify_password(
                    password, user.hashed_password
                ):
                    raise ValueError("Invalid password")

            # If MFA is enabled, verify OTP or backup code
            if user.mfa_enabled:
                verified = False

                # Try OTP code
                if otp_code and user.mfa_secret:
                    verified = verify_totp(user.mfa_secret, otp_code)

                # Try backup code
                if not verified and backup_code:
                    backup_codes = uow.mfa_backup_codes.get_unused_codes(user_id)
                    for bc in backup_codes:
                        if verify_backup_code(backup_code, bc.code_hash):
                            verified = True
                            break

                if not verified:
                    raise ValueError("Invalid OTP or backup code")

            # Disable MFA
            user.mfa_enabled = False
            user.mfa_secret = None
            uow.users.update(user)

            # Delete backup codes
            uow.mfa_backup_codes.delete_all_user_codes(user_id)

            uow.commit()
            return True

    @staticmethod
    async def request_password_reset(email: str) -> str:
        """
        Request password reset - generates reset token

        Args:
            email: User email

        Returns:
            Reset token

        Raises:
            ValueError: If user not found
        """
        with UnitOfWork() as uow:
            user = uow.users.get_by_email(email)
            if not user:
                # Don't reveal if email exists
                raise ValueError("If email exists, reset instructions have been sent")

            # Only local users can reset password
            if user.user_type != "local":
                raise ValueError(
                    "Password reset not available for Active Directory users"
                )

            # Generate reset token
            token = generate_reset_token()

            # Invalidate previous tokens
            uow.password_reset_tokens.invalidate_user_tokens(user.id)

            # Create new reset token
            reset_token = PasswordResetToken(
                user_id=user.id,
                token=token,
                expires_at=datetime.utcnow() + timedelta(hours=1),
            )
            uow.password_reset_tokens.create(reset_token)

            uow.commit()

            # Send email with reset token
            try:
                EmailService.send_password_reset_email(
                    to_email=user.email,
                    reset_token=token,
                    user_full_name=user.full_name,
                )
                logger.info(f"Password reset email sent to {user.email}")
            except Exception as e:
                logger.error(f"Failed to send password reset email: {str(e)}")
                # Don't fail the request if email fails - the token is still valid

            return token

    @staticmethod
    async def confirm_password_reset(token: str, new_password: str) -> bool:
        """
        Confirm password reset with token

        Args:
            token: Reset token
            new_password: New password

        Returns:
            True if successful

        Raises:
            ValueError: If token is invalid
        """
        with UnitOfWork() as uow:
            # Verify token
            if not uow.password_reset_tokens.is_token_valid(token):
                raise ValueError("Invalid or expired reset token")

            # Get token
            reset_token = uow.password_reset_tokens.get_by_token(token)
            if not reset_token:
                raise ValueError("Invalid reset token")

            # Get user
            user = uow.users.get_by_id(reset_token.user_id)
            if not user or user.user_type != "local":
                raise ValueError("User not found or not local user")

            # Update password
            user.hashed_password = hash_password(new_password)
            user.password_changed_at = datetime.utcnow()
            uow.users.update(user)

            # Mark token as used
            uow.password_reset_tokens.mark_as_used(token)

            # Revoke all refresh tokens for security
            uow.refresh_tokens.revoke_all_user_tokens(user.id)

            uow.commit()

            # Send confirmation email
            try:
                EmailService.send_password_changed_notification(
                    to_email=user.email,
                    user_full_name=user.full_name,
                )
                logger.info(f"Password changed notification sent to {user.email}")
            except Exception as e:
                logger.error(f"Failed to send password changed notification: {str(e)}")

            return True

    @staticmethod
    async def sync_ad_user(username: str) -> Optional[User]:
        """
        Sync single user from Active Directory

        Args:
            username: AD username

        Returns:
            User entity if successful

        Raises:
            ValueError: If AD is not enabled or user not found
        """
        if not settings.AD_ENABLED:
            raise ValueError("Active Directory integration is not enabled")

        # Get user info from AD
        ad_user_info = ad_service.get_user_info(username)
        if not ad_user_info:
            raise ValueError(f"User {username} not found in Active Directory")

        with UnitOfWork() as uow:
            # Check if user exists by AD sync ID
            user = (
                uow.users.get_by_ad_sync_id(ad_user_info["ad_sync_id"])
                if ad_user_info.get("ad_sync_id")
                else None
            )

            if user:
                # Update existing user
                user.email = ad_user_info.get("email") or user.email
                user.full_name = ad_user_info.get("full_name") or user.full_name
                user.department = ad_user_info.get("department")
                user.phone_number = ad_user_info.get("phone_number")
                user.position = ad_user_info.get("position")
                uow.users.update(user)
            else:
                # Create new user
                user = User(
                    email=ad_user_info["email"],
                    username=ad_user_info["username"],
                    full_name=ad_user_info["full_name"],
                    user_type="active_directory",
                    ad_sync_id=ad_user_info.get("ad_sync_id"),
                    department=ad_user_info.get("department"),
                    phone_number=ad_user_info.get("phone_number"),
                    position=ad_user_info.get("position"),
                    is_active=True,
                )
                user = uow.users.create(user)

            uow.commit()
            return user
