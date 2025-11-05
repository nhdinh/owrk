from datetime import datetime

import json
import logging
import os


from .schema import ServiceStatus
from .helper import get_host_address


logger = logging.getLogger(__name__)


service_file_path = os.getenv("SERVICES_CACHE_FILE", "/tmp/services.json")

service_name = "service-registry"

service_data = ServiceStatus(
    name=service_name,
    hostname="service-registry",
    address=get_host_address(service_name),
    port=3000,
    last_check=datetime.timestamp(datetime.now()),
    status="healthy",
    response_time=0,
    health_endpoint="/health",
)


this_service = {service_name: service_data}


def load_services():
    if os.path.exists(service_file_path):
        services = {}
        logger.info(f"Read cached data from {service_file_path}")

        try:
            with open(service_file_path, "r") as f:
                services = json.loads(f.read().strip())

                if service_name not in services.keys():
                    services[service_name] = dict(service_data)

            for name, service in services.items():
                services[name]["address"] = get_host_address(service["hostname"])

            save_services(services)

            return services
        except:
            pass

    services = {service_name: dict(service_data)}
    save_services(services)

    return services


def save_services(g_services):
    with open(service_file_path, "w+") as f:
        f.write(json.dumps(g_services, indent=4))

        logger.info(f"Save services data to file")


def reset_services():
    os.unlink(service_file_path)

    return {service_name: service_data}


g_services = {}
