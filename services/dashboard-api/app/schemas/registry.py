from typing import Optional
from uuid import UUID
from pydantic import BaseModel, validator


class ServiceBase(BaseModel):
    """Base Service Model"""

    node_id: UUID
    name: str
    description: Optional[str]
    address: str
    service_port: int


class ServiceRegister(ServiceBase):
    @validator("address")
    def validate_url(cls, value: str):
        if not value.startswith("http://"):
            raise ValueError("Node address must be starts with http:// or https://")

        return value


class ServiceResponse(BaseModel):
    # TODO: Make it inherit ServiceBase
    name: str
