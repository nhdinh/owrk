from typing import Annotated
import ipaddress

from pydantic import BaseModel, AfterValidator


def is_ipaddress(addr: str):
    if addr.strip() == "":
        raise ValueError(f"{addr} is not a valid ip address")

    ip_object = ipaddress.ip_address(addr)

    if isinstance(ip_object, ipaddress.IPv4Address) or isinstance(
        ip_object, ipaddress.IPv6Address
    ):
        return addr


def is_hostname(value: str):
    import re

    if len(value) > 255:
        raise ValueError(f"{value} is not a valid hostname")

    if value[-1] == ".":
        value = value[:-1]  # strip exactly one dot from the right, if present

    allowed = re.compile("(?!-)[A-Z\d-]{1,63}(?<!-)$", re.IGNORECASE)

    if all(allowed.match(x) for x in value.split(".")):
        return value.strip()
    else:
        raise ValueError(f"{value} is not a valid hostname")


IPAddress = Annotated[str, AfterValidator(is_ipaddress)]

HostName = Annotated[str, AfterValidator(is_hostname)]


class ServiceBase(BaseModel):
    name: str

    hostname: HostName
    port: int

    health_endpoint: str


class ServiceRegister(ServiceBase):
    pass


class ServiceStatus(ServiceBase):
    address: IPAddress

    last_check: float

    response_time: float
    status: str
