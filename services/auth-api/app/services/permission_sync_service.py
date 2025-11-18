"""
Permission Sync Service - Discovers and syncs permissions from all microservices
"""

import logging
import httpx
from typing import List, Dict, Any
from datetime import datetime

from app.core.unit_of_work import UnitOfWork
from app.models.role import Permission
from app.core.config import settings

logger = logging.getLogger(__name__)


class PermissionSyncService:
    """
    Service for discovering and syncing permissions from all microservices.

    This service:
    1. Fetches registered services from service-registry
    2. Calls /permissions endpoint on each service
    3. Syncs discovered permissions with the database
    4. Tracks which service owns each permission
    """

    def __init__(self):
        self.service_registry_url = settings.SERVICE_REGISTRY_URL
        self.timeout = 10  # seconds

    async def sync_all_permissions(self) -> Dict[str, Any]:
        """
        Main sync method - discovers services and syncs all permissions.

        Returns:
            dict: Sync results with statistics
        """
        logger.info("🔄 Starting permission sync from all services")

        results = {
            "timestamp": datetime.utcnow().isoformat(),
            "services_checked": 0,
            "services_synced": 0,
            "permissions_added": 0,
            "permissions_updated": 0,
            "permissions_deactivated": 0,
            "errors": [],
        }

        try:
            # 1. Discover services from service-registry
            services = await self._discover_services()
            results["services_checked"] = len(services)

            # 2. Sync permissions from each service
            for service in services:
                try:
                    await self._sync_service_permissions(service, results)
                    results["services_synced"] += 1
                except Exception as e:
                    error_msg = f"Failed to sync {service['name']}: {str(e)}"
                    logger.error(error_msg)
                    results["errors"].append(error_msg)

            # 3. Deactivate permissions from services that no longer exist
            await self._deactivate_orphaned_permissions(
                [s["name"] for s in services], results
            )

            logger.info(
                f"✅ Permission sync complete: "
                f"{results['permissions_added']} added, "
                f"{results['permissions_updated']} updated, "
                f"{results['permissions_deactivated']} deactivated"
            )

        except Exception as e:
            error_msg = f"Permission sync failed: {str(e)}"
            logger.error(error_msg)
            results["errors"].append(error_msg)

        return results

    async def _discover_services(self) -> List[Dict[str, Any]]:
        """
        Fetch list of registered services from service-registry.

        Returns:
            list: List of service dictionaries with name, address, port
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.service_registry_url}/services")
                response.raise_for_status()
                data = response.json()

                # Service registry returns a dict of services, convert to list
                # Filter services that are healthy and are API services (not frontends)
                services = [
                    service for service in data.values()
                    if service.get("status") == "healthy" and service.get("name", "").endswith("-api")
                ]

                logger.info(f"📋 Discovered {len(services)} healthy API services")
                return services

        except Exception as e:
            logger.error(f"Failed to discover services: {str(e)}")
            return []

    async def _sync_service_permissions(
        self, service: Dict[str, Any], results: Dict[str, Any]
    ) -> None:
        """
        Sync permissions from a single service.

        Args:
            service: Service info dict (name, address, port)
            results: Results dict to update with statistics
        """
        service_name = service.get("name")
        service_url = f"http://{service.get('address')}:{service.get('port')}"

        logger.info(f"🔍 Syncing permissions from {service_name}")

        try:
            # Fetch permissions from service
            permissions = await self._fetch_service_permissions(service_url)

            if not permissions:
                logger.info(f"⚠️  {service_name} has no permissions to sync")
                return

            # Sync to database - commit after each permission to prevent cascading failures
            for perm_data in permissions:
                try:
                    with UnitOfWork() as uow:
                        self._sync_permission(
                            uow, service_name, perm_data, results
                        )
                        # Commit happens automatically when exiting UnitOfWork context
                        # The UnitOfWork __exit__ handles commit/rollback
                except Exception as e:
                    # Log the full error but don't fail the entire service sync
                    error_msg = str(e)
                    if "0 were matched" not in error_msg:
                        logger.error(
                            f"Failed to sync permission {perm_data.get('code')}: {error_msg}"
                        )
                    # If it's just a "0 rows matched" error, it means values were already correct
                    # This is fine and we can continue

            logger.info(
                f"✅ Synced {len(permissions)} permissions from {service_name}"
            )

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                logger.info(f"⚠️  {service_name} does not expose /permissions endpoint")
            else:
                raise

    async def _fetch_service_permissions(self, service_url: str) -> List[Dict[str, Any]]:
        """
        Fetch permissions from a service's /permissions endpoint.

        Args:
            service_url: Base URL of the service

        Returns:
            list: List of permission dictionaries
        """
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(f"{service_url}/permissions")
            response.raise_for_status()
            data = response.json()

            return data.get("permissions", [])

    def _sync_permission(
        self,
        uow: UnitOfWork,
        service_name: str,
        perm_data: Dict[str, Any],
        results: Dict[str, Any],
    ) -> None:
        """
        Sync a single permission to the database.

        Args:
            uow: Unit of Work instance
            service_name: Name of the service that owns this permission
            perm_data: Permission data dict
            results: Results dict to update with statistics
        """
        code = perm_data.get("code")
        name = perm_data.get("name")
        resource = perm_data.get("resource")
        action = perm_data.get("action")
        description = perm_data.get("description")

        # Generate slug to check for existing permission
        from app.core.utils import generate_slug
        slug = generate_slug(f"{resource}-{action}")

        # Check if permission already exists (by slug, which is unique)
        existing = uow.db.query(Permission).filter(Permission.slug == slug).first()

        if existing:
            # Update existing permission
            updated = False

            if existing.name != name:
                logger.info(f"🔄 {slug}: updating name from '{existing.name}' to '{name}'")
                existing.name = name
                updated = True

            if existing.resource != resource:
                existing.resource = resource
                updated = True

            if existing.action != action:
                existing.action = action
                updated = True

            if existing.description != description:
                existing.description = description
                updated = True

            if existing.service != service_name:
                logger.info(f"🔄 {slug}: updating service from '{existing.service}' to '{service_name}'")
                existing.service = service_name
                updated = True

            if updated:
                results["permissions_updated"] += 1
                logger.debug(f"📝 Updated permission: {name}")

        else:
            # Create new permission
            import uuid as uuid_module

            new_permission = Permission(
                id=uuid_module.uuid4(),  # Generate UUID object (not string)
                name=name,
                slug=slug,  # Use the slug we already generated
                resource=resource,
                action=action,
                description=description,
                service=service_name,
            )
            uow.db.add(new_permission)
            # Don't flush here - let UnitOfWork handle it on commit
            results["permissions_added"] += 1
            logger.debug(f"✨ Added new permission: {name}")

    async def _deactivate_orphaned_permissions(
        self, active_services: List[str], results: Dict[str, Any]
    ) -> None:
        """
        Mark permissions as inactive if their service no longer exists.

        Args:
            active_services: List of currently active service names
            results: Results dict to update with statistics
        """
        with UnitOfWork() as uow:
            # Find permissions from services that are no longer registered
            orphaned = (
                uow.db.query(Permission)
                .filter(
                    Permission.service.isnot(None),
                    Permission.service.notin_(active_services),
                )
                .all()
            )

            if orphaned:
                logger.warning(
                    f"⚠️  Found {len(orphaned)} orphaned permissions from inactive services"
                )

                # Note: We don't actually delete or deactivate them yet
                # Just log them for manual review
                for perm in orphaned:
                    logger.warning(
                        f"   - {perm.name} (service: {perm.service})"
                    )

            results["permissions_deactivated"] = len(orphaned)


# Global singleton instance
permission_sync_service = PermissionSyncService()
