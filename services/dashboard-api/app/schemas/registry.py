from typing import Optional
from uuid import UUID
from pydantic import BaseModel, validator


class ServiceBase(BaseModel):
    """Base Service Model"""

    service_id: UUID
    name: str
    description: Optional[str]
    url: str


class ServiceRegister(ServiceBase):
    @validator("url")
    def validate_url(cls, value: str):
        if not value.startswith("http://"):
            raise ValueError("URL must be starts with http:// or https://")

        return value


class ServiceResponse(BaseModel):
    # TODO: Make it inherit ServiceBase
    name: str
