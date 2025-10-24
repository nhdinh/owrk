"""
Roles Frontend Routes
"""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
import httpx

from ..common import prefixes, get_logger, API_BASE

router = APIRouter(prefix="")
logger = get_logger(__name__)

# Import templates from main module (configured with common templates)
from ..main import templates


def _auth_headers_from_cookies(request: Request) -> dict:
    """Extract auth header from cookies"""
    access = request.cookies.get("access_token")
    return {"Authorization": f"Bearer {access}"} if access else {}


@router.get("/roles", response_class=HTMLResponse)
async def list_roles(request: Request):
    """List all roles"""
    headers = _auth_headers_from_cookies(request)
    if not headers:
        return RedirectResponse(url=f"{prefixes['auth']}/login", status_code=302)

    async with httpx.AsyncClient() as client:
        r = await client.get(f"{API_BASE}/roles", headers=headers)

    if r.status_code == 200:
        roles = r.json()
        return templates.TemplateResponse(
            "roles/list.html",
            {"request": request, "prefixes": prefixes, "roles": roles, "error": None},
        )
    else:
        return templates.TemplateResponse(
            "roles/list.html",
            {
                "request": request,
                "prefixes": prefixes,
                "roles": [],
                "error": "Failed to load roles",
            },
        )


@router.get("/roles/{role_id}", response_class=HTMLResponse)
async def view_role(request: Request, role_id: int):
    """View role details"""
    headers = _auth_headers_from_cookies(request)
    if not headers:
        return RedirectResponse(url=f"{prefixes['auth']}/login", status_code=302)

    async with httpx.AsyncClient() as client:
        r = await client.get(f"{API_BASE}/roles/{role_id}", headers=headers)

    if r.status_code == 200:
        role = r.json()
        return templates.TemplateResponse(
            "roles/detail.html",
            {"request": request, "prefixes": prefixes, "role": role, "error": None},
        )
    else:
        return templates.TemplateResponse(
            "roles/detail.html",
            {
                "request": request,
                "prefixes": prefixes,
                "role": None,
                "error": "Role not found",
            },
        )
