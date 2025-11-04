from pydantic import BaseModel


class ServiceBase(BaseModel):
    name: str
    address: str
    port: int
    health_endpoint: str


class ServiceRegister(ServiceBase):
    pass


class ServiceStatus(ServiceBase):
    last_check: float
    response_time: float
    status: str
