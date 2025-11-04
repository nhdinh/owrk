"""
Configuration settings for Asset Service
"""

import os
from typing import Optional
from urllib.parse import quote_plus


class Settings:
    """Application settings"""

    # Application
    APP_NAME: str = "Asset Management Service"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    TESTING: bool = os.getenv("TESTING", "False").lower() == "true"
    API_PREFIX: str = "/api/v1"

    # Database - MySQL (Write)
    DATABASE_USER: str = os.getenv("DATABASE_USER", "admin")
    DATABASE_PASSWORD: str = "secret123"  # Default
    DATABASE_HOST: str = os.getenv("DATABASE_HOST", "mysql")
    DATABASE_PORT: int = int(os.getenv("DATABASE_PORT", "3306"))
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", "asset_db")

    # Read password from file if provided
    DATABASE_PASSWORD_FILE: Optional[str] = os.getenv("DATABASE_PASSWORD_FILE")
    if DATABASE_PASSWORD_FILE and os.path.exists(DATABASE_PASSWORD_FILE):
        with open(DATABASE_PASSWORD_FILE, "r") as f:
            DATABASE_PASSWORD = f.read().strip()

    DATABASE_URL: str = (
        f"mysql+pymysql://{DATABASE_USER}:{quote_plus(DATABASE_PASSWORD)}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"
    )

    # MongoDB (Read - for CQRS)
    MONGODB_HOST: str = os.getenv("MONGODB_HOST", "mongodb")
    MONGODB_PORT: int = int(os.getenv("MONGODB_PORT", "27017"))
    MONGODB_USER: str = os.getenv("MONGODB_USER", "admin")
    MONGODB_PASSWORD: str = "secret123"  # Default

    # Read MongoDB password from file if provided
    MONGO_PASSWD_FILE: Optional[str] = os.getenv("MONGO_PASSWD_FILE")
    if MONGO_PASSWD_FILE and os.path.exists(MONGO_PASSWD_FILE):
        with open(MONGO_PASSWD_FILE, "r") as f:
            MONGODB_PASSWORD = f.read().strip()

    MONGODB_DB_NAME: str = os.getenv("MONGODB_DB_NAME", "asset_read_db")
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
    JWT_SECRET: str = "your-secret-key-change-this"  # Default
    JWT_SECRET_KEY_FILE: Optional[str] = os.getenv("JWT_SECRET_KEY_FILE")
    if JWT_SECRET_KEY_FILE and os.path.exists(JWT_SECRET_KEY_FILE):
        with open(JWT_SECRET_KEY_FILE, "r") as f:
            JWT_SECRET = f.read().strip()

    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")

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

    # Depreciation Calculation
    DEPRECIATION_DAY_OF_MONTH: int = int(
        os.getenv("DEPRECIATION_DAY_OF_MONTH", "1")
    )  # Run on 1st of each month

    # Auth Service URL
    AUTH_SERVICE_URL: str = os.getenv(
        "AUTH_SERVICE_URL", "http://auth-api-service:8000"
    )


settings = Settings()
