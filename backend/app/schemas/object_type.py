import uuid
from datetime import datetime
from pydantic import BaseModel, Field
from app.domains.objects.models import FieldType

# --- FieldDefinition schemas ------------------------------------


class FieldDefinitionCreate(BaseModel):
    api_name: str = Field(min_length=1, max_length=100,
                          pattern=r"^[a-z][a-z0-9_]*$")
    label: str = Field(min_length=1, max_length=100)
    field_type: FieldType
    is_required: bool = False
    is_searchable: bool = True
    sort_order: int = 0
    options: dict = Field(default_factory=dict)


class FieldDefinitionResponse(BaseModel):
    id: uuid.UUID
    api_name: str
    label: str
    field_type: FieldType
    is_required: bool
    is_system: bool
    is_searchable: bool
    sort_order: int
    options: dict

    model_config = {"from_attributes": True}

# --- ObjectType schemas -----------------------------------------


class ObjectTypeCreate(BaseModel):
    api_name: str = Field(min_length=1, max_length=100,
                          pattern=r"^[a-z][a-z0-9_]*$")
    label: str = Field(min_length=1, max_length=100)
    label_plural: str = Field(min_length=1, max_length=100)
    description: str | None = None
    icon: str | None = None
    color: str | None = None
    fields: list[FieldDefinitionCreate] = Field(default_factory=list)


class ObjectTypeUpdate(BaseModel):
    label: str | None = None
    label_plural: str | None = None
    description: str | None = None
    icon: str | None = None
    color: str | None = None
    layout_config: dict | None = None


class ObjectTypeResponse(BaseModel):
    id: uuid.UUID
    api_name: str
    label: str
    label_plural: str
    description: str | None
    icon: str | None
    color: str | None
    is_system: bool
    layout_config: dict
    field_definitions: list[FieldDefinitionResponse]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ObjectTypeSummary(BaseModel):
    id: uuid.UUID
    api_name: str
    label: str
    label_plural: str
    icon: str | None
    color: str | None
    is_system: bool

    model_config = {"from_attributes": True}
