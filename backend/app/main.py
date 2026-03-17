from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse, HTMLResponse
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html

from app.core.config import settings
from app.core.events import on_startup, on_shutdown
from app.api.v1.router import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await on_startup()
    yield
    await on_shutdown()

app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
    docs_url=None,
    redoc_url=None,
    openapi_url="/api/openapi.json" if settings.DEBUG else None,
    default_response_class=ORJSONResponse,
    lifespan=lifespan
)

# --- Middleware -------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Routers ----------------------------------------------------------
app.include_router(api_router, prefix="/api/v1")

if settings.DEBUG:
    @app.get("/api/docs", include_in_schema=False)
    async def custom_swagger_ui_html():
        return get_swagger_ui_html(
            openapi_url="/api/openapi.json",
            title=app.title + " - Swagger UI",
            oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
            swagger_js_url="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js",
            swagger_css_url="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css",
        )

if settings.DEBUG:
    @app.get("/api/redoc", include_in_schema=False)
    async def custom_redoc_ui_html():
        return get_redoc_html(
            openapi_url="/api/openapi.json",
            title=app.title + " - ReDoc",
            # Aquí forzamos la URL que sí funciona
            redoc_js_url="https://unpkg.com/redoc@2/bundles/redoc.standalone.js",
            with_google_fonts=True,
        )


@app.get("/health", tags=["system"])
async def health_check():
    return {"status": "ok", "app": settings.APP_NAME}
