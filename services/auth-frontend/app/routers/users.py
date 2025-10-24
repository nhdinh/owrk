"""
Auth Frontend Routes
"""

from fastapi import APIRouter, Request, Form
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


@router.get("/users", response_class=HTMLResponse)
async def list_users(request: Request):
    """List all users"""
    headers = _auth_headers_from_cookies(request)
    if not headers:
        return RedirectResponse(url=f"{prefixes['auth']}/login", status_code=302)

    async with httpx.AsyncClient() as client:
        r = await client.get(f"{API_BASE}/users", headers=headers)

    if r.status_code == 200:
        users = r.json()

        return templates.TemplateResponse(
            "users/list.html",
            {"request": request, "prefixes": prefixes, "users": users, "error": None},
        )
    else:
        return templates.TemplateResponse(
            "users/list.html",
            {
                "request": request,
                "prefixes": prefixes,
                "users": [],
                "error": "Failed to load users",
            },
        )


@router.get("/users/create", response_class=HTMLResponse)
async def create_user_form(request: Request):
    """Show create user form"""
    headers = _auth_headers_from_cookies(request)
    if not headers:
        return RedirectResponse(url=f"{prefixes['auth']}/login", status_code=302)

    return templates.TemplateResponse(
        "users/create.html", {"request": request, "prefixes": prefixes, "error": None}
    )


@router.post("/users")
async def create_user(
    request: Request,
    email: str = Form(...),
    full_name: str = Form(...),
    username: str = Form(None),
    password: str = Form(...),
    role_id: int = Form(...),
):
    """Create new user"""
    headers = _auth_headers_from_cookies(request)
    if not headers:
        return RedirectResponse(url=f"{prefixes['auth']}/login", status_code=302)

    payload = {
        "email": email,
        "full_name": full_name,
        "username": username,
        "password": password,
        "role_id": role_id,
    }

    async with httpx.AsyncClient() as client:
        r = await client.post(f"{API_BASE}/users", json=payload, headers=headers)

    if r.status_code == 201:
        return RedirectResponse(url=f"{prefixes['auth']}/users", status_code=302)
    else:
        return templates.TemplateResponse(
            "users/create.html",
            {
                "request": request,
                "prefixes": prefixes,
                "error": "Failed to create user",
            },
        )


@router.get("/users/{user_id}", response_class=HTMLResponse)
async def view_user(request: Request, user_id: int):
    """View user details"""
    headers = _auth_headers_from_cookies(request)
    if not headers:
        return RedirectResponse(url=f"{prefixes['auth']}/login", status_code=302)

    async with httpx.AsyncClient() as client:
        r = await client.get(f"{API_BASE}/users/{user_id}", headers=headers)

    if r.status_code == 200:
        user = r.json()
        return templates.TemplateResponse(
            "users/detail.html",
            {"request": request, "prefixes": prefixes, "user": user, "error": None},
        )
    else:
        return templates.TemplateResponse(
            "users/detail.html",
            {
                "request": request,
                "prefixes": prefixes,
                "user": None,
                "error": "User not found",
            },
        )
