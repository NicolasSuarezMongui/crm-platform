import uuid
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.repository import BaseRepository
from app.domains.objects.models import Record, ObjectType


class RecordRepository(BaseRepository[Record]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Record, session)

    async def list_paginated(
        self,
        object_type_id: uuid.UUID,
        skip: int = 0,
        limit: int = 20,
        search: str | None = None,
        stage: str | None = None,
        owner_id: uuid.UUID | None = None,
    ) -> tuple[list[Record], int]:
        filters = [Record.object_type_id == object_type_id]

        if search:
            filters.append(Record.name.ilike(f"%{search}%"))
        if stage:
            filters.append(Record.stage == stage)
        if owner_id:
            filters.append(Record.owner_id == owner_id)

        count_q = select(func.count()).select_from(Record).where(*filters)
        total = (await self.session.execute(count_q)).scalar_one()

        data_q = (
            select(Record)
            .where(*filters)
            .order_by(Record.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        rows = (await self.session.execute(data_q)).scalars().all()

        return list(rows), total

    async def get_with_type(self, record_id: uuid.UUID) -> Record | None:
        result = await self.session.execute(
            select(Record)
            .where(Record.id == record_id)
            .options(selectinload(Record.object_type))
        )
        return result.scalar_one_or_none()
