from fastapi import APIRouter, Depends

from app.core.unit_of_work import UnitOfWork
from app.core.dependencies import require_permission
from app.models.user import User


router = APIRouter(prefix="/permissions", tags=["Collective Permissions"])


@router.get("")
async def get_permissions():
    with UnitOfWork() as uow:
        permissions = uow.permissions.get_all()

        # Serialize data within session context
        result = []
        for perm in permissions:
            result.append(
                {
                    "id": perm.id,
                    "name": perm.name,
                    "resource": perm.resource,
                }
            )

        return result
