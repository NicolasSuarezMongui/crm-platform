"""
Field validator for Record.data JSONB.

Validates incoming data against the FieldDefinitions of an ObjectType.
Strict mode: rejects unknown fields AND missing required fields.
"""

import re
from datetime import datetime, date
from typing import Any

from fastapi import HTTPException, status

from app.domains.objects.models import FieldDefinition, FieldType


class FieldValidationError(Exception):
    def __init__(self, errors: dict[str, str]) -> None:
        self.errors = errors
        super().__init__(str(errors))


def validate_record_data(
    data: dict[str, Any],
    field_definitions: list[FieldDefinition],
    is_partial: bool = False,
) -> dict[str, Any]:
    """
    Validates and coerces record data against field definitions.

    Returns cleaned data dict on success.
    Raises HTTPException 422 with field-level errors on failure.
    """
    errors: dict[str, str] = {}
    cleaned: dict[str, Any] = {}

    defined_fields = {f.api_name: f for f in field_definitions}

    # --- Unknown fields check ---------------------------------
    for key in data:
        if key not in defined_fields:
            errors[key] = f"Unknown field '{key}'"

    if errors:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"message": "Validation failed", "errors": errors},
        )

    # --- Per-field validation ---------------------------------
    for api_name, field_def in defined_fields.items():
        value = data.get(api_name)

        # Required check (skip on partial update if field not present)
        if value is None or value == "":
            if field_def.is_required and not is_partial:
                errors[api_name] = f"Field '{field_def.label}' is required"
            else:
                cleaned[api_name] = None
            continue

        # Type coercion + validation
        coerced, error = _validate_field(value, field_def)
        if error:
            errors[api_name] = error
        else:
            cleaned[api_name] = coerced

    if errors:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"message": "Validation failed", "errors": errors},
        )
    return cleaned


def _validate_field(value: Any, field: FieldDefinition) -> tuple[Any, str | None]:
    """Returns (coerced_value, error_message). error_message is None on success."""

    ft = field.field_type

    match ft:
        case FieldType.TEXT | FieldType.LONG_TEXT:
            if not isinstance(value, str):
                return None, f"Expected text, got {type(value).__name__}"
            max_len = field.options.get("max_length")
            if max_len and len(value) > max_len:
                return None, f"Exceeds maximum length of {max_len}"
            pattern = field.options.get("pattern")
            if pattern and not re.fullmatch(pattern, value):
                return None, f"Value does not match required pattern"
            return value.strip(), None

        case FieldType.INTEGER:
            try:
                return int(value), None
            except (ValueError, TypeError):
                return None, "Expected an integer"

        case FieldType.DECIMAL:
            try:
                return float(value), None
            except (ValueError, TypeError):
                return None, "Expected a decimal number"

        case FieldType.BOOLEAN:
            if isinstance(value, bool):
                return value, None
            if isinstance(value, str) and value.lower() in ("true", "false"):
                return value.lower() == "true", None
            return None, "Expected true or false"

        case FieldType.DATE:
            if isinstance(value, date):
                return value.isoformat(), None
            try:
                date.fromisoformat(str(value))
                return str(value), None
            except ValueError:
                return None, "Expected date in YYYY-MM-DD format"

        case FieldType.DATETIME:
            if isinstance(value, datetime):
                return value.isoformat(), None
            try:
                datetime.fromisoformat(str(value))
                return str(value), None
            except ValueError:
                return None, "Expected datetime in ISO 8601 format"

        case FieldType.EMAIL:
            if not isinstance(value, str):
                return None, "Expected an email address"
            if not re.fullmatch(r"[^@]+@[^@]+\.[^@]+", value):
                return None, "Invalid email address"
            return value.lower().strip(), None

        case FieldType.PHONE:
            if not isinstance(value, str):
                return None, "Expected a phone number"
            cleaned = re.sub(r"[\s\-\(\)]", "", value)
            if not re.fullmatch(r"\+?\d{7,15}", cleaned):
                return None, "Invalid phone number"
            return value.strip(), None

        case FieldType.URL:
            if not isinstance(value, str):
                return None, "Expected a URL"
            if not re.fullmatch(r"https?://.+", value):
                return None, "Invalid URL — must start with http:// or https://"
            return value.strip(), None

        case FieldType.SELECT:
            options = [o["value"] for o in field.options.get("options", [])]
            if value not in options:
                return None, f"Invalid option. Allowed: {', '.join(options)}"
            return value, None

        case FieldType.MULTI_SELECT:
            if not isinstance(value, list):
                return None, "Expected a list of values"
            options = [o["value"] for o in field.options.get("options", [])]
            invalid = [v for v in value if v not in options]
            if invalid:
                return None, f"Invalid options: {', '.join(invalid)}"
            return value, None

        case FieldType.RELATION:
            # Just validate it's a UUID string — FK integrity checked at DB level
            import uuid
            try:
                uuid.UUID(str(value))
                return str(value), None
            except ValueError:
                return None, "Expected a valid UUID for relation field"

        case _:
            return value, None
