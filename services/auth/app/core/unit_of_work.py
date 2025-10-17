"""
Unit of Work Pattern Implementation
Manages transactions and repositories
"""

from typing import Optional
from sqlalchemy.orm import Session
from app.core.database import SessionLocal


class UnitOfWork:
    """
    Unit of Work Pattern for transaction management

    Ensures:
    - All operations in a business transaction use the same DB session
    - Commit/Rollback all changes together (atomicity)
    - Automatic cleanup of resources
    """

    def __init__(self, db: Optional[Session] = None):
        self.db = db or SessionLocal()
        self._should_close_session = db is None

        # Repository instances (lazy loaded)
        self._user_repository = None
        self._role_repository = None
        self._permission_repository = None
        self._refresh_token_repository = None
        self._password_reset_token_repository = None
        self._mfa_backup_code_repository = None

    @property
    def users(self):
        """Lazy load User Repository"""
        if self._user_repository is None:
            from app.repositories.user_repository import UserRepository
            self._user_repository = UserRepository(self.db)
        return self._user_repository

    @property
    def roles(self):
        """Lazy load Role Repository"""
        if self._role_repository is None:
            from app.repositories.role_repository import RoleRepository
            self._role_repository = RoleRepository(self.db)
        return self._role_repository

    @property
    def permissions(self):
        """Lazy load Permission Repository"""
        if self._permission_repository is None:
            from app.repositories.role_repository import PermissionRepository
            self._permission_repository = PermissionRepository(self.db)
        return self._permission_repository

    @property
    def refresh_tokens(self):
        """Lazy load RefreshToken Repository"""
        if self._refresh_token_repository is None:
            from app.repositories.refresh_token_repository import RefreshTokenRepository
            self._refresh_token_repository = RefreshTokenRepository(self.db)
        return self._refresh_token_repository

    @property
    def password_reset_tokens(self):
        """Lazy load PasswordResetToken Repository"""
        if self._password_reset_token_repository is None:
            from app.repositories.refresh_token_repository import PasswordResetTokenRepository
            self._password_reset_token_repository = PasswordResetTokenRepository(self.db)
        return self._password_reset_token_repository

    @property
    def mfa_backup_codes(self):
        """Lazy load MFABackupCode Repository"""
        if self._mfa_backup_code_repository is None:
            from app.repositories.refresh_token_repository import MFABackupCodeRepository
            self._mfa_backup_code_repository = MFABackupCodeRepository(self.db)
        return self._mfa_backup_code_repository

    def commit(self):
        """Commit transaction"""
        self.db.commit()

    def rollback(self):
        """Rollback transaction"""
        self.db.rollback()

    def close(self):
        """Close database session"""
        if self._should_close_session:
            self.db.close()

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - auto commit/rollback"""
        try:
            if exc_type is None:
                self.commit()
            else:
                self.rollback()
        finally:
            self.close()
