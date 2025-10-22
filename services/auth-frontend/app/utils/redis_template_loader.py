"""
Redis-backed Jinja2 Template Loader
Fetches templates from shared-ui-service and caches them in Redis
"""
import logging
import json
from typing import Optional, Tuple
from jinja2 import BaseLoader, TemplateNotFound
import httpx
import redis
import os

logger = logging.getLogger(__name__)


class RedisTemplateLoader(BaseLoader):
    """
    Jinja2 template loader that fetches templates from shared-ui-service
    and caches them in Redis with ETag-based validation
    """

    def __init__(
        self,
        shared_ui_url: str,
        redis_client: redis.Redis,
        cache_ttl: int = 3600,  # 1 hour default
        fallback_to_local: bool = True
    ):
        """
        Initialize the Redis template loader

        Args:
            shared_ui_url: Base URL of the shared-ui-service (e.g., "http://shared-ui:5000")
            redis_client: Redis client instance
            cache_ttl: Time to live for cached templates in seconds
            fallback_to_local: Whether to fallback to local filesystem if service unavailable
        """
        self.shared_ui_url = shared_ui_url.rstrip('/')
        self.redis_client = redis_client
        self.cache_ttl = cache_ttl
        self.fallback_to_local = fallback_to_local
        self.http_client = httpx.Client(timeout=10.0)

        logger.info(f"Initialized RedisTemplateLoader with shared-ui at {self.shared_ui_url}")

    def _get_cache_key(self, template_name: str) -> str:
        """Generate Redis cache key for a template"""
        return f"template:{template_name}"

    def _get_etag_key(self, template_name: str) -> str:
        """Generate Redis cache key for a template's ETag"""
        return f"template:etag:{template_name}"

    def _fetch_template_from_service(self, template_name: str) -> Optional[Tuple[str, str]]:
        """
        Fetch template from shared-ui-service

        Returns:
            Tuple of (content, etag) or None if not found
        """
        try:
            url = f"{self.shared_ui_url}/api/templates/{template_name}"
            logger.debug(f"Fetching template from {url}")

            response = self.http_client.get(url)

            if response.status_code == 404:
                logger.warning(f"Template not found on service: {template_name}")
                return None

            response.raise_for_status()
            data = response.json()

            content = data.get('content')
            etag = data.get('etag')

            if not content or not etag:
                logger.error(f"Invalid response from shared-ui-service for {template_name}")
                return None

            logger.info(f"Successfully fetched template {template_name} (etag: {etag})")
            return (content, etag)

        except httpx.HTTPError as e:
            logger.error(f"HTTP error fetching template {template_name}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error fetching template {template_name}: {e}")
            return None

    def _get_cached_template(self, template_name: str) -> Optional[Tuple[str, str]]:
        """
        Get template from Redis cache

        Returns:
            Tuple of (content, etag) or None if not cached
        """
        try:
            cache_key = self._get_cache_key(template_name)
            etag_key = self._get_etag_key(template_name)

            content = self.redis_client.get(cache_key)
            etag = self.redis_client.get(etag_key)

            if content and etag:
                logger.debug(f"Template {template_name} found in cache")
                return (content.decode('utf-8'), etag.decode('utf-8'))

            return None

        except Exception as e:
            logger.error(f"Error reading from Redis cache: {e}")
            return None

    def _cache_template(self, template_name: str, content: str, etag: str):
        """Cache template in Redis with TTL"""
        try:
            cache_key = self._get_cache_key(template_name)
            etag_key = self._get_etag_key(template_name)

            # Store content and etag with TTL
            self.redis_client.setex(cache_key, self.cache_ttl, content.encode('utf-8'))
            self.redis_client.setex(etag_key, self.cache_ttl, etag.encode('utf-8'))

            logger.debug(f"Cached template {template_name} with TTL {self.cache_ttl}s")

        except Exception as e:
            logger.error(f"Error caching template in Redis: {e}")

    def get_source(self, environment, template):
        """
        Get template source for Jinja2

        This method is called by Jinja2 to load templates
        """
        # Try to get from cache first
        cached = self._get_cached_template(template)
        if cached:
            content, etag = cached

            # Return (source, filename, uptodate_func)
            # uptodate_func returns True if template is still valid
            return content, None, lambda: self._is_template_uptodate(template, etag)

        # Cache miss - fetch from shared-ui-service
        logger.info(f"Cache miss for template {template}, fetching from service")
        result = self._fetch_template_from_service(template)

        if result:
            content, etag = result

            # Cache the template
            self._cache_template(template, content, etag)

            # Return template source
            return content, None, lambda: self._is_template_uptodate(template, etag)

        # Template not found
        logger.error(f"Template not found: {template}")
        raise TemplateNotFound(template)

    def _is_template_uptodate(self, template_name: str, current_etag: str) -> bool:
        """
        Check if cached template is still up-to-date

        This is called by Jinja2 to determine if it should reload the template
        """
        try:
            cached_etag = self.redis_client.get(self._get_etag_key(template_name))
            if cached_etag:
                return cached_etag.decode('utf-8') == current_etag
            return False
        except Exception as e:
            logger.error(f"Error checking template freshness: {e}")
            return False

    def list_templates(self):
        """
        List all available templates from shared-ui-service

        This is used by Jinja2 for template discovery
        """
        try:
            url = f"{self.shared_ui_url}/api/templates"
            response = self.http_client.get(url)
            response.raise_for_status()

            data = response.json()
            templates = data.get('templates', [])

            return [t['path'] for t in templates]

        except Exception as e:
            logger.error(f"Error listing templates: {e}")
            return []

    def invalidate_cache(self, template_name: Optional[str] = None):
        """
        Invalidate cached template(s)

        Args:
            template_name: Specific template to invalidate, or None to clear all
        """
        try:
            if template_name:
                # Invalidate specific template
                self.redis_client.delete(
                    self._get_cache_key(template_name),
                    self._get_etag_key(template_name)
                )
                logger.info(f"Invalidated cache for template: {template_name}")
            else:
                # Invalidate all templates
                keys = self.redis_client.keys("template:*")
                if keys:
                    self.redis_client.delete(*keys)
                    logger.info(f"Invalidated cache for {len(keys)} template entries")

        except Exception as e:
            logger.error(f"Error invalidating cache: {e}")

    def close(self):
        """Close HTTP client"""
        try:
            self.http_client.close()
        except Exception as e:
            logger.error(f"Error closing HTTP client: {e}")
