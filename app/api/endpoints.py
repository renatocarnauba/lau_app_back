from fastapi import APIRouter

from app.api import login, users

api_router = APIRouter(tags=["Default Apis"], responses={404: {"description": "Not found"}})
api_router.include_router(login.router, tags=["login"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
