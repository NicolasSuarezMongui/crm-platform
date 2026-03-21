import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import CurrentUser, RequirePermission
from app.db.session import get_db
from app.domains.iam.services.user_service import UserService
from app.schemas.pagination import PaginatedResponse
from app.schemas.user import (
    UserCreate,
    UserUpdate,
    UserUpdatePassword,
    UserResponse,
    UserSummary,
    AssignRolesRequest,
)

router = APIRouter()


def get_user_service(db: Annotated[AsyncSession, Depends(get_db)]) -> UserService:
    return UserService(db)


@router.get("/", response_model=PaginatedResponse[UserSummary])
async def list_users(
    current_user: CurrentUser,
    service: Annotated[UserService, Depends(get_user_service)],
    _=RequirePermission("users", "read"),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    search: str | None = Query(default=None, max_length=100),
    is_active: bool | None = Query(default=None),
):
    users, total = await service.list_users(
        skip=skip, limit=limit, search=search, is_active=is_active
    )
    return PaginatedResponse(items=users, total=total, skip=skip, limit=limit)


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: CurrentUser):
    """Current authenticated user — no special permission required."""
    return current_user


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: uuid.UUID,
    current_user: CurrentUser,
    service: Annotated[UserService, Depends(get_user_service)],
    _=RequirePermission("users", "read"),
):
    user = await service.get_user(user_id)
    print(f"[DEBUG] User Data: {user.__dict__}")  # Debug print to check user data
    return user


@router.post(
    "/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[RequirePermission("users", "write")],
)
async def create_user(
    body: UserCreate,
    service: Annotated[UserService, Depends(get_user_service)],
):
    return await service.create_user(body)


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: uuid.UUID,
    body: UserUpdate,
    current_user: CurrentUser,
    service: Annotated[UserService, Depends(get_user_service)],
):
    # Users can update themselves; admins can update anyone
    if current_user.id != user_id:
        from app.core.dependencies import RequirePermission
        if not any(r.has_permission("users", "write") for r in current_user.roles):
            from fastapi import HTTPException
            raise HTTPException(
                status_code=403, detail="Cannot update another user")

    return await service.update_user(user_id, body)


@router.patch(
    "/{user_id}/password",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def change_password(
    user_id: uuid.UUID,
    body: UserUpdatePassword,
    current_user: CurrentUser,
    service: Annotated[UserService, Depends(get_user_service)],
):
    await service.change_password(user_id, body, requester=current_user)


@router.patch(
    "/{user_id}/deactivate",
    response_model=UserResponse,
    dependencies=[RequirePermission("users", "write")],
)
async def deactivate_user(
    user_id: uuid.UUID,
    current_user: CurrentUser,
    service: Annotated[UserService, Depends(get_user_service)],
):
    return await service.deactivate_user(user_id, requester=current_user)


@router.patch(
    "/{user_id}/reactivate",
    response_model=UserResponse,
    dependencies=[RequirePermission("users", "write")],
)
async def reactivate_user(
    user_id: uuid.UUID,
    service: Annotated[UserService, Depends(get_user_service)],
):
    return await service.reactivate_user(user_id)


@router.put(
    "/{user_id}/roles",
    response_model=UserResponse,
    dependencies=[RequirePermission("users", "write")],
)
async def assign_roles(
    user_id: uuid.UUID,
    body: AssignRolesRequest,
    service: Annotated[UserService, Depends(get_user_service)],
):
    """Replace all roles for a user (full replacement, not append)."""
    return await service.assign_roles(user_id, body)
