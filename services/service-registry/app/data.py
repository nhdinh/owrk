from datetime import datetime
import json
import logging
import os

logger = logging.getLogger(__name__)


service_file_path = os.getenv("SERVICES_CACHE_FILE", "/tmp/services.json")
this_service = {
    "service-registry": {
        "name": "service-registry",
        "address": "service-registry",
        "port": 3000,
        "last_check": datetime.timestamp(datetime.now()),
        "status": "healthy",
        "response_time": 0,
        "heath_endpoint": "/health",
    }
}


def load_services():
    if os.path.exists(service_file_path):
        logger.info(f"Read cached data from {service_file_path}")
        with open(service_file_path, "r") as f:
            saved_services = json.loads(f.read())

            if "service-registry" not in saved_services.keys():
                saved_services["service-registry"] = this_service["service-registry"]

            return saved_services

    return this_service


def save_services(g_services):
    with open(service_file_path, "w+") as f:
        f.write(json.dumps(g_services))

        logger.info(f"Save services data to file")


def reset_services():
    os.unlink(service_file_path)

    return this_service


g_services = {}
