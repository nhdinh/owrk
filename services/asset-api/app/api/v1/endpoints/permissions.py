from typing import List, Union
from fastapi import APIRouter, Depends

from app.core.dependencies import get_current_user
from app.schemas.asset_schema import PermissionResponse


router = APIRouter()


@router.get("/")
async def list_permissions(
    active_only: bool = False, current_user: dict = Depends(get_current_user)
):
    return {}
