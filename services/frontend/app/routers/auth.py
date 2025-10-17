from fastapi import APIRouter, Request, Depends, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import httpx
import os

API_BASE = os.getenv("API_BASE", "http://auth-service:8000/api/v1")

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


def set_auth_cookies(response: RedirectResponse, access_token: str, refresh_token: str):
    response.set_cookie("access_token", access_token, httponly=True, samesite="lax")
    response.set_cookie("refresh_token", refresh_token, httponly=True, samesite="lax")


@router.get("/login", response_class=HTMLResponse)
async def get_login(request: Request):
    return templates.TemplateResponse(
        "auth/login.html", {"request": request, "error": None}
    )


@router.post("/login")
async def post_login(
    request: Request, email: str = Form(...), password: str = Form(...)
):
    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"{API_BASE}/auth/login", json={"email": email, "password": password}
        )
    if r.status_code != 200:
        return templates.TemplateResponse(
            "auth/login.html",
            {"request": request, "error": "Đăng nhập thất bại"},
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    data = r.json()
    if data.get("requires_mfa"):
        request.session["temp_token"] = data["temp_token"]
        return RedirectResponse(url="/verify-otp", status_code=status.HTTP_302_FOUND)
    # No MFA: simulate step 2 with dummy otp (backend will skip when mfa_enabled False)
    async with httpx.AsyncClient() as client:
        r2 = await client.post(
            f"{API_BASE}/auth/verify-otp",
            json={"temp_token": data["temp_token"], "otp_code": "000000"},
        )
    if r2.status_code != 200:
        return templates.TemplateResponse(
            "auth/login.html",
            {"request": request, "error": "OTP không hợp lệ"},
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    td = r2.json()
    resp = RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)
    set_auth_cookies(resp, td["access_token"], td["refresh_token"])
    return resp


@router.get("/verify-otp", response_class=HTMLResponse)
async def get_verify_otp(request: Request):
    if not request.session.get("temp_token"):
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse(
        "auth/verify_otp.html", {"request": request, "error": None}
    )


@router.post("/verify-otp")
async def post_verify_otp(request: Request, otp_code: str = Form(...)):
    temp_token = request.session.get("temp_token")
    if not temp_token:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"{API_BASE}/auth/verify-otp",
            json={"temp_token": temp_token, "otp_code": otp_code},
        )
    if r.status_code != 200:
        return templates.TemplateResponse(
            "auth/verify_otp.html",
            {"request": request, "error": "OTP không hợp lệ"},
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    data = r.json()
    resp = RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)
    set_auth_cookies(resp, data["access_token"], data["refresh_token"])
    request.session.pop("temp_token", None)
    return resp


@router.get("/logout")
async def logout():
    resp = RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    resp.delete_cookie("access_token")
    resp.delete_cookie("refresh_token")
    return resp


# ===================== Forgot / Reset Password =====================

@router.get("/forgot-password", response_class=HTMLResponse)
async def get_forgot_password(request: Request):
    return templates.TemplateResponse(
        "auth/forgot_password.html", {"request": request, "sent": False, "error": None}
    )


@router.post("/forgot-password")
async def post_forgot_password(request: Request, email: str = Form(...)):
    async with httpx.AsyncClient() as client:
        r = await client.post(f"{API_BASE}/auth/forgot-password", json={"email": email})
    if r.status_code != 200:
        return templates.TemplateResponse(
            "auth/forgot_password.html",
            {"request": request, "sent": False, "error": "Không thể gửi hướng dẫn đặt lại mật khẩu"},
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    data = r.json()
    # Dev note: backend trả về token trong dev; hiển thị để test nhanh
    return templates.TemplateResponse(
        "auth/forgot_password.html",
        {"request": request, "sent": True, "dev_token": data.get("token"), "error": None},
    )


@router.get("/reset-password", response_class=HTMLResponse)
async def get_reset_password(request: Request):
    token = request.query_params.get("token")
    if not token:
        return RedirectResponse(url="/forgot-password", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse(
        "auth/reset_password.html", {"request": request, "token": token, "error": None, "success": False}
    )


@router.post("/reset-password")
async def post_reset_password(request: Request, token: str = Form(...), new_password: str = Form(...)):
    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"{API_BASE}/auth/reset-password", json={"token": token, "new_password": new_password}
        )
    if r.status_code != 200:
        return templates.TemplateResponse(
            "auth/reset_password.html",
            {"request": request, "token": token, "error": "Mã đặt lại không hợp lệ hoặc đã hết hạn", "success": False},
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    return templates.TemplateResponse(
        "auth/reset_password.html",
        {"request": request, "token": token, "error": None, "success": True},
    )


# ===================== MFA Setup / Enable =====================

def _auth_headers_from_cookies(request: Request) -> dict:
    access = request.cookies.get("access_token")
    return {"Authorization": f"Bearer {access}"} if access else {}


@router.get("/mfa-setup", response_class=HTMLResponse)
async def get_mfa_setup(request: Request):
    headers = _auth_headers_from_cookies(request)
    if not headers:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{API_BASE}/auth/mfa/setup", headers=headers)
    if r.status_code != 200:
        return templates.TemplateResponse(
            "auth/mfa_setup.html",
            {"request": request, "error": "Không thể khởi tạo MFA", "data": None},
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    data = r.json()
    return templates.TemplateResponse("auth/mfa_setup.html", {"request": request, "error": None, "data": data})


@router.post("/mfa-setup")
async def post_mfa_enable(request: Request, otp_code: str = Form(...)):
    headers = _auth_headers_from_cookies(request)
    if not headers:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    async with httpx.AsyncClient() as client:
        r = await client.post(f"{API_BASE}/auth/mfa/enable", headers=headers, json={"otp_code": otp_code})
    if r.status_code != 200:
        # Reload setup data on error to re-display QR/backup codes if needed (optional)
        async with httpx.AsyncClient() as client:
            setup_r = await client.get(f"{API_BASE}/auth/mfa/setup", headers=headers)
        setup_data = setup_r.json() if setup_r.status_code == 200 else None
        return templates.TemplateResponse(
            "auth/mfa_setup.html",
            {"request": request, "error": "OTP không hợp lệ", "data": setup_data},
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    return RedirectResponse(url="/profile", status_code=status.HTTP_302_FOUND)


# ===================== Security Settings: Change Password / Disable MFA =====================

@router.post("/change-password")
async def change_password(
    request: Request,
    current_password: str = Form(...),
    new_password: str = Form(...),
):
    headers = _auth_headers_from_cookies(request)
    if not headers:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    payload = {"current_password": current_password, "new_password": new_password}
    async with httpx.AsyncClient() as client:
        r = await client.post(f"{API_BASE}/users/change-password", headers=headers, json=payload)
    if r.status_code != 200:
        return RedirectResponse(url="/profile/security?error=change", status_code=status.HTTP_302_FOUND)
    return RedirectResponse(url="/profile/security?ok=change", status_code=status.HTTP_302_FOUND)


@router.post("/mfa-disable")
async def mfa_disable(
    request: Request,
    password: str = Form(...),
    otp_code: str | None = Form(None),
    backup_code: str | None = Form(None),
):
    headers = _auth_headers_from_cookies(request)
    if not headers:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    payload = {"password": password, "otp_code": otp_code, "backup_code": backup_code}
    async with httpx.AsyncClient() as client:
        r = await client.post(f"{API_BASE}/auth/mfa/disable", headers=headers, json=payload)
    if r.status_code != 200:
        return RedirectResponse(url="/profile/security?error=mfa", status_code=status.HTTP_302_FOUND)
    return RedirectResponse(url="/profile/security?ok=mfa", status_code=status.HTTP_302_FOUND)
