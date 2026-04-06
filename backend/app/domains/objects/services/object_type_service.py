import uuid
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.objects.models import ObjectType, FieldDefinition
from app.domains.objects.repositories.object_type_repository import ObjectTypeRepository
from app.schemas.object_type import (
    ObjectTypeCreate,
    ObjectTypeUpdate,
    FieldDefinitionCreate,
)


class ObjectTypeService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = ObjectTypeRepository(session)

    async def list_object_types(self) -> list[ObjectType]:
        return await self.repo.list_all()

    async def get_object_type(self, object_type_id: uuid.UUID) -> ObjectType:
        obj = await self.repo.get_with_fields(object_type_id)
        if not obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"ObjectType {object_type_id} not found",
            )
        return obj

    async def get_by_api_name(self, api_name: str) -> ObjectType:
        obj = await self.repo.get_by_api_name(api_name)
        if not obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"ObjectType {api_name} not found",
            )
        return obj

    async def create_object_type(self, data: ObjectTypeCreate) -> ObjectType:
        existing = await self.repo.get_by_api_name(data.api_name)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"ObjectType '{data.api_name}' already exists",
            )

        obj = ObjectType(
            api_name=data.api_name,
            label=data.label,
            label_plural=data.label_plural,
            description=data.description,
            icon=data.icon,
            color=data.color,
            is_system=False,
        )
        self.session.add(obj)
        await self.session.flush()

        # Create field definitions
        for i, field_data in enumerate(data.fields):
            await self._add_field(obj.id, field_data, sort_order=i, is_system=False)

        await self.session.refresh(obj)
        return obj

    async def update_object_type(
        self, object_type_id: uuid.UUID, data: ObjectTypeUpdate
    ) -> ObjectType:
        await self.get_object_type(object_type_id)
        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            return await self.get_object_type(object_type_id)
        return await self.repo.update(object_type_id, **update_data)

    async def delete_object_type(self, object_type_id: uuid.UUID) -> None:
        obj = await self.get_object_type(object_type_id)
        if obj.is_system:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="System object types cannot be deleted",
            )
        await self.repo.delete(object_type_id)

    async def add_field(
        self, object_type_id: uuid.UUID, data: FieldDefinitionCreate
    ) -> FieldDefinition:
        obj = await self.get_object_type(object_type_id)

        # Check duplicate api_name within this object type
        existing = next(
            (f for f in obj.field_definitions if f.api_name == data.api_name), None
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Field '{data.api_name}' already exists",
            )
        return await self._add_field(object_type_id, data)

    async def delete_field(
        self, object_type_id: uuid.UUID, field_id: uuid.UUID
    ) -> None:
        obj = await self.get_object_type(object_type_id)
        field = next((f for f in obj.field_definitions if f.id == field_id), None)
        if not field:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Field not found"
            )

        if field.is_system:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="System fields cannot be deleted",
            )

        await self.session.delete(field)

    async def _add_field(
        self,
        object_type_id: uuid.UUID,
        data: FieldDefinitionCreate,
        sort_order: int | None = None,
        is_system: bool = False,
    ) -> FieldDefinition:
        field = FieldDefinition(
            object_type_id=object_type_id,
            api_name=data.api_name,
            label=data.label,
            field_type=data.field_type,
            is_required=data.is_required,
            is_searchable=data.is_searchable,
            sort_order=sort_order if sort_order is not None else data.sort_order,
            options=data.options,
            is_system=is_system,
        )
        self.session.add(field)
        await self.session.flush()
        return field
