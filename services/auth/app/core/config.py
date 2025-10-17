"""
Configuration settings for Auth Service
"""

from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables
    """

    # Application
    APP_NAME: str = "Asset Management - Auth Service"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Database - PostgreSQL (Write DB)
    DATABASE_URL: str = "postgresql://admin:secret123@localhost:5432/asset_management"
    DB_SCHEMA: str = "auth_db"

    # MongoDB (Read DB for CQRS)
    MONGODB_URL: str = "mongodb://admin:secret123@localhost:27017/"
    MONGODB_DB_NAME: str = "asset_management_read"

    # RabbitMQ
    RABBITMQ_URL: str = "amqp://guest:guest@localhost:5672/"

    # Redis
    REDIS_URL: str = "redis://localhost:6379"

    # JWT Settings
    JWT_SECRET: str = "your-super-secret-jwt-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480  # 8 hours
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # MFA/OTP Settings
    MFA_ISSUER: str = "AssetManagement"
    MFA_BACKUP_CODES_COUNT: int = 10

    # Active Directory Settings
    AD_SERVER: str = "ldap://ad.company.local"
    AD_DOMAIN: str = "company.local"
    AD_BIND_DN: str = "CN=admin,DC=company,DC=local"
    AD_BIND_PASSWORD: str = "ad_password"
    AD_SEARCH_BASE: str = "OU=Users,DC=company,DC=local"
    AD_ENABLED: bool = False  # Enable when AD is available

    # Password Policy
    PASSWORD_MIN_LENGTH: int = 8
    PASSWORD_REQUIRE_UPPERCASE: bool = True
    PASSWORD_REQUIRE_LOWERCASE: bool = True
    PASSWORD_REQUIRE_DIGIT: bool = True
    PASSWORD_REQUIRE_SPECIAL: bool = False

    # Security
    BCRYPT_SALT_ROUNDS: int = 12
    MAX_LOGIN_ATTEMPTS: int = 5
    LOCKOUT_DURATION_MINUTES: int = 30

    # Session
    SESSION_TIMEOUT_MINUTES: int = 480  # 8 hours
    REMEMBER_ME_DAYS: int = 7

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
    ]

    # SMTP Settings (for email notifications)
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = "noreply@company.com"
    SMTP_PASSWORD: str = ""
    SMTP_FROM: str = "noreply@company.com"
    SMTP_TLS: bool = True

    # File Upload
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_FILE_EXTENSIONS: List[str] = [".pdf", ".png", ".jpg", ".jpeg"]

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60

    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
