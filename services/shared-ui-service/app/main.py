"""
Shared UI Service - FastAPI Application
Serves templates and static files over HTTP for other frontend services
"""

import logging
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import hashlib

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(filename)s:%(lineno)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Shared UI Service",
    description="Serves shared templates and static files for frontend services",
    version="1.0.0",
)

# CORS middleware to allow frontend services to fetch resources
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual frontend origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Paths to shared resources
SHARED_UI_DIR = (
    Path("/shared-ui")
    if Path("/shared-ui").exists()
    else Path(__file__).parent.parent.parent.parent / "common-ui"
)
TEMPLATES_DIR = SHARED_UI_DIR / "templates"
STATIC_DIR = SHARED_UI_DIR / "static"

logger.info(f"Shared UI Directory: {SHARED_UI_DIR}")
logger.info(f"Templates Directory: {TEMPLATES_DIR}")
logger.info(f"Static Directory: {STATIC_DIR}")


def calculate_etag(file_path: Path) -> str:
    """Calculate ETag for a file based on its content"""
    with open(file_path, "rb") as f:
        file_hash = hashlib.md5(f.read()).hexdigest()
    return f'"{file_hash}"'


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Shared UI Service",
        "version": "1.0.0",
        "endpoints": {
            "templates": "/api/templates/{template_path}",
            "static": "/api/static/{file_path}",
            "list_templates": "/api/templates",
            "list_static": "/api/static",
            "health": "/health",
        },
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "ok", "service": "shared-ui-service"}


@app.get("/api/templates")
async def list_templates():
    """List all available templates"""
    if not TEMPLATES_DIR.exists():
        raise HTTPException(status_code=500, detail="Templates directory not found")

    templates = []
    for template_file in TEMPLATES_DIR.rglob("*.html"):
        relative_path = template_file.relative_to(TEMPLATES_DIR)
        templates.append(
            {
                "path": str(relative_path).replace("\\", "/"),
                "name": template_file.name,
                "size": template_file.stat().st_size,
                "etag": calculate_etag(template_file),
            }
        )

    return {"templates": templates, "count": len(templates)}


@app.get("/api/templates/{template_path:path}")
async def get_template(template_path: str):
    """Get a specific template file"""
    template_file = TEMPLATES_DIR / template_path

    # Security check: ensure the file is within templates directory
    try:
        template_file = template_file.resolve()
        TEMPLATES_DIR.resolve()
        if not str(template_file).startswith(str(TEMPLATES_DIR.resolve())):
            raise HTTPException(status_code=403, detail="Access denied")
    except Exception as e:
        logger.error(f"Path resolution error: {e}")
        raise HTTPException(status_code=403, detail="Invalid path")

    if not template_file.exists() or not template_file.is_file():
        raise HTTPException(status_code=404, detail="Template not found")

    # Read template content
    try:
        content = template_file.read_text(encoding="utf-8")
        etag = calculate_etag(template_file)

        return JSONResponse(
            content={
                "path": template_path,
                "content": content,
                "etag": etag,
                "size": len(content),
            },
            headers={"ETag": etag},
        )
    except Exception as e:
        logger.error(f"Error reading template {template_path}: {e}")
        raise HTTPException(status_code=500, detail="Error reading template")


@app.get("/api/static")
async def list_static_files():
    """List all available static files"""
    if not STATIC_DIR.exists():
        raise HTTPException(status_code=500, detail="Static directory not found")

    static_files = []
    for static_file in STATIC_DIR.rglob("*"):
        if static_file.is_file():
            relative_path = static_file.relative_to(STATIC_DIR)
            static_files.append(
                {
                    "path": str(relative_path).replace("\\", "/"),
                    "name": static_file.name,
                    "size": static_file.stat().st_size,
                    "type": static_file.suffix,
                    "etag": calculate_etag(static_file),
                }
            )

    return {"files": static_files, "count": len(static_files)}


@app.get("/api/static/{file_path:path}")
async def get_static_file(file_path: str, etag: Optional[str] = None):
    """Get a specific static file"""
    static_file = STATIC_DIR / file_path
    logger.info(f"Requesting static: {file_path}?{etag}")

    # Security check: ensure the file is within static directory
    try:
        static_file = static_file.resolve()
        STATIC_DIR.resolve()
        if not str(static_file).startswith(str(STATIC_DIR.resolve())):
            raise HTTPException(status_code=403, detail="Access denied")
    except Exception as e:
        logger.error(f"Path resolution error: {e}")
        raise HTTPException(status_code=403, detail="Invalid path")

    if not static_file.exists() or not static_file.is_file():
        raise HTTPException(status_code=404, detail="File not found")

    # Determine content type based on file extension
    content_types = {
        ".css": "text/css",
        ".js": "application/javascript",
        ".json": "application/json",
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".gif": "image/gif",
        ".svg": "image/svg+xml",
        ".ico": "image/x-icon",
        ".woff": "font/woff",
        ".woff2": "font/woff2",
        ".ttf": "font/ttf",
        ".eot": "application/vnd.ms-fontobject",
    }

    media_type = content_types.get(
        static_file.suffix.lower(), "application/octet-stream"
    )
    etag = calculate_etag(static_file)

    return FileResponse(path=static_file, media_type=media_type, headers={"ETag": etag})


@app.get("/api/manifest")
async def get_manifest():
    """Get complete manifest of all templates and static files with ETags"""
    manifest = {"templates": {}, "static": {}, "version": "1.0.0"}

    # Add all templates
    if TEMPLATES_DIR.exists():
        for template_file in TEMPLATES_DIR.rglob("*.html"):
            relative_path = str(template_file.relative_to(TEMPLATES_DIR)).replace(
                "\\", "/"
            )
            manifest["templates"][relative_path] = {
                "etag": calculate_etag(template_file),
                "size": template_file.stat().st_size,
            }

    # Add all static files
    if STATIC_DIR.exists():
        for static_file in STATIC_DIR.rglob("*"):
            if static_file.is_file():
                relative_path = str(static_file.relative_to(STATIC_DIR)).replace(
                    "\\", "/"
                )
                manifest["static"][relative_path] = {
                    "etag": calculate_etag(static_file),
                    "size": static_file.stat().st_size,
                    "type": static_file.suffix,
                }

    return manifest


if __name__ == "__main__":
    import uvicorn

    logger.info("Run uvicorn")

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=5000,
        reload=True,
        reload_dirs=[
            "/app/app/*",
            "/shared-ui/static/css/*",
            "/shared-ui/static/js/*",
            "/shared-ui/static/images/*",
            "/shared-ui/templates/components/*",
            "/shared-ui/templates/layouts/*",
        ],
    )
