import uuid
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.objects.models import ObjectType, Record
from app.domains.objects.repositories.record_repository import RecordRepository
from app.domains.objects.repositories.object_type_repository import ObjectTypeRepository
from app.domains.objects.field_validator import validate_record_data
from app.schemas.record import RecordCreate, RecordUpdate


class RecordService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = RecordRepository(session)
        self.type_repo = ObjectTypeRepository(session)

    async def list_records(
        self,
        object_type_api_name: str,
        skip: int = 0,
        limit: int = 20,
        search: str | None = None,
        stage: str | None = None,
        owner_id: uuid.UUID | None = None,
    ) -> tuple[list[Record], int]:
        obj_type = await self._resolve_type(object_type_api_name)
        return await self.repo.list_paginated(
            object_type_id=obj_type.id,
            skip=skip,
            limit=limit,
            search=search,
            stage=stage,
            owner_id=owner_id,
        )

    async def get_record(self, record_id: uuid.UUID) -> Record:
        record = await self.repo.get_by_id(record_id)
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Record {record_id} not found",
            )
        return record

    async def create_record(
        self, object_type_api_name: str, data: RecordCreate, current_user_id: uuid.UUID
    ) -> Record:
        obj_type = await self._resolve_type(object_type_api_name)

        validated_data = validate_record_data(
            data.data, obj_type.field_definitions, is_partial=False
        )

        record = Record(
            object_type_id=obj_type.id,
            owner_id=data.owner_id or current_user_id,
            name=data.name,
            stage=data.stage,
            data=validated_data,
        )

        self.session.add(record)
        await self.session.flush()
        await self.session.refresh(record)
        return record

    async def update_record(self, record_id: uuid.UUID, data: RecordUpdate) -> Record:
        record = await self.get_record(record_id)

        update_kwargs: dict = {}

        if data.name is not None:
            update_kwargs["name"] = data.name
        if data.stage is not None:
            update_kwargs["stage"] = data.stage
        if data.owner_id is not None:
            update_kwargs["owner_id"] = data.owner_id

        if data.data is not None:
            # Load field definitions for validation
            obj_type = await self.type_repo.get_with_fields(record.object_type_id)
            if not obj_type:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="ObjectType not found",
                )

            validated_data = validate_record_data(
                data.data,
                obj_type.field_definitions,
                is_partial=True,  # PATCH - only validate provided fields
            )
            # Merge with existing data instead of replacing
            merged = {**record.data, **validated_data}
            update_kwargs["data"] = merged

        if not update_kwargs:
            return record

        return await self.repo.update(record_id, **update_kwargs)

    async def delete_record(self, record_id: uuid.UUID) -> None:
        await self.get_record(record_id)
        await self.repo.delete(record_id)

    async def _resolve_type(self, api_name: str):
        obj_type = await self.type_repo.get_by_api_name(api_name)
        if not obj_type:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Object type '{api_name}' not found",
            )
        return obj_type
