"""
Configuration settings for Procurement Service
"""

import os
from typing import Optional
from urllib.parse import quote_plus


class Settings:
    """Application settings"""

    # Application
    APP_NAME: str = "Procurement Management Service"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    TESTING: bool = os.getenv("TESTING", "False").lower() == "true"
    API_PREFIX: str = "/api/v1"
    SERVICE_NAME: str = "procurement-api"
    SERVICE_HOSTNAME: str = "procurement-api"
    SERVICE_PORT: int = 8004
    SERVICE_HEALTH_ENDPOINT: str = "/health"

    # Service Registry
    SERVICE_REGISTRY_URL: str = os.getenv("SERVICE_REGISTRY_URL", "http://service-registry:3000")

    # Database - MySQL (Write)
    DATABASE_USER: str = os.getenv("DATABASE_USER", "officework")
    DATABASE_PASSWORD: str = "secret123"  # Default
    DATABASE_HOST: str = os.getenv("DATABASE_HOST", "mysql")
    DATABASE_PORT: int = int(os.getenv("DATABASE_PORT", "3306"))
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", "procurement_db")

    # Read password from file if provided
    DB_PASSWORD_FILE: Optional[str] = os.getenv("DB_PASSWORD_FILE")
    if DB_PASSWORD_FILE and os.path.exists(DB_PASSWORD_FILE):
        with open(DB_PASSWORD_FILE, "r") as f:
            DB_PASSWORD = f.read().strip()

    DATABASE_URL: str = (
        f"mysql+pymysql://{DATABASE_USER}:{quote_plus(DB_PASSWORD)}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"
    )

    # MongoDB (Read - for CQRS)
    MONGODB_HOST: str = os.getenv("MONGODB_HOST", "mongodb")
    MONGODB_PORT: int = int(os.getenv("MONGODB_PORT", "27017"))
    MONGODB_USER: str = os.getenv("MONGODB_USER", "admin")
    MONGODB_PASSWORD: str = "secret123"  # Default

    # Read MongoDB password from file if provided
    MONGODB_PASSWORD_FILE: Optional[str] = os.getenv("MONGODB_PASSWORD_FILE")
    if MONGODB_PASSWORD_FILE and os.path.exists(MONGODB_PASSWORD_FILE):
        with open(MONGODB_PASSWORD_FILE, "r") as f:
            MONGODB_PASSWORD = f.read().strip()

    MONGODB_DATABASE: str = os.getenv("MONGODB_DATABASE", "procurement_read_db")
    MONGODB_URL: str = (
        f"mongodb://{MONGODB_USER}:{quote_plus(MONGODB_PASSWORD)}@{MONGODB_HOST}:{MONGODB_PORT}/"
    )

    # Redis
    REDIS_HOST: str = os.getenv("REDIS_HOST", "redis")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_URL: str = f"redis://{REDIS_HOST}:{REDIS_PORT}"

    # RabbitMQ
    RABBITMQ_HOST: str = os.getenv("RABBITMQ_HOST", "rabbitmq")
    RABBITMQ_PORT: int = int(os.getenv("RABBITMQ_PORT", "5672"))
    RABBITMQ_URL: str = f"amqp://guest:guest@{RABBITMQ_HOST}:{RABBITMQ_PORT}/"

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

    # File Upload
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "/app/uploads")
    MAX_UPLOAD_SIZE: int = int(os.getenv("MAX_UPLOAD_SIZE", "10485760"))  # 10MB
    ALLOWED_EXTENSIONS: set = {
        ".pdf",
        ".jpg",
        ".jpeg",
        ".png",
        ".doc",
        ".docx",
        ".xls",
        ".xlsx",
    }

    # Auth Service URL
    AUTH_SERVICE_URL: str = os.getenv(
        "AUTH_SERVICE_URL", "http://auth-api-service:8000"
    )

    # Asset Service URL
    ASSET_SERVICE_URL: str = os.getenv(
        "ASSET_SERVICE_URL", "http://asset-api-service:8000"
    )


settings = Settings()
