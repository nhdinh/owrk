"""
GetUserByIdHandler - Query handler for getting user by ID from MongoDB
"""

import logging
from typing import Optional, Dict
from app.core.message_bus import QueryHandler
from app.schemas.queries.user_queries import GetUserByIdQuery
from app.read_repositories.user_read_repository import UserReadRepository

logger = logging.getLogger(__name__)


class GetUserByIdHandler(QueryHandler[GetUserByIdQuery, Optional[Dict]]):
    """
    Handler for GetUserByIdQuery
    Reads from MongoDB read model for fast queries
    """

    def __init__(self, user_read_repo: UserReadRepository):
        self.user_read_repo = user_read_repo

    async def handle(self, query: GetUserByIdQuery) -> Optional[Dict]:
        """
        Get user by ID from MongoDB

        Args:
            query: GetUserByIdQuery with user_id

        Returns:
            User dict or None if not found
        """
        logger.debug(f"Getting user by ID: {query.user_id}")

        user = await self.user_read_repo.get_by_id(query.user_id)

        if user:
            logger.debug(f"Found user: {user.get('email')}")
        else:
            logger.debug(f"User not found: {query.user_id}")

        return user
