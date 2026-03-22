import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import CurrentUser, RequirePermission
from app.db.session import get_db
from app.domains.iam.services.role_service import RoleService
from app.schemas.role import RoleCreate, RoleUpdate, RoleResponse, RoleWithUsersResponse

router = APIRouter()


def get_role_service(db: Annotated[AsyncSession, Depends(get_db)]) -> RoleService:
    return RoleService(db)


@router.get(
    "",
    response_model=list[RoleResponse],
    dependencies=[RequirePermission("users", "read")],
)
async def list_roles(
    service: Annotated[RoleService, Depends(get_role_service)],
):
    return await service.list_roles()


@router.get(
    "/{role_id}",
    response_model=RoleWithUsersResponse,
    dependencies=[RequirePermission("users", "read")],
)
async def get_role(
        role_id: uuid.UUID,
        service: Annotated[RoleService, Depends(get_role_service)],
):
    role, user_count = await service.get_role_detail(role_id)
    return RoleWithUsersResponse(
        **RoleResponse.model_validate(role).model_dump(),
        user_count=user_count,
    )


@router.post(
    "",
    response_model=RoleResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[RequirePermission("settings", "write")],
)
async def create_role(
    body: RoleCreate,
    service: Annotated[RoleService, Depends(get_role_service)],
):
    return await service.create_role(body)


@router.patch(
    "/{role_id}",
    response_model=RoleResponse,
    dependencies=[RequirePermission("settings", "write")],
)
async def update_role(
    role_id: uuid.UUID,
    body: RoleUpdate,
    service: Annotated[RoleService, Depends(get_role_service)],
):
    return await service.update_role(role_id, body)


@router.delete(
    "/{role_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[RequirePermission("settings", "write")],
)
async def delete_role(
    role_id: uuid.UUID,
    service: Annotated[RoleService, Depends(get_role_service)],
):
    await service.delete_role(role_id)
