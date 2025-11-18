"""
Configuration settings for Auth Service
"""

from enum import StrEnum
from pydantic_settings import BaseSettings
from typing import List
import os

MONGO_PASSWD: str = "secret123"
mongo_passwd_file = os.getenv("MONGO_PASSWD_FILE")
if mongo_passwd_file and os.path.exists(mongo_passwd_file):
    with open(mongo_passwd_file, "r") as f:
        MONGO_PASSWD = f.read().strip()


class HealthCheckMethods(StrEnum):
    PING = "PING"
    HTTPX = "HTTPX"


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables
    """

    # Application
    APP_NAME: str = "Service Registry"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = ENVIRONMENT == "development"
    SERVICE_NAME: str = "service-registry"
    SERVICE_PORT: int = 3000
    SERVICE_ADDRESS: str = "service-registry"

    # MongoDB
    MONGODB_HOST: str = os.getenv("MONGODB_HOST", "mongodb")
    MONGODB_PORT: str = os.getenv("MONGODB_PORT", "27017")
    MONGODB_USER: str = os.getenv("MONGODB_USER", "admin")
    MONGODB_URL: str = (
        f"mongodb://{MONGODB_USER}:{MONGO_PASSWD}@{MONGODB_HOST}:{MONGODB_PORT}/"
        f"?authSource=admin"  # Authenticate against admin database
    )
    MONGODB_DB_NAME: str = "service_registry"

    SERVICE_HEALTH_CHECK: HealthCheckMethods = HealthCheckMethods.HTTPX

    # Redis - Real-time storage
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_DB: int = int(os.getenv("REDIS_DB", "0"))

    # InfluxDB - Time-series metrics
    INFLUXDB_URL: str = os.getenv("INFLUXDB_URL", "http://localhost:8086")
    INFLUXDB_TOKEN: str = os.getenv("INFLUXDB_TOKEN", "my-super-secret-auth-token")
    INFLUXDB_ORG: str = os.getenv("INFLUXDB_ORG", "officework")
    INFLUXDB_BUCKET: str = os.getenv("INFLUXDB_BUCKET", "service_metrics")

    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
