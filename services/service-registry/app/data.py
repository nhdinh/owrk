from datetime import datetime
import json
import logging
import os

from .schema import ServiceStatus

logger = logging.getLogger(__name__)


service_file_path = os.getenv("SERVICES_CACHE_FILE", "/tmp/services.json")
service_name = "service-registry"
service_data = ServiceStatus(
    name=service_name,
    address="service-registry",
    port=3000,
    last_check=datetime.timestamp(datetime.now()),
    status="healthy",
    response_time=0,
    health_endpoint="/health",
)

this_service = {service_name: service_data}


def load_services():
    if os.path.exists(service_file_path):
        logger.info(f"Read cached data from {service_file_path}")
        with open(service_file_path, "r") as f:
            saved_services = json.loads(f.read())

            if service_name not in saved_services.keys():
                saved_services[service_name] = service_data

            return saved_services

    return this_service


def save_services(g_services):
    with open(service_file_path, "w+") as f:
        f.write(json.dumps(g_services, indent=4))

        logger.info(f"Save services data to file")


def reset_services():
    os.unlink(service_file_path)

    return {service_name: service_data}


g_services = {}
