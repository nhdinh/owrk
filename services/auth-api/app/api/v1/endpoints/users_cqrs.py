"""
Users CQRS Endpoints - Demo endpoints using CQRS pattern via Message Bus
This demonstrates the new architecture with Command/Query separation
"""

from typing import List, Dict
from fastapi import APIRouter, Depends, HTTPException, status, Query as QueryParam

from app.core.dependencies import get_current_user, get_message_bus
from app.core.database import get_db
from app.core.message_bus import MessageBus
from app.models.user import User
from sqlalchemy.orm import Session
from app.schemas.user_schema import UserCreate, UserUpdate, UserResponse
from app.schemas.commands.user_commands import (
    CreateUserCommand,
    UpdateUserCommand,
    DeleteUserCommand,
    ActivateUserCommand,
    DeactivateUserCommand,
)
from app.schemas.queries.user_queries import (
    GetUserByIdQuery,
    GetUsersListQuery,
    GetUserHistoryQuery,
)

router = APIRouter(prefix="/users-cqrs", tags=["users-cqrs"])


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user_cqrs(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    bus: MessageBus = Depends(get_message_bus),
    current_user: User = Depends(get_current_user),
):
    """
    Create new user using CQRS Command pattern

    **NEW**: This endpoint demonstrates the CQRS pattern:
    - Uses CreateUserCommand instead of direct service call
    - Command is dispatched through MessageBus
    - Handler automatically saves version history
    - Handler publishes event to RabbitMQ
    """
    # Create command
    # Use _auth_id to avoid detached instance error
    current_user_id = getattr(current_user, "_auth_id", None)
    if not current_user_id:
        raise HTTPException(status_code=401, detail="Invalid user session")

    command = CreateUserCommand(
        email=user_data.email,
        full_name=user_data.full_name,
        password=user_data.password,
        role_id=user_data.role_id,
        department_id=user_data.department_id,
        phone_number=user_data.phone_number,
        position=user_data.position,
        user_type=user_data.user_type or "local",
        created_by=current_user_id,
    )

    # Dispatch command via Message Bus with database session
    try:
        result = await bus.execute_command(command, db=db)
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create user: {str(e)}",
        )


@router.put("/{user_id}", response_model=UserResponse)
async def update_user_cqrs(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    bus: MessageBus = Depends(get_message_bus),
    current_user: User = Depends(get_current_user),
):
    """
    Update user using CQRS Command pattern

    **NEW**: Features:
    - Automatic version increment
    - Saves previous version to history table
    - Publishes UserUpdated event
    """
    # Use _auth_id to avoid detached instance error
    current_user_id = getattr(current_user, "_auth_id", None)
    if not current_user_id:
        raise HTTPException(status_code=401, detail="Invalid user session")

    # Create command with only provided fields
    command = UpdateUserCommand(
        user_id=user_id,
        full_name=user_data.full_name,
        phone_number=user_data.phone_number,
        position=user_data.position,
        department_id=user_data.department_id,
        role_id=user_data.role_id,
        updated_by=current_user_id,
    )

    try:
        result = await bus.execute_command(command, db=db)
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update user: {str(e)}",
        )


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_cqrs(
    user_id: int,
    db: Session = Depends(get_db),
    bus: MessageBus = Depends(get_message_bus),
    current_user: User = Depends(get_current_user),
):
    """
    Delete (soft delete) user using CQRS Command pattern
    """
    current_user_id = getattr(current_user, "_auth_id", None)
    if not current_user_id:
        raise HTTPException(status_code=401, detail="Invalid user session")

    command = DeleteUserCommand(user_id=user_id, deleted_by=current_user_id)

    try:
        await bus.execute_command(command, db=db)
        return None
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/{user_id}/activate", response_model=UserResponse)
async def activate_user_cqrs(
    user_id: int,
    db: Session = Depends(get_db),
    bus: MessageBus = Depends(get_message_bus),
    current_user: User = Depends(get_current_user),
):
    """
    Activate user account using CQRS Command pattern
    """
    current_user_id = getattr(current_user, "_auth_id", None)
    if not current_user_id:
        raise HTTPException(status_code=401, detail="Invalid user session")

    command = ActivateUserCommand(user_id=user_id, activated_by=current_user_id)

    try:
        result = await bus.execute_command(command, db=db)
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/{user_id}/deactivate", response_model=UserResponse)
async def deactivate_user_cqrs(
    user_id: int,
    db: Session = Depends(get_db),
    bus: MessageBus = Depends(get_message_bus),
    current_user: User = Depends(get_current_user),
):
    """
    Deactivate user account using CQRS Command pattern
    """
    current_user_id = getattr(current_user, "_auth_id", None)
    if not current_user_id:
        raise HTTPException(status_code=401, detail="Invalid user session")

    command = DeactivateUserCommand(user_id=user_id, deactivated_by=current_user_id)

    try:
        result = await bus.execute_command(command, db=db)
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/{user_id}", response_model=Dict)
async def get_user_cqrs(
    user_id: int,
    bus: MessageBus = Depends(get_message_bus),
    current_user: User = Depends(get_current_user),
):
    """
    Get user by ID using CQRS Query pattern

    **NEW**: Features:
    - Reads from MongoDB (fast read model)
    - Denormalized data (no joins needed)
    - Includes embedded role and department info
    """
    query = GetUserByIdQuery(user_id=user_id)

    try:
        result = await bus.execute_query(query)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found",
            )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user: {str(e)}",
        )


@router.get("/", response_model=Dict)
async def get_users_list_cqrs(
    skip: int = QueryParam(0, ge=0),
    limit: int = QueryParam(100, ge=1, le=1000),
    is_active: bool = QueryParam(None),
    role_id: int = QueryParam(None),
    department_id: int = QueryParam(None),
    search: str = QueryParam(None),
    bus: MessageBus = Depends(get_message_bus),
    current_user: User = Depends(get_current_user),
):
    """
    Get paginated users list using CQRS Query pattern

    **NEW**: Features:
    - Reads from MongoDB
    - Supports filtering and search
    - Returns total count for pagination
    """
    query = GetUsersListQuery(
        skip=skip,
        limit=limit,
        is_active=is_active,
        role_id=role_id,
        department_id=department_id,
        search=search,
    )

    try:
        result = await bus.execute_query(query)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get users list: {str(e)}",
        )


@router.get("/{user_id}/history", response_model=Dict)
async def get_user_history_cqrs(
    user_id: int,
    skip: int = QueryParam(0, ge=0),
    limit: int = QueryParam(50, ge=1, le=100),
    db: Session = Depends(get_db),
    bus: MessageBus = Depends(get_message_bus),
    current_user: User = Depends(get_current_user),
):
    """
    Get user version history using CQRS Query pattern

    **NEW**: Features:
    - Returns complete version history
    - Shows who changed what and when
    - Supports pagination
    - Ordered by version DESC
    """
    query = GetUserHistoryQuery(user_id=user_id, skip=skip, limit=limit)

    try:
        result = await bus.execute_query(query, db=db)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user history: {str(e)}",
        )
