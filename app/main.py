from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.config.integration.endpoints import api_router as modules_api_router
from app.config.settings import settings
from app.modules.lau_commons.api.endpoints import api_router as core_api_router

app = FastAPI(title=settings.PROJECT_NAME, openapi_url=f"{settings.API_V1_STR}/openapi.json")

# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(core_api_router, prefix=settings.API_V1_STR)
app.include_router(modules_api_router)
