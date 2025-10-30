"""
GetUsersListHandler - Query handler for getting paginated users list
"""
import logging
from typing import List, Dict
from app.core.message_bus import QueryHandler
from app.schemas.queries.user_queries import GetUsersListQuery
from app.read_repositories.user_read_repository import UserReadRepository

logger = logging.getLogger(__name__)


class GetUsersListHandler(QueryHandler[GetUsersListQuery, Dict]):
    """
    Handler for GetUsersListQuery
    Returns paginated list with filters
    """

    def __init__(self, user_read_repo: UserReadRepository):
        self.user_read_repo = user_read_repo

    async def handle(self, query: GetUsersListQuery) -> Dict:
        """
        Get users list with pagination and filters

        Args:
            query: GetUsersListQuery with pagination and filter params

        Returns:
            Dict with users list, total count, and pagination info
        """
        logger.debug(f"Getting users list: skip={query.skip}, limit={query.limit}")

        # Build MongoDB filters
        filters = {}
        if query.is_active is not None:
            filters["is_active"] = query.is_active
        if query.role_id is not None:
            filters["role_id"] = query.role_id
        if query.department_id is not None:
            filters["department_id"] = query.department_id

        # Get users
        users = await self.user_read_repo.find_all(
            skip=query.skip,
            limit=query.limit,
            filters=filters
        )

        # Get total count
        total = await self.user_read_repo.count_users(filters)

        logger.debug(f"Found {len(users)} users, total: {total}")

        return {
            "users": users,
            "total": total,
            "skip": query.skip,
            "limit": query.limit
        }
