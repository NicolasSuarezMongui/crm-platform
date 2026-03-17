import enum
import uuid

from sqlalchemy import Enum as SAEnum, ForeignKey, String, Boolean, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_model import BaseModel


class AuditAction(str, enum.Enum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    LOGIN = "login"
    LOGOUT = "logout"
    EXPORT = "export"
    IMPORT = "import"
    PERMISSION_CHANGE = "permission_change"


class AuditLog(BaseModel):
    """
    Immutable audit trail. Never update or delete rows from this table.
    Useful for compliance, debugging, and undo functionality.
    """
    __tablename__ = "audit_logs"

    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    action: Mapped[AuditAction] = mapped_column(
        SAEnum(AuditAction), nullable=False, index=True)
    resource_type: Mapped[str] = mapped_column(
        String(100), nullable=False, index=True)
    resource_id: Mapped[str | None] = mapped_column(
        String(100), nullable=True, index=True)
    ip_address: Mapped[str | None] = mapped_column(String(50), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Snapshot of before/after for UPDATE actions
    old_data: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    new_data: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    context: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)


class NotificationType(str, enum.Enum):
    RECORD_ASSIGNED = "record_assigned"
    RECORD_UPDATED = "record_updated"
    MENTION = "mention"
    BULK_IMPORT_DONE = "bulk_import_done"
    BULK_IMPORT_FAILED = "bulk_import_failed"
    SYSTEM = "sytem"


class Notification(BaseModel):
    __tablename__ = "notifications"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    type: Mapped[NotificationType] = mapped_column(
        SAEnum(NotificationType), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=True)
    is_read: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False, index=True)
    read_at: Mapped[str | None] = mapped_column(nullable=True)

    # Flexible payload (link to record, job id, etc.)
    payload: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)


class BulkJobStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    DONE = "done"
    FAILED = "failed"
    PARTIAL = "partial"


class BulkJob(BaseModel):
    __tablename__ = "bulk_jobs"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    object_type_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("object_types.id", ondelete="CASCADE"),
        nullable=False,
    )
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    total_rows: Mapped[int] = mapped_column(default=0, nullable=False)
    processed_rows: Mapped[int] = mapped_column(default=0, nullable=False)
    success_rows: Mapped[int] = mapped_column(default=0, nullable=False)
    error_rows: Mapped[int] = mapped_column(default=0, nullable=False)

    # Array of {"row": 5, "field": "email", "error": "Invalid format"}
    errors: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
    celery_task_id: Mapped[str | None] = mapped_column(
        String(255), nullable=True)
