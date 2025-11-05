"""
Configuration settings for Dashboard API
"""

from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings"""

    # Service
    SERVICE_NAME: str = "dashboard-api"
    SERVICE_HOSTNAME: str = "dashboard-api"
    SERVICE_PORT: int = int(os.getenv("SERVICE_PORT", 8000))
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"

    # MySQL Database
    MYSQL_HOST: str = "mysql"
    MYSQL_PORT: int = 3306
    MYSQL_USER: str = "officework_dbu"
    MYSQL_DATABASE: str = "auth_db"

    # MongoDB
    MONGODB_HOST: str = "mongodb"
    MONGODB_PORT: int = 27017
    MONGODB_USER: str = "admin"
    MONGODB_DATABASE: str = "officework_read"

    # Redis
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379

    # RabbitMQ
    RABBITMQ_HOST: str = os.getenv("RABBITMQ_HOST", "rabbitmq")
    RABBITMQ_PORT: str = os.getenv("RABBITMQ_PORT", "5672")
    RABBITMQ_URL: str = f"amqp://guest:guest@{RABBITMQ_HOST}:{RABBITMQ_PORT}/"

    # JWT
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # External APIs
    ASSET_API_URL: str = "http://asset-api:8000/api/v1"
    AUTH_API_URL: str = "http://auth-api:8000/api/v1"

    # Secrets (read from files)
    MYSQL_PASSWORD: Optional[str] = None
    MONGODB_PASSWORD: Optional[str] = None
    JWT_SECRET_KEY: Optional[str] = None

    # Ping service health
    SERVICES_HEALTH_POLL_DURATION: int = 5

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Read secrets from files if they exist
        self._read_secret("MYSQL_PASSWORD", "/run/secrets/mysql_user_passwd")
        self._read_secret("MONGODB_PASSWORD", "/run/secrets/mongo_passwd")
        self._read_secret("JWT_SECRET_KEY", "/run/secrets/jwt_secret_key")

    def _read_secret(self, attr_name: str, file_path: str):
        """Read secret from file"""
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                setattr(self, attr_name, f.read().strip())

    @property
    def DATABASE_URL(self) -> str:
        """MySQL connection URL"""
        return f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"

    @property
    def MONGODB_URL(self) -> str:
        """MongoDB connection URL"""
        from urllib.parse import quote_plus

        username = quote_plus(self.MONGODB_USER)
        password = quote_plus(self.MONGODB_PASSWORD) if self.MONGODB_PASSWORD else ""
        return f"mongodb://{username}:{password}@{self.MONGODB_HOST}:{self.MONGODB_PORT}/?authSource=admin"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
