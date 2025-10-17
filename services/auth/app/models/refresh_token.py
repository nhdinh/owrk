"""
Refresh Token Model
"""

from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from app.models.base import Base


class RefreshToken(Base):
    """
    Refresh Token model for JWT token refresh mechanism
    """
    __tablename__ = "refresh_tokens"
    __table_args__ = {'schema': 'auth_db'}

    # Token Information
    token = Column(String(255), unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey('auth_db.users.id'), nullable=False)

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
    __table_args__ = {'schema': 'auth_db'}

    # Token Information
    token = Column(String(255), unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey('auth_db.users.id'), nullable=False)

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
    __table_args__ = {'schema': 'auth_db'}

    # Code Information
    code = Column(String(20), nullable=False)
    user_id = Column(Integer, ForeignKey('auth_db.users.id'), nullable=False)

    # Status
    is_used = Column(Boolean, default=False, nullable=False)
    used_at = Column(DateTime(timezone=True), nullable=True)

    # Timestamps inherited from Base

    def __repr__(self):
        return f"<MFABackupCode(id={self.id}, user_id={self.user_id}, used={self.is_used})>"
