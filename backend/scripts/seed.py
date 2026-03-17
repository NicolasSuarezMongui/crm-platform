import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import AsyncSessionLocal
from app.domains.iam.models.user import User
from app.domains.iam.models.role import Role
from app.core.security import hash_password


async def seed():
    async with AsyncSessionLocal() as session:
        async with session.begin():
            # ─── Roles ───────────────────────────────────────
            admin_role = Role(
                name="admin",
                description="Acceso total al sistema",
                is_system_role=True,
                permissions={
                    "users":        {"read": True, "write": True, "delete": True},
                    "contacts":     {"read": True, "write": True, "delete": True},
                    "accounts":     {"read": True, "write": True, "delete": True},
                    "deals":        {"read": True, "write": True, "delete": True},
                    "reports":      {"read": True, "write": True, "delete": True},
                    "settings":     {"read": True, "write": True, "delete": True},
                    "bulk_import":  {"execute": True},
                    "object_types": {"manage": True},
                },
            )

            sales_role = Role(
                name="sales",
                description="Vendedor — acceso a contactos y deals",
                is_system_role=True,
                permissions={
                    "users":        {"read": False, "write": False, "delete": False},
                    "contacts":     {"read": True,  "write": True,  "delete": False},
                    "accounts":     {"read": True,  "write": True,  "delete": False},
                    "deals":        {"read": True,  "write": True,  "delete": False},
                    "reports":      {"read": True,  "write": False, "delete": False},
                    "settings":     {"read": False, "write": False, "delete": False},
                    "bulk_import":  {"execute": False},
                    "object_types": {"manage": False},
                },
            )

            viewer_role = Role(
                name="viewer",
                description="Solo lectura",
                is_system_role=True,
                permissions={
                    "users":        {"read": False, "write": False, "delete": False},
                    "contacts":     {"read": True,  "write": False, "delete": False},
                    "accounts":     {"read": True,  "write": False, "delete": False},
                    "deals":        {"read": True,  "write": False, "delete": False},
                    "reports":      {"read": True,  "write": False, "delete": False},
                    "settings":     {"read": False, "write": False, "delete": False},
                    "bulk_import":  {"execute": False},
                    "object_types": {"manage": False},
                },
            )

            session.add_all([admin_role, sales_role, viewer_role])
            await session.flush()

            # ─── Users ───────────────────────────────────────
            superuser = User(
                email="admin@crm.local",
                full_name="Admin CRM",
                password_hash=hash_password("admin1234"),
                is_active=True,
                is_superuser=True,
                roles=[admin_role],
            )

            sales_user = User(
                email="sales@crm.local",
                full_name="Vendedor Demo",
                password_hash=hash_password("sales1234"),
                is_active=True,
                is_superuser=False,
                roles=[sales_role],
            )

            viewer_user = User(
                email="viewer@crm.local",
                full_name="Viewer Demo",
                password_hash=hash_password("viewer1234"),
                is_active=True,
                is_superuser=False,
                roles=[viewer_role],
            )

            session.add_all([superuser, sales_user, viewer_user])

        print("✓ Roles creados: admin, sales, viewer")
        print("✓ Usuarios creados:")
        print("    admin@crm.local   / admin1234  (superuser)")
        print("    sales@crm.local   / sales1234  (role: sales)")
        print("    viewer@crm.local  / viewer1234 (role: viewer)")


if __name__ == "__main__":
    asyncio.run(seed())
