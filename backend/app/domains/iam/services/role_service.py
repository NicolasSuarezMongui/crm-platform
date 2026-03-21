import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.iam.models.role import Role
from app.domains.iam.repositories.role_repository import RoleRepository
from app.schemas.role import RoleCreate, RoleUpdate


class RoleService:
    def __init__(self, session: AsyncSession) -> None:
        self.repo = RoleRepository(session)

    async def list_roles(self) -> list[Role]:
        return await self.repo.list_all()

    async def get_role(self, role_id: uuid.UUID) -> Role:
        role = await self.repo.get_by_id(role_id)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Role {role_id} not found",
            )
        return role

    async def get_role_detail(self, role_id: uuid.UUID) -> tuple[Role, int]:
        result = await self.repo.get_with_user_count(role_id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Role {role_id} not found",
            )
        return result

    async def create_role(self, data: RoleCreate) -> Role:
        existing = await self.repo.get_by_name(data.name)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Role '{data.name}' already exists",
            )
        return await self.repo.create(
            name=data.name,
            description=data.description,
            permissions=data.permissions,
            is_system_role=False,
        )

    async def update_role(self, role_id: uuid.UUID, data: RoleUpdate) -> Role:
        role = await self.get_role(role_id)

        if data.name and data.name != role.name:
            existing = await self.repo.get_by_name(data.name)
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Role '{data.name}' already exists",
                )

        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            return role

        return await self.repo.update(role_id, **update_data)

    async def delete_role(self, role_id: uuid.UUID) -> None:
        role = await self.get_role(role_id)

        if role.is_system_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="System roles cannot be deleted",
            )

        user_count = await self.repo.get_user_count(role_id)
        if user_count > 0:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Cannot delete role - {
                    user_count} user(s) still assigned. Reassing them first.",
            )

        await self.repo.delete(role_id)
