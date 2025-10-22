import os
from fastapi import FastAPI, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import httpx
from starlette.middleware.sessions import SessionMiddleware
from pathlib import Path
from jinja2 import ChoiceLoader, FileSystemLoader, Environment, select_autoescape
from .common import get_logger
import redis


logger = get_logger(__name__)


app = FastAPI(title="Asset Management - Frontend")

# Static and templates (resolve absolute paths)
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"
# Add common-ui templates directory (shared across frontends)
# When running in Docker, common-ui directory is mounted at /common-ui
COMMONUI_TEMPLATES_DIR = (
    Path("/common-ui/templates")
    if Path("/common-ui/templates").exists()
    else BASE_DIR.parent.parent.parent / "common-ui" / "templates"
)

remote_static = FastAPI()


@remote_static.get("/{path:path}")
async def serve_remote(path: str):
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"http://shared-ui:5000/{path}")
        return Response(
            resp.content, resp.status_code, media_type=resp.headers.get("content-type")
        )


# app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
app.mount("/static", remote_static)

# Initialize Redis client for template caching
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379")
SHARED_UI_URL = os.getenv("SHARED_UI_URL", "http://shared-ui:5000")
USE_REDIS_LOADER = (
    os.getenv("USE_REDIS_LOADER", "true").lower() == "true"
    and os.getenv("ENVIRONMENT", "development").lower() == "production"
)

redis_client = None
try:
    redis_client = redis.from_url(REDIS_URL, decode_responses=False)
    redis_client.ping()
    logger.info(f"Connected to Redis at {REDIS_URL}")
except Exception as e:
    logger.warning(f"Could not connect to Redis: {e}. Will use local filesystem only.")
    USE_REDIS_LOADER = False

# Create Jinja2 environment with ChoiceLoader to search multiple template directories
loaders = []

# Add Redis-backed loader for shared templates (if enabled)
if USE_REDIS_LOADER and redis_client:
    try:
        from .utils.redis_template_loader import RedisTemplateLoader

        redis_loader = RedisTemplateLoader(
            shared_ui_url=SHARED_UI_URL,
            redis_client=redis_client,
            cache_ttl=3600,  # 1 hour cache
        )
        loaders.append(redis_loader)
        logger.info("Enabled Redis template loader for shared-ui templates")
    except Exception as e:
        logger.warning(f"Could not initialize Redis template loader: {e}")

# Add local filesystem loaders (fallback)
loaders.extend(
    [
        FileSystemLoader(str(TEMPLATES_DIR)),
        FileSystemLoader(str(COMMONUI_TEMPLATES_DIR)),
    ]
)

jinja_loader = ChoiceLoader(loaders)
jinja_env = Environment(
    loader=jinja_loader, autoescape=select_autoescape(["html", "xml"])
)

# Create templates object with pre-configured environment
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
templates.env = jinja_env

logger.info(f"Template loaders configured: {len(loaders)} loaders")

# Import routers after templates is configured
from .routers import auth, pages

# Session (for CSRF/non-sensitive state). Tokens will be in HTTPOnly cookies
# JWT Settings
JWT_SECRET: str = "your-super-secret-jwt-key-change-in-production"
jwt_secret_file = os.getenv("JWT_SECRET_KEY_FILE")
if jwt_secret_file and os.path.exists(jwt_secret_file):
    with open(jwt_secret_file, "r") as f:
        JWT_SECRET = f.read().strip()
app.add_middleware(SessionMiddleware, secret_key=JWT_SECRET)

# Routers
# Note: When behind nginx gateway, routes are already prefixed by nginx
# so we don't add AUTH_PREFIX here
app.include_router(auth.router, prefix="", tags=["auth"])
app.include_router(pages.router, prefix="", tags=["pages"])


@app.get("/health")
async def health():
    return {"status": "ok"}
