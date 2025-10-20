"""
RefreshToken and related repositories
"""

from typing import Optional, List
from datetime import datetime
from sqlalchemy.orm import Session

from app.repositories.base_repository import BaseRepository
from app.models.refresh_token import RefreshToken, PasswordResetToken, MFABackupCode


class RefreshTokenRepository(BaseRepository[RefreshToken]):
    """
    Repository for RefreshToken entity
    """

    def __init__(self, db: Session):
        super().__init__(RefreshToken, db)

    def get_by_token(self, token: str) -> Optional[RefreshToken]:
        """Get refresh token by token string"""
        return self.db.query(RefreshToken).filter(
            RefreshToken.token == token
        ).first()

    def get_by_user_id(self, user_id: int, skip: int = 0, limit: int = 10) -> List[RefreshToken]:
        """Get all refresh tokens for a user"""
        return self.db.query(RefreshToken).filter(
            RefreshToken.user_id == user_id
        ).order_by(RefreshToken.created_at.desc()).offset(skip).limit(limit).all()

    def get_active_tokens_by_user(self, user_id: int) -> List[RefreshToken]:
        """Get all active (non-revoked, non-expired) tokens for a user"""
        now = datetime.utcnow()
        return self.db.query(RefreshToken).filter(
            RefreshToken.user_id == user_id,
            RefreshToken.is_revoked == False,
            RefreshToken.expires_at > now
        ).all()

    def revoke_token(self, token: str) -> bool:
        """Revoke a refresh token"""
        refresh_token = self.get_by_token(token)
        if refresh_token:
            refresh_token.is_revoked = True
            refresh_token.revoked_at = datetime.utcnow()
            self.db.flush()
            return True
        return False

    def revoke_all_user_tokens(self, user_id: int) -> int:
        """Revoke all refresh tokens for a user. Returns count of revoked tokens."""
        tokens = self.get_active_tokens_by_user(user_id)
        count = 0
        for token in tokens:
            token.is_revoked = True
            token.revoked_at = datetime.utcnow()
            count += 1
        if count > 0:
            self.db.flush()
        return count

    def cleanup_expired_tokens(self) -> int:
        """Delete expired tokens. Returns count of deleted tokens."""
        now = datetime.utcnow()
        result = self.db.query(RefreshToken).filter(
            RefreshToken.expires_at < now
        ).delete()
        self.db.flush()
        return result

    def is_token_valid(self, token: str) -> bool:
        """Check if token exists and is valid (not revoked, not expired)"""
        refresh_token = self.get_by_token(token)
        if not refresh_token:
            return False

        if refresh_token.is_revoked:
            return False

        if refresh_token.expires_at < datetime.utcnow():
            return False

        return True


class PasswordResetTokenRepository(BaseRepository[PasswordResetToken]):
    """
    Repository for PasswordResetToken entity
    """

    def __init__(self, db: Session):
        super().__init__(PasswordResetToken, db)

    def get_by_token(self, token: str) -> Optional[PasswordResetToken]:
        """Get password reset token by token string"""
        return self.db.query(PasswordResetToken).filter(
            PasswordResetToken.token == token
        ).first()

    def get_by_user_id(self, user_id: int) -> List[PasswordResetToken]:
        """Get all password reset tokens for a user"""
        return self.db.query(PasswordResetToken).filter(
            PasswordResetToken.user_id == user_id
        ).order_by(PasswordResetToken.created_at.desc()).all()

    def invalidate_user_tokens(self, user_id: int) -> int:
        """Mark all user's password reset tokens as used. Returns count."""
        tokens = self.db.query(PasswordResetToken).filter(
            PasswordResetToken.user_id == user_id,
            PasswordResetToken.is_used == False
        ).all()

        count = 0
        for token in tokens:
            token.is_used = True
            count += 1

        if count > 0:
            self.db.flush()

        return count

    def is_token_valid(self, token: str) -> bool:
        """Check if token exists and is valid (not used, not expired)"""
        reset_token = self.get_by_token(token)
        if not reset_token:
            return False

        if reset_token.is_used:
            return False

        if reset_token.expires_at < datetime.utcnow():
            return False

        return True

    def mark_as_used(self, token: str) -> bool:
        """Mark token as used"""
        reset_token = self.get_by_token(token)
        if reset_token:
            reset_token.is_used = True
            self.db.flush()
            return True
        return False


class MFABackupCodeRepository(BaseRepository[MFABackupCode]):
    """
    Repository for MFABackupCode entity
    """

    def __init__(self, db: Session):
        super().__init__(MFABackupCode, db)

    def get_user_backup_codes(self, user_id: int) -> List[MFABackupCode]:
        """Get all backup codes for a user"""
        return self.db.query(MFABackupCode).filter(
            MFABackupCode.user_id == user_id
        ).all()

    def get_unused_codes(self, user_id: int) -> List[MFABackupCode]:
        """Get unused backup codes for a user"""
        return self.db.query(MFABackupCode).filter(
            MFABackupCode.user_id == user_id,
            MFABackupCode.is_used == False
        ).all()

    def mark_code_as_used(self, user_id: int, code_hash: str) -> bool:
        """Mark a backup code as used"""
        backup_code = self.db.query(MFABackupCode).filter(
            MFABackupCode.user_id == user_id,
            MFABackupCode.code_hash == code_hash,
            MFABackupCode.is_used == False
        ).first()

        if backup_code:
            backup_code.is_used = True
            backup_code.used_at = datetime.utcnow()
            self.db.flush()
            return True

        return False

    def delete_all_user_codes(self, user_id: int) -> int:
        """Delete all backup codes for a user. Returns count."""
        result = self.db.query(MFABackupCode).filter(
            MFABackupCode.user_id == user_id
        ).delete()
        self.db.flush()
        return result

    def get_unused_count(self, user_id: int) -> int:
        """Count unused backup codes for a user"""
        return self.db.query(MFABackupCode).filter(
            MFABackupCode.user_id == user_id,
            MFABackupCode.is_used == False
        ).count()
