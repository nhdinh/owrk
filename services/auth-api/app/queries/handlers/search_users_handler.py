"""
SearchUsersHandler - Query handler for full-text search
"""
import logging
from typing import List, Dict
from app.core.message_bus import QueryHandler
from app.schemas.queries.user_queries import GetUsersListQuery  # Reuse for search
from app.read_repositories.user_read_repository import UserReadRepository

logger = logging.getLogger(__name__)


class SearchUsersHandler(QueryHandler[GetUsersListQuery, List[Dict]]):
    """
    Handler for user search queries
    Uses MongoDB text search
    """

    def __init__(self, user_read_repo: UserReadRepository):
        self.user_read_repo = user_read_repo

    async def handle(self, query: GetUsersListQuery) -> List[Dict]:
        """
        Search users by name, email, or username

        Args:
            query: GetUsersListQuery with search term

        Returns:
            List of matching users
        """
        if not query.search:
            return []

        logger.debug(f"Searching users: {query.search}")

        users = await self.user_read_repo.search_users(
            search_term=query.search,
            skip=query.skip,
            limit=query.limit
        )

        logger.debug(f"Found {len(users)} matching users")

        return users
