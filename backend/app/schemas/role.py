import uuid
from datetime import datetime
from pydantic import BaseModel, Field

# --- Request schemas --------------------------------------------------------


class RoleCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    description: str | None = Field(default=None, max_length=500)
    permissions: dict = Field(default_factory=dict)


class RoleUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=100)
    description: str | None = None
    permissions: dict | None = None

# --- Response schemas ------------------------------------------------------


class RoleResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: str | None
    is_system_role: bool
    permissions: dict
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class RoleWithUsersResponse(RoleResponse):
    """Role detail including assigned user count."""
    user_count: int = 0
