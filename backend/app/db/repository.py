"""
Generic repository pattern.
Every domain module will extend BaseRepository for its models,
keeping database logic out of route handlers and domain services.
"""

import uuid
from typing import Any, Generic, Sequence, Type, TypeVar

from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base_model import BaseModel

ModelT = TypeVar("ModelT", bound=BaseModel)


class BaseRepository(Generic[ModelT]):
    def __init__(self, model: Type[ModelT], session: AsyncSession) -> None:
        self.model = model
        self.session = session

    # --- Read --------------------------------------------------

    async def get_by_id(self, id: uuid.UUID) -> ModelT | None:
        result = await self.session.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()

    async def get_all(
        self,
        *,
        skip: int = 0,
        limit: int = 50,
        filters: list[Any] | None = None,
        order_by: Any | None = None,
    ) -> Sequence[ModelT]:
        q = select(self.model)
        if filters:
            q = q.where(*filters)
        if order_by is not None:
            q = q.order_by(order_by)
        else:
            q = q.order_by(self.model.created_at.desc())
        q = q.offset(skip).limit(limit)
        result = await self.session.execute(q)
        return result.scalars().all()

    async def count(self, filters: list[Any] | None = None) -> int:
        q = select(func.count()).select_from(self.model)
        if filters:
            q = q.where(*filters)
        result = await self.session.execute(q)
        return result.scalar_one()

    # --- Write -----------------------------------------------

    async def create(self, **kwargs: Any) -> ModelT:
        obj = self.model(**kwargs)
        self.session.add(obj)
        await self.session.flush()  # flush to get DB-generated values (id, timestamps)
        await self.session.refresh(obj)
        return obj

    async def update(self, id: uuid.UUID, **kwargs: Any) -> ModelT | None:
        await self.session.execute(
            update(self.model)
            .where(self.model.id == id)
            .values(**kwargs)
            .execution_options(synchronize_session="fetch")
        )
        return await self.get_by_id(id)

    async def delete(self, id: uuid.UUID) -> bool:
        result = await self.session.execute(
            delete(self.model).where(self.model.id == id)
        )
        return result.rowcount > 0

    # --- Helpers --------------------------------------------

    async def exists(self, filters: list[Any]) -> bool:
        q = select(func.count()).select_from(self.model).where(*filters)
        result = await self.session.execute(q)
        return result.scalar_one() > 0
