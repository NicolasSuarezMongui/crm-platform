import uuid

from sqlalchemy import select, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.repository import BaseRepository
from app.domains.iam.models.user import User


class UserRepository(BaseRepository[User]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(User, session)

    async def get_by_email(self, email: str) -> User | None:
        result = await self.session.execute(
            select(User).where(User.email == email.lower())
        )
        return result.scalar_one_or_none()

    async def get_with_roles(self, user_id: uuid.UUID) -> User | None:
        result = await self.session.execute(
            select(User)
            .where(User.id == user_id)
            .options(selectinload(User.roles))
        )
        return result.scalar_one_or_none()

    async def list_paginated(
        self,
        skip: int = 0,
        limit: int = 20,
        search: str | None = None,
        is_active: bool | None = None,
    ) -> tuple[list[User], int]:
        filters = []

        if search:
            term = f"%{search.lower()}%"
            filters.append(
                or_(
                    User.email.ilike(term),
                    User.full_name.ilike(term),
                )
            )

        if is_active is not None:
            filters.append(User.is_active == is_active)

        # Count query
        count_q = select(func.count()).select_from(User)
        if filters:
            count_q = count_q.where(*filters)
        total = (await self.session.execute(count_q)).scalar_one()

        # Data query
        data_q = (
            select(User)
            .options(selectinload(User.roles))
            .order_by(User.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        if filters:
            data_q = data_q.where(*filters)

        rows = (await self.session.execute(data_q)).scalars().all()
        return list(rows), total
