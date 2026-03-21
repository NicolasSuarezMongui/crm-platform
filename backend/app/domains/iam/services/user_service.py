import uuid

from fastapi import HTTPException, status
from pydantic import AmqpDsn
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password, verify_password
from app.domains.iam.models.user import User
from app.domains.iam.repositories.user_repository import UserRepository
from app.domains.iam.repositories.role_repository import RoleRepository
from app.schemas.user import UserCreate, UserUpdate, UserUpdatePassword, AssignRolesRequest


class UserService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = UserRepository(session)
        self.role_repo = RoleRepository(session)

    async def list_users(
        self,
        skip: int = 0,
        limit: int = 20,
        search: str | None = None,
        is_active: bool | None = None,
    ) -> tuple[list[User], int]:
        return await self.repo.list_paginated(
            skip=skip,
            limit=limit,
            search=search,
            is_active=is_active
        )

    async def get_user(self, user_id: uuid.UUID):
        user = await self.repo.get_with_roles(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User {user_id} not found.",
            )
        return user

    async def create_user(self, data: UserCreate) -> User:
        existing = await self.repo.get_by_email(data.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered",
            )

        # Validate role_ids exist
        roles = []
        for role_id in data.role_ids:
            role = await self.role_repo.get_by_id(role_id)
            if not role:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Role {role_id} not found",
                )
            roles.append(role)

        user = User(
            email=data.email.lower(),
            full_name=data.full_name,
            password_hash=hash_password(data.password),
            is_superuser=data.is_superuser,
            roles=roles,
        )
        self.session.add(user)
        await self.session.flush()
        await self.session.refresh(user)
        return user

    async def update_user(self, user_id: uuid.UUID, data: UserUpdate) -> User:
        await self.get_user(user_id)  # Validates existence
        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            return await self.get_user(user_id)
        return await self.repo.update(user_id, **update_data)

    async def change_password(
        self, user_id: uuid.UUID, data: UserUpdatePassword, requester: User
    ) -> None:
        user = await self.get_user(user_id)

        # Only superusers can change other users's passwords without current_password check
        if requester.id != user_id and not requester.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot change another user's password",
            )

        if requester.id == user_id:
            if not verify_password(data.current_password, user.password_hash):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Current password is incorrect",
                )

        await self.repo.update(user_id, password_hash=hash_password(data.new_password))

    async def deactivate_user(self, user_id: uuid.UUID, requester: User) -> User:
        user = await self.get_user(user_id)

        if user.id == requester.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You cannot deactivate your own account.",
            )

        return await self.repo.update(user_id, is_active=False)

    async def reactivate_user(self, user_id: uuid.UUID) -> User:
        await self.get_user(user_id)
        return await self.repo.update(user_id, is_active=True)

    async def assign_roles(
        self, user_id: uuid.UUID, data: AssignRolesRequest
    ) -> User:
        user = await self.get_user(user_id)

        roles = []
        for role_id in data.role_ids:
            role = await self.role_repo.get_by_id(role_id)
            if not role:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Role {role_id} not found",
                )
            roles.append(role)

        user.roles = roles
        await self.session.flush()
        await self.session.refresh(user)
        return user
