from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import httpx
import os
from config import AUTH_PREFIX

API_BASE = os.getenv("API_BASE", "http://auth-service:8000/api/v1")

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


async def get_access_token(request: Request) -> str | None:
    return request.cookies.get("access_token")


@router.get("/", response_class=HTMLResponse)
async def root():
    return RedirectResponse(url=f"/{AUTH_PREFIX}/dashboard")


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(
    request: Request, access_token: str | None = Depends(get_access_token)
):
    if not access_token:
        return RedirectResponse(url=f"/{AUTH_PREFIX}login")

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
        "dashboard.html", {"request": request, "user": user}
    )


@router.get("/profile", response_class=HTMLResponse)
async def profile(
    request: Request, access_token: str | None = Depends(get_access_token)
):
    if not access_token:
        return RedirectResponse(url=f"/{AUTH_PREFIX}login")
    headers = {"Authorization": f"Bearer {access_token}"}
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{API_BASE}/auth/me", headers=headers)
    if r.status_code != 200:
        return RedirectResponse(url=f"/{AUTH_PREFIX}login")
    user = r.json()
    return templates.TemplateResponse(
        "profile.html", {"request": request, "user": user}
    )


@router.get("/profile/security", response_class=HTMLResponse)
async def security_settings(
    request: Request, access_token: str | None = Depends(get_access_token)
):
    if not access_token:
        return RedirectResponse(url=f"/{AUTH_PREFIX}login")
    return templates.TemplateResponse(
        "security_settings.html",
        {"request": request, "change_ok": False, "disable_ok": False, "error": None},
    )
