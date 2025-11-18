"""
Redis Storage Layer for Service Registry
Provides real-time service discovery with fast read/write operations
"""

import json
import logging
from typing import Dict, Optional, List
from datetime import datetime
import redis

logger = logging.getLogger(__name__)


class RedisServiceStore:
    """
    Redis-based storage for active service registrations
    Optimized for high-frequency updates and fast lookups
    """

    def __init__(self, redis_client: redis.Redis):
        """
        Initialize Redis storage

        Args:
            redis_client: Redis client instance
        """
        self.redis = redis_client
        self.SERVICES_HASH = "services:active"
        self.SERVICE_STATUS_PREFIX = "service:status:"
        self.SERVICE_HISTORY_PREFIX = "service:history:"
        self.MAX_HISTORY_ITEMS = 100

    def register(self, service_data: dict) -> bool:
        """
        Register or update a service

        Args:
            service_data: Service information dictionary

        Returns:
            bool: True if successful
        """
        try:
            service_name = service_data["name"]
            service_data["last_updated"] = datetime.now().timestamp()

            # Store in hash for O(1) lookup of all services
            self.redis.hset(
                self.SERVICES_HASH, service_name, json.dumps(service_data)
            )

            # Store individual service key for additional metadata
            service_key = f"{self.SERVICE_STATUS_PREFIX}{service_name}"
            self.redis.set(service_key, json.dumps(service_data))

            # Add to history timeline (capped list)
            history_key = f"{self.SERVICE_HISTORY_PREFIX}{service_name}"
            history_entry = {
                "timestamp": service_data["last_updated"],
                "status": service_data.get("status", "unknown"),
                "response_time": service_data.get("response_time", 0),
            }
            self.redis.lpush(history_key, json.dumps(history_entry))
            self.redis.ltrim(history_key, 0, self.MAX_HISTORY_ITEMS - 1)

            logger.info(f"✅ Registered {service_name} in Redis")
            return True

        except Exception as e:
            logger.error(f"❌ Redis registration error: {e}")
            return False

    def get(self, service_name: str) -> Optional[dict]:
        """
        Get service by name

        Args:
            service_name: Name of the service

        Returns:
            Service data dict or None if not found
        """
        try:
            data = self.redis.hget(self.SERVICES_HASH, service_name)
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            logger.error(f"❌ Error getting service {service_name}: {e}")
            return None

    def get_all(self) -> Dict[str, dict]:
        """
        Get all registered services

        Returns:
            Dictionary of all services {service_name: service_data}
        """
        try:
            services = {}
            all_data = self.redis.hgetall(self.SERVICES_HASH)

            for name_bytes, data_bytes in all_data.items():
                name = name_bytes.decode("utf-8")
                services[name] = json.loads(data_bytes)

            return services
        except Exception as e:
            logger.error(f"❌ Error getting all services: {e}")
            return {}

    def update_status(
        self, service_name: str, status: str, response_time: float
    ) -> bool:
        """
        Update service health status

        Args:
            service_name: Name of the service
            status: Health status (healthy, down, etc.)
            response_time: Response time in milliseconds

        Returns:
            bool: True if successful
        """
        try:
            service = self.get(service_name)
            if not service:
                logger.warning(f"Service {service_name} not found for status update")
                return False

            # Update service data
            service["status"] = status
            service["response_time"] = response_time
            service["last_check"] = datetime.now().timestamp()

            # Save updated data
            self.redis.hset(self.SERVICES_HASH, service_name, json.dumps(service))

            # Update individual service key
            service_key = f"{self.SERVICE_STATUS_PREFIX}{service_name}"
            self.redis.set(service_key, json.dumps(service))

            # Add to history
            history_key = f"{self.SERVICE_HISTORY_PREFIX}{service_name}"
            history_entry = {
                "timestamp": service["last_check"],
                "status": status,
                "response_time": response_time,
            }
            self.redis.lpush(history_key, json.dumps(history_entry))
            self.redis.ltrim(history_key, 0, self.MAX_HISTORY_ITEMS - 1)

            return True

        except Exception as e:
            logger.error(f"❌ Error updating status for {service_name}: {e}")
            return False

    def delete(self, service_name: str) -> bool:
        """
        Remove service from registry

        Args:
            service_name: Name of the service to remove

        Returns:
            bool: True if successful
        """
        try:
            # Remove from main hash
            self.redis.hdel(self.SERVICES_HASH, service_name)

            # Remove individual key
            service_key = f"{self.SERVICE_STATUS_PREFIX}{service_name}"
            self.redis.delete(service_key)

            # Keep history for audit trail (don't delete)

            logger.info(f"🗑️  Removed {service_name} from Redis registry")
            return True

        except Exception as e:
            logger.error(f"❌ Error deleting service {service_name}: {e}")
            return False

    def get_history(self, service_name: str, limit: int = 20) -> List[dict]:
        """
        Get recent history for a service

        Args:
            service_name: Name of the service
            limit: Number of history items to retrieve

        Returns:
            List of history entries
        """
        try:
            history_key = f"{self.SERVICE_HISTORY_PREFIX}{service_name}"
            history_items = self.redis.lrange(history_key, 0, limit - 1)

            return [json.loads(item) for item in history_items]

        except Exception as e:
            logger.error(f"❌ Error getting history for {service_name}: {e}")
            return []

    def get_service_count(self) -> int:
        """
        Get total number of registered services

        Returns:
            int: Number of services
        """
        try:
            return self.redis.hlen(self.SERVICES_HASH)
        except Exception as e:
            logger.error(f"❌ Error getting service count: {e}")
            return 0

    def get_healthy_count(self) -> int:
        """
        Get number of healthy services

        Returns:
            int: Number of healthy services
        """
        try:
            services = self.get_all()
            return sum(1 for s in services.values() if s.get("status") == "healthy")
        except Exception as e:
            logger.error(f"❌ Error getting healthy count: {e}")
            return 0

    def cleanup_stale_services(self, max_age_seconds: int = 600) -> List[str]:
        """
        Mark services as down if they haven't sent heartbeat

        Args:
            max_age_seconds: Maximum age before marking as stale (default 10 minutes)

        Returns:
            List of service names that were marked as down
        """
        try:
            stale_services = []
            all_services = self.get_all()
            current_time = datetime.now().timestamp()

            for name, service in all_services.items():
                last_check = service.get("last_check", 0)

                # If no heartbeat for max_age_seconds, mark as down
                if current_time - last_check > max_age_seconds:
                    if service.get("status") != "down":
                        self.update_status(name, "down", 0)
                        stale_services.append(name)
                        logger.warning(
                            f"⚠️  Marked {name} as down (no heartbeat for {int(current_time - last_check)}s)"
                        )

            return stale_services

        except Exception as e:
            logger.error(f"❌ Error cleaning up stale services: {e}")
            return []

    def get_statistics(self) -> dict:
        """
        Get registry statistics

        Returns:
            Dictionary with statistics
        """
        try:
            services = self.get_all()
            total = len(services)
            healthy = sum(1 for s in services.values() if s.get("status") == "healthy")
            down = sum(1 for s in services.values() if s.get("status") == "down")

            # Calculate average response time for healthy services
            healthy_services = [
                s for s in services.values() if s.get("status") == "healthy"
            ]
            avg_response_time = (
                sum(s.get("response_time", 0) for s in healthy_services)
                / len(healthy_services)
                if healthy_services
                else 0
            )

            return {
                "total_services": total,
                "healthy_services": healthy,
                "down_services": down,
                "average_response_time": round(avg_response_time, 2),
                "timestamp": datetime.now().timestamp(),
            }

        except Exception as e:
            logger.error(f"❌ Error getting statistics: {e}")
            return {}
