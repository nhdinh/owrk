from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
import httpx
import os
from ..common import get_logger, prefixes

API_BASE = os.getenv("API_BASE", "http://auth-service:8000/api/v1")

router = APIRouter()
logger = get_logger(__name__)

# Import templates from main module (configured with common templates)
from ..main import templates


async def get_access_token(request: Request) -> str | None:
    return request.cookies.get("access_token")


@router.get("/", response_class=HTMLResponse)
async def root():
    # When behind nginx at /auth/, redirect to /auth/dashboard
    return RedirectResponse(url=f"{prefixes['auth']}/dashboard")


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(
    request: Request, access_token: str | None = Depends(get_access_token)
):
    if not access_token:
        return RedirectResponse(url=f"{prefixes['auth']}/login")

    # Fetch user data from auth-api
    headers = {"Authorization": f"Bearer {access_token}"}
    user = None
    try:
        async with httpx.AsyncClient() as client:
            r = await client.get(f"{API_BASE}/auth/me", headers=headers)
            if r.status_code == 200:
                user = r.json()
    except Exception as e:
        print(f"Error fetching user data: {e}")

    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request, "user": user, "prefixes": prefixes},
    )


@router.get("/profile", response_class=HTMLResponse)
async def profile(
    request: Request, access_token: str | None = Depends(get_access_token)
):
    if not access_token:
        return RedirectResponse(url=f"{prefixes['auth']}/login")
    headers = {"Authorization": f"Bearer {access_token}"}
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{API_BASE}/auth/me", headers=headers)
    if r.status_code != 200:
        return RedirectResponse(url=f"{prefixes['auth']}/login")
    user = r.json()
    return templates.TemplateResponse(
        "profile.html", {"request": request, "user": user, "prefixes": prefixes}
    )


@router.get("/profile/security", response_class=HTMLResponse)
async def security_settings(
    request: Request, access_token: str | None = Depends(get_access_token)
):
    if not access_token:
        return RedirectResponse(url=f"{prefixes['auth']}/login")
    return templates.TemplateResponse(
        "security_settings.html",
        {
            "request": request,
            "prefixes": prefixes,
            "change_ok": False,
            "disable_ok": False,
            "error": None,
        },
    )
