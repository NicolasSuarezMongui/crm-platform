"""
Phase 3 seed — creates the three core CRM object types with their fields.
Run after the phase 3 migration:
    python -m scripts.seed_objects
"""

import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import AsyncSessionLocal
from app.domains.objects.models import ObjectType, FieldDefinition, FieldType


OBJECT_TYPES = [
    {
        "api_name": "contact",
        "label": "Contacto",
        "label_plural": "Contactos",
        "description": "Personas individuales relacionadas con el negocio",
        "icon": "user",
        "color": "#6366f1",
        "fields": [
            {
                "api_name": "email",
                "label": "Email",
                "field_type": FieldType.EMAIL,
                "is_required": True,
                "sort_order": 0,
            },
            {
                "api_name": "phone",
                "label": "Teléfono",
                "field_type": FieldType.PHONE,
                "is_required": False,
                "sort_order": 1,
            },
            {
                "api_name": "company",
                "label": "Empresa",
                "field_type": FieldType.TEXT,
                "is_required": False,
                "sort_order": 2,
            },
            {
                "api_name": "position",
                "label": "Cargo",
                "field_type": FieldType.TEXT,
                "is_required": False,
                "sort_order": 3,
            },
            {
                "api_name": "notes",
                "label": "Notas",
                "field_type": FieldType.LONG_TEXT,
                "is_required": False,
                "sort_order": 4,
            },
            {
                "api_name": "status",
                "label": "Estado",
                "field_type": FieldType.SELECT,
                "is_required": False,
                "sort_order": 5,
                "options": {
                    "options": [
                        {"value": "lead", "label": "Lead", "color": "#6366f1"},
                        {"value": "prospect", "label": "Prospecto", "color": "#f59e0b"},
                        {"value": "customer", "label": "Cliente", "color": "#10b981"},
                        {"value": "inactive", "label": "Inactivo", "color": "#6b7280"},
                    ]
                },
            },
        ],
    },
    {
        "api_name": "account",
        "label": "Cuenta",
        "label_plural": "Cuentas",
        "description": "Empresas u organizaciones",
        "icon": "building",
        "color": "#0ea5e9",
        "fields": [
            {
                "api_name": "website",
                "label": "Sitio web",
                "field_type": FieldType.URL,
                "is_required": False,
                "sort_order": 0,
            },
            {
                "api_name": "phone",
                "label": "Teléfono",
                "field_type": FieldType.PHONE,
                "is_required": False,
                "sort_order": 1,
            },
            {
                "api_name": "industry",
                "label": "Industria",
                "field_type": FieldType.TEXT,
                "is_required": False,
                "sort_order": 2,
            },
            {
                "api_name": "employees",
                "label": "Empleados",
                "field_type": FieldType.INTEGER,
                "is_required": False,
                "sort_order": 3,
            },
            {
                "api_name": "revenue",
                "label": "Ingresos",
                "field_type": FieldType.DECIMAL,
                "is_required": False,
                "sort_order": 4,
            },
            {
                "api_name": "notes",
                "label": "Notas",
                "field_type": FieldType.LONG_TEXT,
                "is_required": False,
                "sort_order": 5,
            },
            {
                "api_name": "type",
                "label": "Tipo",
                "field_type": FieldType.SELECT,
                "is_required": False,
                "sort_order": 6,
                "options": {
                    "options": [
                        {"value": "customer", "label": "Cliente"},
                        {"value": "partner", "label": "Partner"},
                        {"value": "prospect", "label": "Prospecto"},
                        {"value": "vendor", "label": "Proveedor"},
                    ]
                },
            },
        ],
    },
    {
        "api_name": "deal",
        "label": "Oportunidad",
        "label_plural": "Oportunidades",
        "description": "Oportunidades de negocio en proceso de venta",
        "icon": "trending-up",
        "color": "#10b981",
        "fields": [
            {
                "api_name": "amount",
                "label": "Monto",
                "field_type": FieldType.DECIMAL,
                "is_required": False,
                "sort_order": 0,
            },
            {
                "api_name": "close_date",
                "label": "Fecha cierre",
                "field_type": FieldType.DATE,
                "is_required": False,
                "sort_order": 1,
            },
            {
                "api_name": "probability",
                "label": "Probabilidad %",
                "field_type": FieldType.INTEGER,
                "is_required": False,
                "sort_order": 2,
            },
            {
                "api_name": "description",
                "label": "Descripción",
                "field_type": FieldType.LONG_TEXT,
                "is_required": False,
                "sort_order": 3,
            },
            {
                "api_name": "account_id",
                "label": "Cuenta",
                "field_type": FieldType.RELATION,
                "is_required": False,
                "sort_order": 4,
                "options": {"target_object_type": "account"},
            },
            {
                "api_name": "contact_id",
                "label": "Contacto",
                "field_type": FieldType.RELATION,
                "is_required": False,
                "sort_order": 5,
                "options": {"target_object_type": "contact"},
            },
            {
                "api_name": "stage",
                "label": "Etapa",
                "field_type": FieldType.SELECT,
                "is_required": True,
                "sort_order": 6,
                "options": {
                    "options": [
                        {"value": "prospecting", "label": "Prospección"},
                        {"value": "proposal", "label": "Propuesta"},
                        {"value": "negotiation", "label": "Negociación"},
                        {"value": "closed_won", "label": "Ganado"},
                        {"value": "closed_lost", "label": "Perdido"},
                    ]
                },
            },
        ],
    },
]


async def seed_objects():
    async with AsyncSessionLocal() as session:
        async with session.begin():
            for obj_def in OBJECT_TYPES:
                # Skip if already exists
                from sqlalchemy import select

                existing = (
                    await session.execute(
                        select(ObjectType).where(
                            ObjectType.api_name == obj_def["api_name"]
                        )
                    )
                ).scalar_one_or_none()

                if existing:
                    print(f"  → Skipping '{obj_def['api_name']}' (already exists)")
                    continue

                fields = obj_def.pop("fields")
                obj_type = ObjectType(**obj_def, is_system=True)
                session.add(obj_type)
                await session.flush()

                for field_def in fields:
                    options = field_def.pop("options", {})
                    field = FieldDefinition(
                        object_type_id=obj_type.id,
                        is_system=True,
                        options=options,
                        **field_def,
                    )
                    session.add(field)

                print(f"  ✓ Created '{obj_def['api_name']}' with {len(fields)} fields")

        print("\n✓ Object types seeded successfully")


if __name__ == "__main__":
    asyncio.run(seed_objects())
