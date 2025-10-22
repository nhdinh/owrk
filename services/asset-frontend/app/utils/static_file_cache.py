"""
Redis-backed Static File Cache
Caches static files (CSS, JS, images) from shared-ui-service in Redis
"""
import logging
from typing import Optional, Tuple, Dict
import httpx
import redis

logger = logging.getLogger(__name__)


class StaticFileCache:
    """
    Cache for static files from shared-ui-service
    Stores files in Redis with ETag-based validation
    """

    def __init__(
        self,
        shared_ui_url: str,
        redis_client: redis.Redis,
        cache_ttl: int = 86400,  # 24 hours default for static files
    ):
        """
        Initialize the static file cache

        Args:
            shared_ui_url: Base URL of the shared-ui-service (e.g., "http://shared-ui:5000")
            redis_client: Redis client instance
            cache_ttl: Time to live for cached files in seconds (default: 24 hours)
        """
        self.shared_ui_url = shared_ui_url.rstrip('/')
        self.redis_client = redis_client
        self.cache_ttl = cache_ttl
        self.http_client = httpx.Client(timeout=10.0)

        logger.info(f"Initialized StaticFileCache with shared-ui at {self.shared_ui_url}")

    def _get_cache_key(self, file_path: str) -> str:
        """Generate Redis cache key for a static file"""
        return f"static:{file_path}"

    def _get_etag_key(self, file_path: str) -> str:
        """Generate Redis cache key for a file's ETag"""
        return f"static:etag:{file_path}"

    def _get_content_type_key(self, file_path: str) -> str:
        """Generate Redis cache key for a file's content type"""
        return f"static:content_type:{file_path}"

    def _fetch_file_from_service(self, file_path: str) -> Optional[Tuple[bytes, str, str]]:
        """
        Fetch static file from shared-ui-service

        Returns:
            Tuple of (content, etag, content_type) or None if not found
        """
        try:
            url = f"{self.shared_ui_url}/api/static/{file_path}"
            logger.debug(f"Fetching static file from {url}")

            response = self.http_client.get(url)

            if response.status_code == 404:
                logger.warning(f"Static file not found on service: {file_path}")
                return None

            response.raise_for_status()

            content = response.content
            etag = response.headers.get('ETag', '')
            content_type = response.headers.get('Content-Type', 'application/octet-stream')

            if not content:
                logger.error(f"Empty response from shared-ui-service for {file_path}")
                return None

            logger.info(f"Successfully fetched static file {file_path} (etag: {etag}, type: {content_type})")
            return (content, etag, content_type)

        except httpx.HTTPError as e:
            logger.error(f"HTTP error fetching static file {file_path}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error fetching static file {file_path}: {e}")
            return None

    def _get_cached_file(self, file_path: str) -> Optional[Tuple[bytes, str, str]]:
        """
        Get static file from Redis cache

        Returns:
            Tuple of (content, etag, content_type) or None if not cached
        """
        try:
            cache_key = self._get_cache_key(file_path)
            etag_key = self._get_etag_key(file_path)
            content_type_key = self._get_content_type_key(file_path)

            content = self.redis_client.get(cache_key)
            etag = self.redis_client.get(etag_key)
            content_type = self.redis_client.get(content_type_key)

            if content and etag and content_type:
                logger.debug(f"Static file {file_path} found in cache")
                return (content, etag.decode('utf-8'), content_type.decode('utf-8'))

            return None

        except Exception as e:
            logger.error(f"Error reading from Redis cache: {e}")
            return None

    def _cache_file(self, file_path: str, content: bytes, etag: str, content_type: str):
        """Cache static file in Redis with TTL"""
        try:
            cache_key = self._get_cache_key(file_path)
            etag_key = self._get_etag_key(file_path)
            content_type_key = self._get_content_type_key(file_path)

            # Store content, etag, and content type with TTL
            self.redis_client.setex(cache_key, self.cache_ttl, content)
            self.redis_client.setex(etag_key, self.cache_ttl, etag.encode('utf-8'))
            self.redis_client.setex(content_type_key, self.cache_ttl, content_type.encode('utf-8'))

            logger.debug(f"Cached static file {file_path} with TTL {self.cache_ttl}s")

        except Exception as e:
            logger.error(f"Error caching static file in Redis: {e}")

    def get_file(self, file_path: str) -> Optional[Tuple[bytes, str, str]]:
        """
        Get static file with caching

        This is the main method to use for fetching static files

        Args:
            file_path: Path to the static file (e.g., "css/common.css")

        Returns:
            Tuple of (content, etag, content_type) or None if not found
        """
        # Try to get from cache first
        cached = self._get_cached_file(file_path)
        if cached:
            return cached

        # Cache miss - fetch from shared-ui-service
        logger.info(f"Cache miss for static file {file_path}, fetching from service")
        result = self._fetch_file_from_service(file_path)

        if result:
            content, etag, content_type = result

            # Cache the file
            self._cache_file(file_path, content, etag, content_type)

            return result

        # File not found
        logger.error(f"Static file not found: {file_path}")
        return None

    def invalidate_cache(self, file_path: Optional[str] = None):
        """
        Invalidate cached static file(s)

        Args:
            file_path: Specific file to invalidate, or None to clear all
        """
        try:
            if file_path:
                # Invalidate specific file
                self.redis_client.delete(
                    self._get_cache_key(file_path),
                    self._get_etag_key(file_path),
                    self._get_content_type_key(file_path)
                )
                logger.info(f"Invalidated cache for static file: {file_path}")
            else:
                # Invalidate all static files
                keys = self.redis_client.keys("static:*")
                if keys:
                    self.redis_client.delete(*keys)
                    logger.info(f"Invalidated cache for {len(keys)} static file entries")

        except Exception as e:
            logger.error(f"Error invalidating cache: {e}")

    def get_manifest(self) -> Dict:
        """
        Get manifest of all available static files from shared-ui-service

        Returns:
            Dictionary with file information
        """
        try:
            url = f"{self.shared_ui_url}/api/static"
            response = self.http_client.get(url)
            response.raise_for_status()

            return response.json()

        except Exception as e:
            logger.error(f"Error fetching static files manifest: {e}")
            return {"files": [], "count": 0}

    def close(self):
        """Close HTTP client"""
        try:
            self.http_client.close()
        except Exception as e:
            logger.error(f"Error closing HTTP client: {e}")
