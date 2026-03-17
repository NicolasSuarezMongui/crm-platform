"""
Object engine - the heart of the CRM's flexibility.

ObjectType defines a "thing" in the CRM (Contact, Account, Deal, or any custom type).
FieldDefinition defines the schema of each custom field.
Record stores actual data for any object type.

This enables Salesforce-style custom objects without runtime DDL changes.
"""

import enum
import uuid

from sqlalchemy import Enum as SAEnum, ForeignKey, String, Boolean, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_model import BaseModel


class FieldType(str, enum.Enum):
    TEXT = "text",
    LONG_TEXT = "long_text"
    INTEGER = "integer"
    DECIMAL = "decimal"
    BOOLEAN = "boolean"
    DATE = "date"
    DATETIME = "datetime"
    EMAIL = "email"
    PHONE = "phone"
    URL = "url"
    SELECT = "select"          # single choice
    MULTI_SELECT = "multi_select"
    RELATION = "relation"      # FK to another record


class ObjectType(BaseModel):
    """
    Defines a type of CRM object (built-in or user-created).
    e.g: Contact, Account, Deal, or custom 'Project' type.
    """
    __tablename__ = "object_types"

    api_name: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False, index=True)
    label: Mapped[str] = mapped_column(String(100), nullable=False)
    label_plural: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=True)
    icon: Mapped[str | None] = mapped_column(String(50), nullable=False)
    color: Mapped[str | None] = mapped_column(String(20), nullable=False)
    is_system: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False)

    # Storages page layout config: which fields appear, in what order, in what sections
    # {"sections": [{"name": "Basic Info", "fields": ["name", "email"], "columns": 2}]}
    layout_config: Mapped[dict] = mapped_column(
        JSONB, default=dict, nullable=False)

    # Relationships
    field_definitions: Mapped[list["FieldDefinition"]] = relationship(
        back_populates="object_type",
        lazy="selectin",
        cascade="all, delete-orphan",
    )
    records: Mapped[list["Record"]] = relationship(
        back_populates="object_type",
        lazy="noload",
    )


class FieldDefinition(BaseModel):
    """
    Defines a field (column) for an ObjectType.
    """
    __tablename__ = "field_definitions"

    object_type_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("object_types.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    api_name: Mapped[str] = mapped_column(String(100), nullable=False)
    label: Mapped[str] = mapped_column(String(100), nullable=False)
    field_type: Mapped[FieldType] = mapped_column(
        SAEnum(FieldType), nullable=False)
    is_required: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False)
    is_system: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False)
    is_searchable: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False)
    sort_order: Mapped[int] = mapped_column(default=0, nullable=False)

    # Validation and display config
    # For SELECT: {"options": [{"value": "lead", "label": "Lead", "color": "#3B82F6"}]}
    # For RELATION: {"target_object_type": "contact", "display_field": "name"}
    # For TEXT: {"max_length": 255, "pattern": "^[A-Z].*"}
    options: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)

    object_type: Mapped["ObjectType"] = relationship(
        back_populates="field_definitions")


class Record(BaseModel):
    """
    A single instance of any ObjectType.
    All field values live in the JSONB 'data' column.
    Core searchable fields (name, owner) are promoted to real columns.
    """
    __tablename__ = "records"

    object_type_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("object_types.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    owner_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Promoted for fast querying without JSONB parsing
    name: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    stage: Mapped[str | None] = mapped_column(
        String(100), nullable=True, index=True)

    # All custom field values live here
    # {"email": "jhon@example.com", "phone": "+1234567890", "custom_field_x": "value"}
    data: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)

    object_type: Mapped["ObjectType"] = relationship(back_populates="records")
