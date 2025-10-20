"""
Asset Frontend - FastAPI + Jinja2
"""
import logging
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path

# Import routers
from app.routers import assets

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

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Setup templates
templates = Jinja2Templates(directory="app/templates")

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
