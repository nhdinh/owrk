"""
Active Directory Integration using LDAP
"""

from typing import Optional, Dict
import ldap3
from ldap3 import Server, Connection, ALL, SUBTREE
from ldap3.core.exceptions import LDAPException

from app.core.config import settings


class ActiveDirectoryService:
    """
    Service for Active Directory integration via LDAP
    """

    def __init__(self):
        self.server_uri = settings.AD_SERVER
        self.domain = settings.AD_DOMAIN
        self.bind_dn = settings.AD_BIND_DN
        self.bind_password = settings.AD_BIND_PASSWORD
        self.search_base = settings.AD_SEARCH_BASE
        self.enabled = settings.AD_ENABLED

    def _get_connection(self, user_dn: Optional[str] = None, password: Optional[str] = None) -> Optional[Connection]:
        """
        Create LDAP connection

        Args:
            user_dn: User distinguished name (optional, uses bind_dn if not provided)
            password: User password (optional, uses bind_password if not provided)

        Returns:
            LDAP Connection or None if failed
        """
        if not self.enabled:
            return None

        try:
            server = Server(self.server_uri, get_info=ALL)

            # Use provided credentials or default bind credentials
            dn = user_dn if user_dn else self.bind_dn
            pwd = password if password else self.bind_password

            conn = Connection(
                server,
                user=dn,
                password=pwd,
                authentication=ldap3.SIMPLE,
                auto_bind=True
            )
            return conn
        except LDAPException as e:
            print(f"LDAP Connection Error: {e}")
            return None

    def authenticate_user(self, username: str, password: str) -> Optional[Dict]:
        """
        Authenticate user against Active Directory

        Args:
            username: Username (sAMAccountName)
            password: User password

        Returns:
            User information dict if authentication successful, None otherwise
        """
        if not self.enabled:
            return None

        try:
            # First, bind with service account to search for user
            conn = self._get_connection()
            if not conn:
                return None

            # Search for user
            search_filter = f"(sAMAccountName={username})"
            conn.search(
                search_base=self.search_base,
                search_filter=search_filter,
                search_scope=SUBTREE,
                attributes=['mail', 'displayName', 'department', 'telephoneNumber',
                           'title', 'distinguishedName', 'objectGUID']
            )

            if not conn.entries:
                print(f"User {username} not found in AD")
                return None

            user_entry = conn.entries[0]
            user_dn = user_entry.distinguishedName.value

            # Close service connection
            conn.unbind()

            # Try to bind with user credentials to verify password
            user_conn = self._get_connection(user_dn=user_dn, password=password)
            if not user_conn:
                print(f"Authentication failed for user {username}")
                return None

            # Authentication successful, extract user info
            user_info = {
                "username": username,
                "email": user_entry.mail.value if hasattr(user_entry, 'mail') else None,
                "full_name": user_entry.displayName.value if hasattr(user_entry, 'displayName') else username,
                "department": user_entry.department.value if hasattr(user_entry, 'department') else None,
                "phone_number": user_entry.telephoneNumber.value if hasattr(user_entry, 'telephoneNumber') else None,
                "position": user_entry.title.value if hasattr(user_entry, 'title') else None,
                "ad_sync_id": str(user_entry.objectGUID.value) if hasattr(user_entry, 'objectGUID') else None,
                "user_type": "active_directory"
            }

            user_conn.unbind()
            return user_info

        except LDAPException as e:
            print(f"LDAP Authentication Error: {e}")
            return None

    def get_user_info(self, username: str) -> Optional[Dict]:
        """
        Get user information from Active Directory

        Args:
            username: Username (sAMAccountName)

        Returns:
            User information dict or None
        """
        if not self.enabled:
            return None

        try:
            conn = self._get_connection()
            if not conn:
                return None

            search_filter = f"(sAMAccountName={username})"
            conn.search(
                search_base=self.search_base,
                search_filter=search_filter,
                search_scope=SUBTREE,
                attributes=['mail', 'displayName', 'department', 'telephoneNumber',
                           'title', 'objectGUID', 'whenCreated', 'whenChanged']
            )

            if not conn.entries:
                return None

            user_entry = conn.entries[0]
            user_info = {
                "username": username,
                "email": user_entry.mail.value if hasattr(user_entry, 'mail') else None,
                "full_name": user_entry.displayName.value if hasattr(user_entry, 'displayName') else username,
                "department": user_entry.department.value if hasattr(user_entry, 'department') else None,
                "phone_number": user_entry.telephoneNumber.value if hasattr(user_entry, 'telephoneNumber') else None,
                "position": user_entry.title.value if hasattr(user_entry, 'title') else None,
                "ad_sync_id": str(user_entry.objectGUID.value) if hasattr(user_entry, 'objectGUID') else None,
                "user_type": "active_directory"
            }

            conn.unbind()
            return user_info

        except LDAPException as e:
            print(f"LDAP Search Error: {e}")
            return None

    def sync_all_users(self) -> list[Dict]:
        """
        Sync all users from Active Directory

        Returns:
            List of user information dicts
        """
        if not self.enabled:
            return []

        try:
            conn = self._get_connection()
            if not conn:
                return []

            # Search for all users
            search_filter = "(objectClass=user)"
            conn.search(
                search_base=self.search_base,
                search_filter=search_filter,
                search_scope=SUBTREE,
                attributes=['sAMAccountName', 'mail', 'displayName', 'department',
                           'telephoneNumber', 'title', 'objectGUID']
            )

            users = []
            for entry in conn.entries:
                if hasattr(entry, 'sAMAccountName'):
                    user_info = {
                        "username": entry.sAMAccountName.value,
                        "email": entry.mail.value if hasattr(entry, 'mail') else None,
                        "full_name": entry.displayName.value if hasattr(entry, 'displayName') else entry.sAMAccountName.value,
                        "department": entry.department.value if hasattr(entry, 'department') else None,
                        "phone_number": entry.telephoneNumber.value if hasattr(entry, 'telephoneNumber') else None,
                        "position": entry.title.value if hasattr(entry, 'title') else None,
                        "ad_sync_id": str(entry.objectGUID.value) if hasattr(entry, 'objectGUID') else None,
                        "user_type": "active_directory"
                    }
                    users.append(user_info)

            conn.unbind()
            return users

        except LDAPException as e:
            print(f"LDAP Sync Error: {e}")
            return []


# Global instance
ad_service = ActiveDirectoryService()
