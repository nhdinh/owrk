"""
GetUserHistoryHandler - Query handler for user version history
"""

import logging
from typing import List, Dict
from sqlalchemy.orm import Session
from app.core.message_bus import QueryHandler
from app.schemas.queries.user_queries import GetUserHistoryQuery
from app.models.user_history import UserHistory

logger = logging.getLogger(__name__)


class GetUserHistoryHandler(QueryHandler[GetUserHistoryQuery, Dict]):
    """
    Handler for GetUserHistoryQuery
    Returns user's version history from MySQL
    """

    def __init__(self):
        pass

    async def handle(self, query: GetUserHistoryQuery, db: Session) -> Dict:
        """
        Get user version history

        Args:
            query: GetUserHistoryQuery with user_id and pagination
            db: Database session for this request

        Returns:
            Dict with history entries and pagination info
        """
        logger.debug(f"Getting history for user ID: {query.user_id}")

        # Query history entries
        history_query = (
            db.query(UserHistory)
            .filter(UserHistory.user_id == query.user_id)
            .order_by(UserHistory.version.desc())
        )

        # Get total count
        total = history_query.count()

        # Apply pagination
        history_entries = history_query.offset(query.skip).limit(query.limit).all()

        # Convert to dicts
        history_data = []
        for entry in history_entries:
            history_data.append(
                {
                    "id": entry.id,
                    "version": entry.version,
                    "changed_at": (
                        entry.changed_at.isoformat() if entry.changed_at else None
                    ),
                    "changed_by": entry.changed_by,
                    "change_reason": entry.change_reason,
                    "change_type": entry.change_type,
                    "email": entry.email,
                    "full_name": entry.full_name,
                    "is_active": entry.is_active,
                    "role_id": entry.role_id,
                    "department_id": entry.department_id,
                }
            )

        logger.debug(f"Found {len(history_data)} history entries, total: {total}")

        return {
            "history": history_data,
            "total": total,
            "skip": query.skip,
            "limit": query.limit,
        }
