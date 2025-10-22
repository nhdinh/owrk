"""
Asset Frontend - FastAPI + Jinja2
"""
import logging
import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
from jinja2 import ChoiceLoader, FileSystemLoader, Environment, select_autoescape
import redis

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Asset Management Frontend",
    description="Frontend for Asset Management System",
    version="1.0.0"
)

# Static and templates (resolve absolute paths)
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"
# Add common-ui templates directory (shared across frontends)
# When running in Docker, common-ui directory is mounted at /common-ui
COMMON_TEMPLATES_DIR = Path("/common-ui/templates") if Path("/common-ui/templates").exists() else BASE_DIR.parent.parent.parent / "common-ui" / "templates"

# Mount static files
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Initialize Redis client for template caching
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379")
SHARED_UI_URL = os.getenv("SHARED_UI_URL", "http://shared-ui:5000")
USE_REDIS_LOADER = os.getenv("USE_REDIS_LOADER", "true").lower() == "true"

redis_client = None
try:
    redis_client = redis.from_url(REDIS_URL, decode_responses=False)
    redis_client.ping()
    logger.info(f"Connected to Redis at {REDIS_URL}")
except Exception as e:
    logger.warning(f"Could not connect to Redis: {e}. Will use local filesystem only.")
    USE_REDIS_LOADER = False

# Setup templates with ChoiceLoader to search multiple template directories
loaders = []

# Add Redis-backed loader for shared templates (if enabled)
if USE_REDIS_LOADER and redis_client:
    try:
        from app.utils.redis_template_loader import RedisTemplateLoader
        redis_loader = RedisTemplateLoader(
            shared_ui_url=SHARED_UI_URL,
            redis_client=redis_client,
            cache_ttl=3600  # 1 hour cache
        )
        loaders.append(redis_loader)
        logger.info("Enabled Redis template loader for shared-ui templates")
    except Exception as e:
        logger.warning(f"Could not initialize Redis template loader: {e}")

# Add local filesystem loaders (fallback)
loaders.extend([
    FileSystemLoader(str(TEMPLATES_DIR)),
    FileSystemLoader(str(COMMON_TEMPLATES_DIR))
])

jinja_loader = ChoiceLoader(loaders)
jinja_env = Environment(
    loader=jinja_loader, autoescape=select_autoescape(["html", "xml"])
)

# Create templates object with pre-configured environment
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
templates.env = jinja_env

logger.info(f"Template loaders configured: {len(loaders)} loaders")

# Import routers after templates is configured
from app.routers import assets

# Include routers
app.include_router(assets.router, prefix="/assets", tags=["assets"])


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Redirect to assets page"""
    return templates.TemplateResponse("assets/list.html", {"request": request})


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "ok"}


@app.exception_handler(404)
async def not_found(request: Request, exc):
    """Custom 404 handler"""
    return templates.TemplateResponse(
        "error.html",
        {"request": request, "status_code": 404, "message": "Page not found"},
        status_code=404
    )


@app.exception_handler(500)
async def server_error(request: Request, exc):
    """Custom 500 handler"""
    logger.error(f"Server error: {exc}")
    return templates.TemplateResponse(
        "error.html",
        {"request": request, "status_code": 500, "message": "Internal server error"},
        status_code=500
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3001)
