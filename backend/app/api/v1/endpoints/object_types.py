import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import RequirePermission
from app.db.session import get_db
from app.domains.objects.services.object_type_service import ObjectTypeService
from app.schemas.object_type import (
    ObjectTypeCreate,
    ObjectTypeUpdate,
    ObjectTypeResponse,
    ObjectTypeSummary,
    FieldDefinitionCreate,
    FieldDefinitionResponse,
)

router = APIRouter()


def get_service(db: Annotated[AsyncSession, Depends(get_db)]) -> ObjectTypeService:
    return ObjectTypeService(db)


@router.get("", response_model=list[ObjectTypeSummary])
async def list_object_types(
    service: Annotated[ObjectTypeService, Depends(get_service)],
):
    return await service.list_object_types()


@router.get("/{object_type_id}", response_model=ObjectTypeResponse)
async def get_object_type(
    object_type_id: uuid.UUID,
    service: Annotated[ObjectTypeService, Depends(get_service)],
):
    return await service.get_object_type(object_type_id)


@router.post(
    "",
    response_model=ObjectTypeResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[RequirePermission("object_types", "manage")],
)
async def create_object_type(
    body: ObjectTypeCreate,
    service: Annotated[ObjectTypeService, Depends(get_service)],
):
    return await service.create_object_type(body)


@router.patch(
    "/{object_type_id}",
    response_model=ObjectTypeResponse,
    dependencies=[RequirePermission("object_types", "manage")],
)
async def update_object_type(
    object_type_id: uuid.UUID,
    body: ObjectTypeUpdate,
    service: Annotated[ObjectTypeService, Depends(get_service)],
):
    return await service.update_object_type(object_type_id, body)


@router.delete(
    "/{object_type_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[RequirePermission("object_types", "manage")],
)
async def delete_object_type(
    object_type_id: uuid.UUID,
    service: Annotated[ObjectTypeService, Depends(get_service)],
):
    await service.delete_object_type(object_type_id)


@router.post(
    "/{object_type_id}/fields",
    response_model=FieldDefinitionResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[RequirePermission("object_types", "manage")],
)
async def add_field(
    object_type_id: uuid.UUID,
    body: FieldDefinitionCreate,
    service: Annotated[ObjectTypeService, Depends(get_service)],
):
    return await service.add_field(object_type_id, body)


@router.delete(
    "/{object_type_id}/fields/{field_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[RequirePermission("object_types", "manage")],
)
async def delete_field(
    object_type_id: uuid.UUID,
    field_id: uuid.UUID,
    service: Annotated[ObjectTypeService, Depends(get_service)],
):
    await service.delete_field(object_type_id, field_id)
