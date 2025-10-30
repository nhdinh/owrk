"""
User Read Repository - MongoDB (CQRS Read Model)
Handles all READ operations for User entity
"""

from typing import Optional, List, Dict
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase


class UserReadRepository:
    """
    Read-only repository for User queries from MongoDB
    Part of CQRS pattern - optimized for fast reads
    """

    def __init__(self, mongo_db: AsyncIOMotorDatabase):
        self.db = mongo_db
        self.collection = mongo_db.users

    async def get_by_id(self, user_id: int) -> Optional[Dict]:
        """
        Get user by ID from MongoDB read model

        Args:
            user_id: User ID

        Returns:
            User document or None
        """
        return await self.collection.find_one({"id": user_id})

    async def get_by_email(self, email: str) -> Optional[Dict]:
        """
        Get user by email - optimized for fast lookup

        Args:
            email: User email

        Returns:
            User document or None
        """
        return await self.collection.find_one({"email": email})

    async def get_by_username(self, username: str) -> Optional[Dict]:
        """
        Get user by username

        Args:
            username: Username

        Returns:
            User document or None
        """
        return await self.collection.find_one({"username": username})

    async def find_all(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Get list of users with pagination and filters

        Args:
            skip: Number of documents to skip
            limit: Maximum number of documents to return
            filters: MongoDB query filters

        Returns:
            List of user documents
        """
        query = filters or {}
        cursor = self.collection.find(query).skip(skip).limit(limit)
        return await cursor.to_list(length=limit)

    async def get_active_users(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[Dict]:
        """
        Get all active users

        Args:
            skip: Pagination offset
            limit: Max results

        Returns:
            List of active users
        """
        return await self.find_all(
            skip=skip,
            limit=limit,
            filters={"is_active": True}
        )

    async def get_users_by_role(
        self,
        role_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Dict]:
        """
        Get users by role ID

        Args:
            role_id: Role ID
            skip: Pagination offset
            limit: Max results

        Returns:
            List of users with specified role
        """
        return await self.find_all(
            skip=skip,
            limit=limit,
            filters={"role_id": role_id}
        )

    async def get_users_by_department(
        self,
        department_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Dict]:
        """
        Get users by department

        Args:
            department_id: Department ID
            skip: Pagination offset
            limit: Max results

        Returns:
            List of users in department
        """
        return await self.find_all(
            skip=skip,
            limit=limit,
            filters={"department_id": department_id}
        )

    async def get_users_with_mfa(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[Dict]:
        """
        Get users with MFA enabled

        Args:
            skip: Pagination offset
            limit: Max results

        Returns:
            List of users with MFA
        """
        return await self.find_all(
            skip=skip,
            limit=limit,
            filters={"mfa_enabled": True}
        )

    async def search_users(
        self,
        search_term: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Dict]:
        """
        Search users by name, email, or username

        Args:
            search_term: Search term
            skip: Pagination offset
            limit: Max results

        Returns:
            List of matching users
        """
        query = {
            "$or": [
                {"full_name": {"$regex": search_term, "$options": "i"}},
                {"email": {"$regex": search_term, "$options": "i"}},
                {"username": {"$regex": search_term, "$options": "i"}}
            ]
        }
        return await self.find_all(skip=skip, limit=limit, filters=query)

    async def count_users(self, filters: Optional[Dict] = None) -> int:
        """
        Count users with optional filters

        Args:
            filters: MongoDB query filters

        Returns:
            Total count
        """
        query = filters or {}
        return await self.collection.count_documents(query)

    async def count_active_users(self) -> int:
        """Count total active users"""
        return await self.count_users({"is_active": True})

    async def get_users_statistics(self) -> Dict:
        """
        Get user statistics (aggregated data)

        Returns:
            Dictionary with statistics
        """
        pipeline = [
            {
                "$group": {
                    "_id": None,
                    "total_users": {"$sum": 1},
                    "active_users": {
                        "$sum": {"$cond": [{"$eq": ["$is_active", True]}, 1, 0]}
                    },
                    "mfa_enabled_users": {
                        "$sum": {"$cond": [{"$eq": ["$mfa_enabled", True]}, 1, 0]}
                    },
                    "local_users": {
                        "$sum": {"$cond": [{"$eq": ["$user_type", "local"]}, 1, 0]}
                    },
                    "ad_users": {
                        "$sum": {"$cond": [{"$eq": ["$user_type", "active_directory"]}, 1, 0]}
                    }
                }
            }
        ]

        cursor = self.collection.aggregate(pipeline)
        results = await cursor.to_list(length=1)

        if results:
            stats = results[0]
            stats.pop("_id", None)
            return stats

        return {
            "total_users": 0,
            "active_users": 0,
            "mfa_enabled_users": 0,
            "local_users": 0,
            "ad_users": 0
        }

    async def upsert_user(self, user_data: Dict) -> bool:
        """
        Insert or update user in MongoDB (called by event consumer)

        Args:
            user_data: User data from event

        Returns:
            True if successful
        """
        user_id = user_data.get("id")
        if not user_id:
            return False

        # Remove sensitive data before storing
        safe_data = {k: v for k, v in user_data.items() if k not in ["hashed_password", "mfa_secret"]}

        # Add metadata
        safe_data["synced_at"] = datetime.utcnow()

        await self.collection.update_one(
            {"id": user_id},
            {"$set": safe_data},
            upsert=True
        )
        return True

    async def delete_user(self, user_id: int) -> bool:
        """
        Delete user from MongoDB (called by event consumer)

        Args:
            user_id: User ID

        Returns:
            True if successful
        """
        result = await self.collection.delete_one({"id": user_id})
        return result.deleted_count > 0

    async def create_indexes(self):
        """
        Create indexes for better query performance
        Should be called on application startup
        """
        await self.collection.create_index("id", unique=True)
        await self.collection.create_index("email", unique=True)
        await self.collection.create_index("username")
        await self.collection.create_index("role_id")
        await self.collection.create_index("department_id")
        await self.collection.create_index("is_active")
        await self.collection.create_index("mfa_enabled")
        await self.collection.create_index("user_type")
        # Text index for search
        await self.collection.create_index([
            ("full_name", "text"),
            ("email", "text"),
            ("username", "text")
        ])
        print("✅ MongoDB indexes created for users collection")
