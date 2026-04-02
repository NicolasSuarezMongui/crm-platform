import uuid
from datetime import datetime
from typing import Any
from pydantic import BaseModel, Field


class RecordCreate(BaseModel):
    name: str = Field(min_length=1, max_length=500)
    stage: str | None = None
    owner_id: uuid.UUID | None = None
    data: dict[str, Any] = Field(default_factory=dict)


class RecordUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=500)
    stage: str | None = None
    owner_id: uuid.UUID | None = None
    data: dict[str, Any] | None = None


class RecordResponse(BaseModel):
    id: uuid.UUID
    object_type_id: uuid.UUID
    name: str
    stage: str | None
    owner_id: uuid.UUID | None
    data: dict[str, Any]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
