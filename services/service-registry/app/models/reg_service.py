import enum
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, Enum as SQLEnum


class RegisteredServiceStatus(str, enum.Enum):
    HEALTHY = "HEALTHY"
    DOWN = "DOWN"


class RegisteredService(BaseModel):
    """Service model"""

    __tablename__ = "services"
    __table_args__ = {"schema": "registry_db"}

    name = Column(String(255), nullable=False)
    hostname = Column(String(255), nullable=False, unique=True, index=True)
    hostport = Column(Integer, nullable=False)
    health_endpoint = Column(String(255))
    description = Column(String(255), nullable=True, default="")
    status = Column(
        SQLEnum(RegisteredServiceStatus),
        default=RegisteredServiceStatus.HEALTHY,
        nullable=False,
        index=True,
    )

    def __repr__(self) -> str:
        return f"<Service(name={self.name})>"
