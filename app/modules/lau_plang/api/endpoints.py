from fastapi import APIRouter

from app.modules.lau_finance.api import accounts

api_router = APIRouter(
    prefix="/finance",
    tags=["Finance Module"],
    responses={404: {"description": "Not found"}},
)
api_router.include_router(accounts.router, prefix="/accounts", tags=["accounts"])
