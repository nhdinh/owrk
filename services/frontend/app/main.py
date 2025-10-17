from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from pathlib import Path
from .routers import auth, pages

app = FastAPI(title="Asset Management - Frontend")

# Static and templates (resolve absolute paths)
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# Session (for CSRF/non-sensitive state). Tokens will be in HTTPOnly cookies
app.add_middleware(SessionMiddleware, secret_key="dev-secret-change")

# Routers
app.include_router(auth.router, prefix="", tags=["auth"])
app.include_router(pages.router, prefix="", tags=["pages"])


@app.get("/health")
async def health():
    return {"status": "ok"}
