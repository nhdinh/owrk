from pydantic import BaseModel
from sqlalchemy import Column, String


class ServiceResponse(BaseModel):
    """ServiceResponse model"""

    __tablename__ = "service_response"
    __table_args__ = {"schema": "registry_db"}

    hostname = Column(String(255), nullable=False, unique=True, index=True)
