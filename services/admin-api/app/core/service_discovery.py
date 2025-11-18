"""
Service Discovery Client
Communicates with service-registry to register and discover services
"""

import logging
import socket
from typing import Optional, Dict
import httpx
from app.core.config import settings

logger = logging.getLogger(__name__)


class ServiceDiscoveryClient:
    """Client for service discovery and registration"""

    def __init__(self, registry_url: str = "http://service-registry:3000"):
        self.registry_url = registry_url
        self.registered = False

    async def register(
        self,
        service_name: str,
        hostname: str,
        port: int,
        health_endpoint: str = "/health"
    ) -> bool:
        """
        Register service with the registry

        Args:
            service_name: Name of the service
            hostname: Hostname of the service
            port: Port number
            health_endpoint: Health check endpoint path

        Returns:
            bool: True if registration successful
        """
        try:
            # Get IP address from hostname
            address = socket.gethostbyname(hostname)

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.registry_url}/register",
                    json={
                        "name": service_name,
                        "hostname": hostname,
                        "address": address,
                        "port": port,
                        "health_endpoint": health_endpoint
                    },
                    timeout=5.0
                )

                if response.status_code == 201:
                    self.registered = True
                    logger.info(f"✅ Service {service_name} registered successfully")
                    logger.info(f"   Registry: {self.registry_url}")
                    logger.info(f"   Service: {hostname}:{port}")
                    return True
                else:
                    logger.error(f"❌ Failed to register service: {response.text}")
                    return False

        except Exception as e:
            logger.error(f"❌ Service registration error: {str(e)}")
            return False

    async def get_service(self, service_name: str) -> Optional[Dict]:
        """
        Get service information by name

        Args:
            service_name: Name of the service to look up

        Returns:
            Dict with service info or None if not found
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.registry_url}/services",
                    timeout=5.0
                )

                if response.status_code == 200:
                    services = response.json()
                    service = services.get(service_name)
                    if service:
                        return service
                    else:
                        logger.warning(f"Service {service_name} not found in registry")
                        return None
                else:
                    logger.warning(f"Failed to get services from registry: {response.status_code}")
                    return None

        except Exception as e:
            logger.error(f"Error getting service {service_name}: {str(e)}")
            return None

    async def get_service_url(self, service_name: str) -> Optional[str]:
        """
        Get full service URL (http://hostname:port)

        Args:
            service_name: Name of the service

        Returns:
            Service URL or None if not found
        """
        service = await self.get_service(service_name)
        if service:
            hostname = service.get("hostname")
            port = service.get("port")
            if hostname and port:
                return f"http://{hostname}:{port}"
        return None

    async def get_all_services(self) -> Dict:
        """
        Get all registered services

        Returns:
            Dict of all services
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.registry_url}/services",
                    timeout=5.0
                )

                if response.status_code == 200:
                    return response.json()
                else:
                    logger.error("Failed to get services list")
                    return {}

        except Exception as e:
            logger.error(f"Error getting services: {str(e)}")
            return {}


# Global service discovery client instance
service_discovery = ServiceDiscoveryClient(settings.SERVICE_REGISTRY_URL)


async def register_service():
    """Register this service with the registry"""
    await service_discovery.register(
        service_name=settings.SERVICE_NAME,
        hostname=settings.SERVICE_HOSTNAME,
        port=settings.SERVICE_PORT,
        health_endpoint=settings.SERVICE_HEALTH_ENDPOINT
    )


async def get_service_url(service_name: str, fallback_url: Optional[str] = None) -> str:
    """
    Get service URL with fallback

    Args:
        service_name: Name of the service to look up
        fallback_url: Fallback URL if service not found

    Returns:
        Service URL
    """
    url = await service_discovery.get_service_url(service_name)
    if url:
        return url

    if fallback_url:
        logger.warning(f"Service {service_name} not found, using fallback: {fallback_url}")
        return fallback_url

    raise ValueError(f"Service {service_name} not found and no fallback provided")
