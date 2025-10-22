"""
Asset Management Routes
"""
import os
import httpx
import logging
from fastapi import APIRouter, Request, Form, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from typing import Optional

logger = logging.getLogger(__name__)

router = APIRouter()

# Asset API base URL
ASSET_API_URL = os.getenv("ASSET_API_URL", "http://asset-api:8000/api/v1")

# Import templates from main module (configured with common templates)
from ..main import templates


async def get_api_client():
    """Get HTTP client for API calls"""
    return httpx.AsyncClient(base_url=ASSET_API_URL, timeout=30.0)


@router.get("/", response_class=HTMLResponse)
async def list_assets(
    request: Request,
    search: Optional[str] = None,
    category_id: Optional[int] = None,
    status: Optional[str] = None,
    page: int = 1,
    page_size: int = 20
):
    """Asset list page with search and filters"""
    try:
        async with await get_api_client() as client:
            # Fetch assets
            params = {
                "page": page,
                "page_size": page_size
            }
            if search:
                params["search"] = search
            if category_id:
                params["category_id"] = category_id
            if status:
                params["status"] = status

            # Mock token for now - in production, get from session
            headers = {"Authorization": "Bearer mock-token"}

            try:
                response = await client.get("/assets/", params=params, headers=headers)
                response.raise_for_status()
                assets_data = response.json()
            except httpx.HTTPStatusError:
                assets_data = {"items": [], "total": 0, "page": 1, "page_size": 20}

            # Fetch categories for filter
            try:
                cat_response = await client.get("/categories/", headers=headers)
                categories = cat_response.json() if cat_response.status_code == 200 else []
            except:
                categories = []

            return templates.TemplateResponse(
                "assets/list.html",
                {
                    "request": request,
                    "assets": assets_data.get("items", []),
                    "total": assets_data.get("total", 0),
                    "page": page,
                    "page_size": page_size,
                    "categories": categories,
                    "search": search,
                    "category_id": category_id,
                    "status": status
                }
            )
    except Exception as e:
        logger.error(f"Error fetching assets: {e}")
        return templates.TemplateResponse(
            "assets/list.html",
            {
                "request": request,
                "assets": [],
                "total": 0,
                "page": 1,
                "page_size": 20,
                "categories": [],
                "error": str(e)
            }
        )


@router.get("/{asset_id}", response_class=HTMLResponse)
async def asset_detail(request: Request, asset_id: int):
    """Asset detail page"""
    try:
        async with await get_api_client() as client:
            headers = {"Authorization": "Bearer mock-token"}

            try:
                response = await client.get(f"/assets/{asset_id}", headers=headers)
                response.raise_for_status()
                asset = response.json()
            except httpx.HTTPStatusError as e:
                raise HTTPException(status_code=e.response.status_code, detail="Asset not found")

            # Fetch assignment history
            try:
                history_response = await client.get(f"/assets/{asset_id}/history", headers=headers)
                history = history_response.json() if history_response.status_code == 200 else []
            except:
                history = []

            # Fetch depreciation records
            try:
                dep_response = await client.get(f"/assets/{asset_id}/depreciation", headers=headers)
                depreciation = dep_response.json() if dep_response.status_code == 200 else []
            except:
                depreciation = []

            return templates.TemplateResponse(
                "assets/detail.html",
                {
                    "request": request,
                    "asset": asset,
                    "history": history,
                    "depreciation": depreciation
                }
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching asset detail: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/create", response_class=HTMLResponse)
async def create_asset_form(request: Request):
    """Create asset form page"""
    try:
        async with await get_api_client() as client:
            headers = {"Authorization": "Bearer mock-token"}

            # Fetch categories
            try:
                response = await client.get("/categories/", headers=headers)
                categories = response.json() if response.status_code == 200 else []
            except:
                categories = []

            return templates.TemplateResponse(
                "assets/form.html",
                {
                    "request": request,
                    "categories": categories,
                    "asset": None,
                    "action": "Create"
                }
            )
    except Exception as e:
        logger.error(f"Error loading create form: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/create")
async def create_asset(
    request: Request,
    name: str = Form(...),
    asset_code: str = Form(...),
    category_id: int = Form(...),
    asset_type: str = Form(...),
    purchase_price: float = Form(...),
    purchase_date: str = Form(...),
    description: Optional[str] = Form(None)
):
    """Create new asset"""
    try:
        async with await get_api_client() as client:
            headers = {"Authorization": "Bearer mock-token"}

            asset_data = {
                "name": name,
                "asset_code": asset_code,
                "category_id": category_id,
                "asset_type": asset_type,
                "purchase_price": purchase_price,
                "purchase_date": purchase_date,
                "description": description
            }

            response = await client.post("/assets/", json=asset_data, headers=headers)
            response.raise_for_status()
            asset = response.json()

            return RedirectResponse(url=f"/assets/{asset['id']}", status_code=303)
    except Exception as e:
        logger.error(f"Error creating asset: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{asset_id}/edit", response_class=HTMLResponse)
async def edit_asset_form(request: Request, asset_id: int):
    """Edit asset form page"""
    try:
        async with await get_api_client() as client:
            headers = {"Authorization": "Bearer mock-token"}

            # Fetch asset
            response = await client.get(f"/assets/{asset_id}", headers=headers)
            response.raise_for_status()
            asset = response.json()

            # Fetch categories
            try:
                cat_response = await client.get("/categories/", headers=headers)
                categories = cat_response.json() if cat_response.status_code == 200 else []
            except:
                categories = []

            return templates.TemplateResponse(
                "assets/form.html",
                {
                    "request": request,
                    "categories": categories,
                    "asset": asset,
                    "action": "Edit"
                }
            )
    except Exception as e:
        logger.error(f"Error loading edit form: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{asset_id}/assign")
async def assign_asset(
    asset_id: int,
    user_id: int = Form(...),
    assigned_by: int = Form(...),
    notes: Optional[str] = Form(None)
):
    """Assign asset to user"""
    try:
        async with await get_api_client() as client:
            headers = {"Authorization": "Bearer mock-token"}

            assign_data = {
                "user_id": user_id,
                "assigned_by": assigned_by,
                "notes": notes
            }

            response = await client.post(f"/assets/{asset_id}/assign", json=assign_data, headers=headers)
            response.raise_for_status()

            return RedirectResponse(url=f"/assets/{asset_id}", status_code=303)
    except Exception as e:
        logger.error(f"Error assigning asset: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{asset_id}/return")
async def return_asset(
    asset_id: int,
    assignment_id: int = Form(...),
    return_condition: str = Form(...),
    notes: Optional[str] = Form(None)
):
    """Return asset from user"""
    try:
        async with await get_api_client() as client:
            headers = {"Authorization": "Bearer mock-token"}

            return_data = {
                "assignment_id": assignment_id,
                "return_condition": return_condition,
                "notes": notes
            }

            response = await client.post(f"/assets/{asset_id}/return", json=return_data, headers=headers)
            response.raise_for_status()

            return RedirectResponse(url=f"/assets/{asset_id}", status_code=303)
    except Exception as e:
        logger.error(f"Error returning asset: {e}")
        raise HTTPException(status_code=500, detail=str(e))
