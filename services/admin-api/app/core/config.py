"""
Configuration settings for Admin Service
"""

import os
from typing import Optional
from urllib.parse import quote_plus


class Settings:
    """Application settings"""

    # Application
    APP_NAME: str = "Admin Management Service"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    API_PREFIX: str = "/api/v1"

    # Database - MySQL
    DATABASE_USER: str = os.getenv("DATABASE_USER", "officework")
    DATABASE_PASSWORD: str = "secret123"  # Default
    DATABASE_HOST: str = os.getenv("DATABASE_HOST", "mysql")
    DATABASE_PORT: int = int(os.getenv("DATABASE_PORT", "3306"))
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", "admin_db")

    # Read password from file if provided
    DB_PASSWORD_FILE: Optional[str] = os.getenv("DB_PASSWORD_FILE")
    if DB_PASSWORD_FILE and os.path.exists(DB_PASSWORD_FILE):
        with open(DB_PASSWORD_FILE, "r") as f:
            DATABASE_PASSWORD = f.read().strip()

    DATABASE_URL: str = (
        f"mysql+pymysql://{DATABASE_USER}:{quote_plus(DATABASE_PASSWORD)}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"
    )

    # Redis
    REDIS_HOST: str = os.getenv("REDIS_HOST", "redis")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_URL: str = f"redis://{REDIS_HOST}:{REDIS_PORT}"

    # JWT (for authentication with Auth Service)
    SECRET_KEY: str = "your-secret-key-change-this"  # Default
    SECRET_KEY_FILE: Optional[str] = os.getenv("SECRET_KEY_FILE")
    if SECRET_KEY_FILE and os.path.exists(SECRET_KEY_FILE):
        with open(SECRET_KEY_FILE, "r") as f:
            SECRET_KEY = f.read().strip()

    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")

    # CORS
    ALLOWED_ORIGINS: list = os.getenv(
        "ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:8000"
    ).split(",")

    # Auth Service URL
    AUTH_SERVICE_URL: str = os.getenv("AUTH_SERVICE_URL", "http://auth-api:8000")

    # Service Registry URL
    SERVICE_REGISTRY_URL: str = os.getenv(
        "SERVICE_REGISTRY_URL", "http://service-registry:3000"
    )

    # Audit Log Settings
    AUDIT_LOG_RETENTION_DAYS: int = int(os.getenv("AUDIT_LOG_RETENTION_DAYS", "90"))
    SYSTEM_LOG_RETENTION_DAYS: int = int(os.getenv("SYSTEM_LOG_RETENTION_DAYS", "30"))


settings = Settings()
