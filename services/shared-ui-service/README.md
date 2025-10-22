# Shared UI Service

FastAPI service that serves shared templates and static files over HTTP for frontend services. Templates are cached in Redis with ETag-based validation for efficient updates.

## Features

- **HTTP Template Serving**: Serves Jinja2 templates via REST API
- **Static File Serving**: Serves CSS, JS, images, and fonts
- **ETag-based Caching**: Provides ETags for cache validation
- **Redis Integration**: Frontend services cache templates in Redis
- **Automatic Cache Expiration**: Templates expire after configured TTL
- **Manifest API**: Provides complete list of templates with ETags

## Architecture

```
┌─────────────────┐
│  Shared-UI      │
│  Service        │──────┐
│  (FastAPI)      │      │
└─────────────────┘      │
                         │ HTTP GET
┌─────────────────┐      │ /api/templates/*
│  Auth-Frontend  │◄─────┤
│  (FastAPI)      │      │
│                 │      │
│  ┌───────────┐  │      │
│  │  Redis    │  │      │
│  │  Cache    │  │      │
│  │  Loader   │  │      │
│  └───────────┘  │      │
│       │         │      │
│       ▼         │      │
│  ┌───────────┐  │      │
│  │   Redis   │  │      │
│  └───────────┘  │      │
└─────────────────┘      │
                         │
┌─────────────────┐      │
│  Asset-Frontend │◄─────┘
│  (FastAPI)      │
│                 │
│  ┌───────────┐  │
│  │  Redis    │  │
│  │  Cache    │  │
│  │  Loader   │  │
│  └───────────┘  │
│       │         │
│       ▼         │
│  ┌───────────┐  │
│  │   Redis   │  │
│  └───────────┘  │
└─────────────────┘
```

## API Endpoints

### Health Check
```
GET /health
```
Returns service health status.

### List Templates
```
GET /api/templates
```
Returns list of all available templates with metadata.

**Response:**
```json
{
  "templates": [
    {
      "path": "layouts/base.html",
      "name": "base.html",
      "size": 1435,
      "etag": "\"74ba7e72d7d8e2195e5cee1deb336093\""
    }
  ],
  "count": 6
}
```

### Get Template
```
GET /api/templates/{template_path}
```
Returns template content with ETag.

**Response:**
```json
{
  "path": "layouts/base.html",
  "content": "<!DOCTYPE html>...",
  "etag": "\"74ba7e72d7d8e2195e5cee1deb336093\"",
  "size": 1435
}
```

### List Static Files
```
GET /api/static
```
Returns list of all available static files.

### Get Static File
```
GET /api/static/{file_path}
```
Returns static file with appropriate content-type.

### Manifest
```
GET /api/manifest
```
Returns complete manifest of all templates and static files with ETags.

**Response:**
```json
{
  "templates": {
    "layouts/base.html": {
      "etag": "\"74ba7e72d7d8e2195e5cee1deb336093\"",
      "size": 1435
    }
  },
  "static": {
    "css/common.css": {
      "etag": "\"abc123...\"",
      "size": 5432,
      "type": ".css"
    }
  },
  "version": "1.0.0"
}
```

## Redis Template Loader

Frontend services use a custom Jinja2 loader that:

1. **Checks Redis Cache**: First looks for template in Redis
2. **Fetches if Missing**: If cache miss, fetches from shared-ui-service
3. **Caches with TTL**: Stores template and ETag in Redis (default 1 hour)
4. **Validates Freshness**: Uses ETag to check if cached version is up-to-date

### Configuration

Environment variables for frontend services:

```bash
SHARED_UI_URL=http://shared-ui:5000
REDIS_URL=redis://redis:6379
USE_REDIS_LOADER=true  # Set to false to disable
```

### Cache Keys

Templates are cached with these Redis keys:

- `template:{template_path}` - Template content
- `template:etag:{template_path}` - Template ETag

### Cache Invalidation

To invalidate cache for a specific template:

```python
from app.utils.redis_template_loader import RedisTemplateLoader

redis_loader.invalidate_cache("layouts/base.html")
```

To clear all cached templates:

```python
redis_loader.invalidate_cache()  # No argument clears all
```

## Development

### Running Locally

```bash
cd services/shared-ui-service
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 5000 --reload
```

### Testing

Test the service endpoints:

```bash
# Health check
curl http://localhost:5000/health

# List templates
curl http://localhost:5000/api/templates

# Get specific template
curl http://localhost:5000/api/templates/layouts/base.html

# Get manifest
curl http://localhost:5000/api/manifest
```

### Docker

Build and run with Docker Compose:

```bash
# Build
docker compose build shared-ui

# Run
docker compose up -d shared-ui

# Check logs
docker compose logs shared-ui

# Test from another container
docker compose exec auth-api curl http://shared-ui:5000/health
```

## Benefits

1. **Centralized Templates**: Single source of truth for shared UI components
2. **Performance**: Redis caching reduces HTTP requests
3. **Flexibility**: Templates can be updated without rebuilding frontends
4. **Scalability**: Shared-ui service can be scaled independently
5. **Cache Efficiency**: ETag validation ensures only changed templates are re-fetched
6. **Fallback**: Frontends can still use local filesystem if service unavailable

## Template Resolution Order

Frontend services use Jinja2 ChoiceLoader with this search order:

1. **Redis Cache Loader** - Fetches from shared-ui-service and caches in Redis
2. **Local Templates** - Service-specific templates (e.g., auth/login.html)
3. **Common-UI Filesystem** - Local fallback for shared templates

This allows:
- Service-specific templates to override shared ones
- Graceful fallback if shared-ui service is unavailable
- Development without shared-ui service running

## Monitoring

Check Redis cache statistics:

```bash
# Count cached templates
docker compose exec redis redis-cli KEYS "template:*" | wc -l

# List all cached templates
docker compose exec redis redis-cli KEYS "template:*"

# Get specific template from cache
docker compose exec redis redis-cli GET "template:layouts/base.html"

# Check template ETag
docker compose exec redis redis-cli GET "template:etag:layouts/base.html"
```

## Performance

- **First Request**: ~15-30ms (cache miss, fetch from service)
- **Subsequent Requests**: ~1-3ms (cache hit from Redis)
- **Cache TTL**: 3600 seconds (1 hour) by default
- **ETag Validation**: Efficient - only re-fetches if template changed

## Troubleshooting

### Service Unhealthy

Check if curl is installed:
```bash
docker compose exec shared-ui curl --version
```

### Templates Not Loading

1. Check shared-ui service is running:
```bash
docker compose ps shared-ui
```

2. Check Redis connection:
```bash
docker compose exec auth-fe python -c "import redis; r = redis.from_url('redis://redis:6379'); print(r.ping())"
```

3. Check logs:
```bash
docker compose logs shared-ui
docker compose logs auth-fe | grep template
```

### Cache Not Working

Verify Redis loader is enabled:
```bash
docker compose logs auth-fe | grep "Redis template loader"
```

Should see: `Enabled Redis template loader for shared-ui templates`
