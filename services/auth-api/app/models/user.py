"""
User Model
"""

from sqlalchemy import Column, String, Boolean, Integer, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import Base


class User(Base):
    """
    User model for authentication and authorization
    Supports both local users and Active Directory users
    """
    __tablename__ = "users"
    __table_args__ = {'schema': 'auth_db'}

    # Basic Information
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=True)
    full_name = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=True)  # Nullable for AD users

    # User Type
    user_type = Column(String(20), default="local", nullable=False)  # local | active_directory
    ad_sync_id = Column(String(255), unique=True, nullable=True)  # AD user ID

    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    email_verified = Column(Boolean, default=False, nullable=False)

    # MFA/Security
    mfa_enabled = Column(Boolean, default=False, nullable=False)
    mfa_secret = Column(String(255), nullable=True)  # Encrypted TOTP secret
    backup_codes = Column(Text, nullable=True)  # JSON array of backup codes

    # Security Tracking
    failed_login_attempts = Column(Integer, default=0, nullable=False)
    locked_until = Column(DateTime(timezone=True), nullable=True)
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    last_login_ip = Column(String(45), nullable=True)

    # Password Management
    password_changed_at = Column(DateTime(timezone=True), nullable=True)
    require_password_change = Column(Boolean, default=False, nullable=False)

    # Department & Contact
    department_id = Column(Integer, nullable=True)
    phone_number = Column(String(20), nullable=True)
    address = Column(Text, nullable=True)
    position = Column(String(100), nullable=True)

    # Foreign Keys
    role_id = Column(Integer, ForeignKey('auth_db.roles.id'), nullable=True)

    # Versioning (for history tracking)
    version = Column(Integer, default=1, nullable=False)  # Incremented on each update

    # Relationships
    role = relationship("Role", back_populates="users")
    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")
    password_reset_tokens = relationship("PasswordResetToken", back_populates="user", cascade="all, delete-orphan")
    history = relationship("UserHistory", backref="user", lazy="dynamic", order_by="UserHistory.version.desc()")

    # Timestamps inherited from Base: created_at, updated_at

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', full_name='{self.full_name}')>"

    @property
    def is_locked(self):
        """Check if user account is locked"""
        if self.locked_until and self.locked_until > func.now():
            return True
        return False

    def can_login(self):
        """Check if user can login"""
        return self.is_active and not self.is_locked
