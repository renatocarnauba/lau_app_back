from fastapi import APIRouter

from app.modules.lau_finance.api import accounts, categories, institutions, transactions

api_router = APIRouter(
    prefix="/finance",
    tags=["Finance Module"],
    responses={404: {"description": "Not found"}},
)
api_router.include_router(accounts.router, prefix="/accounts", tags=["accounts"])
api_router.include_router(categories.router, prefix="/categories", tags=["categories"])
api_router.include_router(institutions.router, prefix="/institutions", tags=["institutions"])
api_router.include_router(transactions.router, prefix="/transactions", tags=["transactions"])
