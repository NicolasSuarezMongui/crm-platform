import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.repository import BaseRepository
from app.domains.objects.models import ObjectType


class ObjectTypeRepository(BaseRepository[ObjectType]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(ObjectType, session)

    async def get_by_api_name(self, api_name: str) -> ObjectType | None:
        result = await self.session.execute(
            select(ObjectType)
            .where(ObjectType.api_name == api_name)
            .options(selectinload(ObjectType.field_definitions))
        )
        return result.scalar_one_or_none()

    async def get_with_fields(self, object_type_id: uuid.UUID) -> ObjectType | None:
        result = await self.session.execute(
            select(ObjectType)
            .where(ObjectType.id == object_type_id)
            .options(selectinload(ObjectType.field_definitions))
        )
        return result.scalar_one_or_none()

    async def list_all(self) -> list[ObjectType]:
        result = await self.session.execute(
            select(ObjectType)
            .options(selectinload(ObjectType.field_definitions))
            .order_by(ObjectType.label)
        )
        return list(result.scalars().all())
