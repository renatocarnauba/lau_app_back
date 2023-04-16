from fastapi import APIRouter

from app.config.settings import settings
from app.modules.lau_finance.api.endpoints import api_router as finance_api_router

"""
    Incluir módulos para Integração abaixo
"""
api_router = APIRouter()
api_router.include_router(finance_api_router, prefix=settings.API_V1_STR)
