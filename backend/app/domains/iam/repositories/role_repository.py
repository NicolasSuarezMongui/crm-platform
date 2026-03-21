from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.repository import BaseRepository
from app.domains.iam.models.role import Role
from app.domains.iam.models.user import user_roles


class RoleRepository(BaseRepository[Role]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Role, session)

    async def get_by_name(self, name: str) -> Role | None:
        result = await self.session.execute(
            select(Role).where(Role.name == name)
        )
        return result.scalar_one_or_none()

    async def get_with_user_count(self, role_id) -> tuple[Role, int] | None:
        role = await self.get_by_id(role_id)
        if not role:
            return None
        count_result = await self.session.execute(
            select(func.count())
            .select_from(user_roles)
            .where(user_roles.c.role_id == role_id)
        )
        count = count_result.scalar_one()
        return role, count

    async def get_user_count(self, role_id) -> int:
        result = await self.session.execute(
            select(func.count())
            .select_from(user_roles)
            .where(user_roles.c.role_id == role_id)
        )
        return result.scalar_one()

    async def list_all(self) -> list[Role]:
        result = await self.session.execute(
            select(Role).order_by(Role.name)
        )
        return list(result.scalars().all())
