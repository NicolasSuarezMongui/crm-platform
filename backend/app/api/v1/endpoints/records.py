import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import CurrentUser, RequirePermission
from app.db.session import get_db
from app.domains.objects.services.record_service import RecordService
from app.schemas.pagination import PaginatedResponse
from app.schemas.record import RecordCreate, RecordUpdate, RecordResponse

router = APIRouter()


def get_service(db: Annotated[AsyncSession, Depends(get_db)]) -> RecordService:
    return RecordService(db)


@router.get("", response_model=PaginatedResponse[RecordResponse])
async def list_records(
    service: Annotated[RecordService, Depends(get_service)],
    _=RequirePermission("contacts", "read"),
    object_type: str = Query(..., description="ObjectType api_name e.g. 'contect'"),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    search: str | None = Query(default=None),
    stage: str | None = Query(default=None),
    owner_id: uuid.UUID | None = Query(default=None),
):
    records, total = await service.list_records(
        object_type_api_name=object_type,
        skip=skip,
        limit=limit,
        search=search,
        stage=stage,
        owner_id=owner_id,
    )
    return PaginatedResponse(items=records, total=total, skip=skip, limit=limit)


@router.get("/{record_id}", response_model=RecordResponse)
async def get_record(
    record_id: uuid.UUID,
    service: Annotated[RecordService, Depends(get_service)],
    _=RequirePermission("contacts", "read"),
):
    return await service.get_record(record_id)


@router.post(
    "",
    response_model=RecordResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_record(
    body: RecordCreate,
    current_user: CurrentUser,
    service: Annotated[RecordService, Depends(get_service)],
    _=RequirePermission("contacts", "write"),
    object_type: str = Query(...),
):
    return await service.create_record(
        object_type_api_name=object_type,
        data=body,
        current_user_id=current_user.id,
    )


@router.patch("/{record_id}", response_model=RecordResponse)
async def update_record(
    record_id: uuid.UUID,
    body: RecordUpdate,
    service: Annotated[RecordService, Depends(get_service)],
    _=RequirePermission("contacts", "write"),
):
    return await service.update_record(record_id, body)


@router.delete(
    "/{record_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_record(
    record_id: uuid.UUID,
    service: Annotated[RecordService, Depends(get_service)],
    _=RequirePermission("contacts", "delete"),
):
    await service.delete_record(record_id)
