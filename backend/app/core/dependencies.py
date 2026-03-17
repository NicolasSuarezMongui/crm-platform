"""
FastAPI dependency injection for auth and permissions.

Usage in routes:
    @router.get("/contacts")
    async def list_contacts(
        current_user: CurrentUser,
        _:RequirePermission("contacts", "read"),
    ):
        ...
"""

import uuid
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_token
from app.db.session import get_db
from app.domains.iam.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)]
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )
    try:
        payload = decode_token(token)
        if payload.get("type") != "access":
            raise credentials_exception
        user_id: str = payload.get("sub")
        if not user_id:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    from sqlalchemy import select
    result = await db.execute(
        select(User).where(User.id == uuid.UUID(
            user_id), User.is_active == True)
    )
    user = result.scalar_one_or_none()
    if not user:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

# --- Typed shorthand ----------------------------------------
CurrentUser = Annotated[User, Depends(get_current_active_user)]

# --- Permission dependency factory --------------------------


def RequirePermission(resource: str, action: str):
    """
    Dependency factory. Checks if any of the user's roles grant this permission.

    Usage:
        @router.delete("/{id}" dependencies=[Depends(RequirePermission("contacts", "delete"))])
    """
    async def check(current_user: CurrentUser) -> User:
        if current_user.is_superuser:
            return current_user

        has_perm = any(
            role.has_permission(resource, action)
            for role in current_user.roles
        )
        if not has_perm:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing permission: {resource}:{action}",
            )
        return current_user

    return Depends(check)
