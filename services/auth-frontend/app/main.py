import logging
import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from pathlib import Path
from .routers import auth, pages

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Asset Management - Frontend")

# Static and templates (resolve absolute paths)
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# Session (for CSRF/non-sensitive state). Tokens will be in HTTPOnly cookies
# JWT Settings
JWT_SECRET: str = "your-super-secret-jwt-key-change-in-production"
jwt_secret_file = os.getenv("JWT_SECRET_KEY_FILE")
if jwt_secret_file and os.path.exists(jwt_secret_file):
    with open(jwt_secret_file, "r") as f:
        JWT_SECRET = f.read().strip()
app.add_middleware(SessionMiddleware, secret_key=JWT_SECRET)

# Routers
app.include_router(auth.router, prefix="", tags=["auth"])
app.include_router(pages.router, prefix="", tags=["pages"])


@app.get("/health")
async def health():
    return {"status": "ok"}
