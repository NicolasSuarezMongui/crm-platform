from typing import TYPE_CHECKING

from sqlalchemy import Boolean, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_model import BaseModel

if TYPE_CHECKING:
    from app.domains.iam.models.user import User


class Role(BaseModel):
    """
    Role with granular permissions stored in JSONB.

    permissions structure:
    {
        "contacts":     {"read": true,  "write": true,  "delete": false},
        "accounts":     {"read": true,  "write": false, "delete": false},
        "deals":        {"read": true,  "write": true,  "delete": true},
        "reports":      {"read": true,  "write": false, "delete": false},
        "settings":     {"read": false, "write": false, "delete": false},
        "bulk_import":  {"execute": true},
        "object_types": {"manage": false}
    }
    """

    __tablename__ = "roles"

    name: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_system_role: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False)
    permissions: Mapped[dict] = mapped_column(
        JSONB, default=dict, nullable=False)

    # Relationship
    users: Mapped[list["User"]] = relationship(
        secondary="user_roles",
        back_populates="roles",
        lazy="noload",
    )

    def has_permission(self, resource: str, action: str) -> bool:
        """Check if this role allows action on resource."""
        return self.permissions.get(resource, {}).get(action, False)
