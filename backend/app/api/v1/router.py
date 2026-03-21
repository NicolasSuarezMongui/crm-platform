from fastapi import APIRouter

from app.api.v1.endpoints import auth, roles, users

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Autenticación"])
api_router.include_router(users.router, prefix="/users", tags=["Usuarios"])
api_router.include_router(roles.router, prefix="/roles", tags=["Roles"])
