from fastapi import APIRouter

from app.api.v1.endpoints import auth, roles, users, object_types, records

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Autenticación"])
api_router.include_router(users.router, prefix="/users", tags=["Usuarios"])
api_router.include_router(roles.router, prefix="/roles", tags=["Roles"])
api_router.include_router(
    object_types.router, prefix="/object-types", tags=["Objectos"]
)
api_router.include_router(records.router, prefix="/records", tags=["Registros"])
