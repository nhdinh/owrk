"""
Configuration settings for Auth Service
"""

from pydantic_settings import BaseSettings
from typing import List
import os
from urllib.parse import quote_plus


# Read secrets from files or environment
DATABASE_PASSWORD: str = "secret123"
mysql_passwd_file = os.getenv("DATABASE_PASSWORD_FILE")
if mysql_passwd_file and os.path.exists(mysql_passwd_file):
    with open(mysql_passwd_file, "r") as f:
        DATABASE_PASSWORD = f.read().strip()


# JWT Settings
JWT_SECRET: str = "your-super-secret-jwt-key-change-in-production"
jwt_secret_file = os.getenv("JWT_SECRET_KEY_FILE")
if jwt_secret_file and os.path.exists(jwt_secret_file):
    with open(jwt_secret_file, "r") as f:
        JWT_SECRET = f.read().strip()

MONGO_PASSWD: str = "secret123"
mongo_passwd_file = os.getenv("MONGO_PASSWD_FILE")
if mongo_passwd_file and os.path.exists(mongo_passwd_file):
    with open(mongo_passwd_file, "r") as f:
        MONGO_PASSWD = f.read().strip()


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables
    """

    # Application
    APP_NAME: str = "Asset Management - Auth Service"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = ENVIRONMENT == "development"

    # Database - MySQL (Write DB)
    DATABASE_USER: str = os.getenv("DATABASE_USER", "admin")
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", "auth_db")
    DATABASE_HOST: str = os.getenv("DATABASE_HOST", "mysql")
    DATABASE_PORT: str = os.getenv("DATABASE_PORT", "3306")

    DATABASE_URL: str = (
        f"mysql+pymysql://{DATABASE_USER}:{quote_plus(DATABASE_PASSWORD)}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}?charset=utf8mb4"
    )

    # MongoDB (Read DB for CQRS)
    MONGODB_HOST: str = os.getenv("MONGODB_HOST", "mongodb")
    MONGODB_PORT: str = os.getenv("MONGODB_PORT", "27017")
    MONGODB_URL: str = (
        f"mongodb://admin:{quote_plus(MONGO_PASSWD)}@{MONGODB_HOST}:{MONGODB_PORT}/"
    )
    MONGODB_DB_NAME: str = "asset_management_read"

    # RabbitMQ
    RABBITMQ_HOST: str = os.getenv("RABBITMQ_HOST", "rabbitmq")
    RABBITMQ_PORT: str = os.getenv("RABBITMQ_PORT", "5672")
    RABBITMQ_URL: str = f"amqp://guest:guest@{RABBITMQ_HOST}:{RABBITMQ_PORT}/"

    # Redis
    REDIS_HOST: str = os.getenv("REDIS_HOST", "redis")
    REDIS_PORT: str = os.getenv("REDIS_PORT", "6379")
    REDIS_URL: str = f"redis://{REDIS_HOST}:{REDIS_PORT}"

    # JWT Settings
    JWT_SECRET: str = JWT_SECRET  # Use the global variable loaded from file
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480  # 8 hours
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # MFA/OTP Settings
    MFA_ISSUER: str = "AssetManagement"
    MFA_BACKUP_CODES_COUNT: int = 10

    # Active Directory Settings
    AD_SERVER: str = os.getenv("AD_SERVER", "ldap://ad.company.local")
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
