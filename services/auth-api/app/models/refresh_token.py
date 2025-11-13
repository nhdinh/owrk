"""
Refresh Token Model
"""

from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Boolean, event
from sqlalchemy.orm import relationship
from app.models.base import Base
from app.core.utils import generate_slug


class RefreshToken(Base):
    """
    Refresh Token model for JWT token refresh mechanism
    """

    __tablename__ = "refresh_tokens"
    __table_args__ = {"schema": "auth_db"}

    # Token Information
    token = Column(String(255), unique=True, index=True, nullable=False)
    user_id = Column(String(32), ForeignKey("auth_db.users.id"), nullable=False)

    # Token Metadata
    expires_at = Column(DateTime(timezone=True), nullable=False)
    is_revoked = Column(Boolean, default=False, nullable=False)
    revoked_at = Column(DateTime(timezone=True), nullable=True)

    # Device/Session Information
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(255), nullable=True)
    device_name = Column(String(100), nullable=True)

    # Relationships
    user = relationship("User", back_populates="refresh_tokens")

    # Timestamps inherited from Base

    def __repr__(self):
        return f"<RefreshToken(id={self.id}, user_id={self.user_id}, revoked={self.is_revoked})>"


class PasswordResetToken(Base):
    """
    Password Reset Token model
    """

    __tablename__ = "password_reset_tokens"
    __table_args__ = {"schema": "auth_db"}

    # Token Information
    token = Column(String(255), unique=True, index=True, nullable=False)
    user_id = Column(String(32), ForeignKey("auth_db.users.id"), nullable=False)

    # Token Metadata
    expires_at = Column(DateTime(timezone=True), nullable=False)
    is_used = Column(Boolean, default=False, nullable=False)
    used_at = Column(DateTime(timezone=True), nullable=True)

    # Request Information
    ip_address = Column(String(45), nullable=True)

    # Relationships
    user = relationship("User", back_populates="password_reset_tokens")

    # Timestamps inherited from Base

    def __repr__(self):
        return f"<PasswordResetToken(id={self.id}, user_id={self.user_id}, used={self.is_used})>"


class MFABackupCode(Base):
    """
    MFA Backup Codes for account recovery
    """

    __tablename__ = "mfa_backup_codes"
    __table_args__ = {"schema": "auth_db"}

    # Code Information
    code_hash = Column(String(255), nullable=False)
    user_id = Column(String(32), ForeignKey("auth_db.users.id"), nullable=False)

    # Status
    is_used = Column(Boolean, default=False, nullable=False)
    used_at = Column(DateTime(timezone=True), nullable=True)

    # Timestamps inherited from Base

    def __repr__(self):
        return f"<MFABackupCode(id={self.id}, user_id={self.user_id}, used={self.is_used})>"


# Event listeners for auto-generating slugs
@event.listens_for(RefreshToken, "before_insert")
def generate_refresh_token_slug(mapper, connection, target):
    """Auto-generate slug from token prefix if not provided"""
    if not target.slug:
        # Use first 12 chars of token as slug (unique enough)
        target.slug = generate_slug(target.token[:12])


@event.listens_for(PasswordResetToken, "before_insert")
def generate_password_reset_token_slug(mapper, connection, target):
    """Auto-generate slug from token prefix if not provided"""
    if not target.slug:
        target.slug = generate_slug(target.token[:12])


@event.listens_for(MFABackupCode, "before_insert")
def generate_mfa_backup_code_slug(mapper, connection, target):
    """Auto-generate slug from code hash prefix if not provided"""
    if not target.slug:
        target.slug = generate_slug(target.code_hash[:12])
