import uuid
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, field_validator

# --- Request schemas ------------------------------------------


class UserCreate(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=1, max_length=255)
    password: str = Field(min_length=8)
    is_superuser: bool = False
    role_ids: list[uuid.UUID] = Field(default_factory=list)

    @field_validator("full_name")
    @classmethod
    def strip_name(cls, v: str) -> str:
        return v.strip()


class UserUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=1, max_length=255)
    avatar_url: str | None = None
    extra_data: dict | None = None

    @field_validator("full_name")
    @classmethod
    def strip_name(cls, v: str | None) -> str | None:
        return v.strip() if v else v


class UserUpdatePassword(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8)


class AssignRolesRequest(BaseModel):
    role_ids: list[uuid.UUID]


# --- Response schemas --------------------------------------

class RoleBasic(BaseModel):
    id: uuid.UUID
    name: str
    permissions: dict

    model_config = {"from_attributes": True}


class UserResponse(BaseModel):
    id: uuid.UUID
    email: str
    full_name: str
    is_active: bool
    is_superuser: bool
    avatar_url: str | None
    extra_data: dict
    roles: list[RoleBasic]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class UserSummary(BaseModel):
    """Lightweight user for lists - no roles detail."""
    id: uuid.UUID
    email: str
    full_name: str
    is_active: bool
    is_superuser: bool
    avatar_url: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
