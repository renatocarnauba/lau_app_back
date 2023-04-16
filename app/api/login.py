from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio.session import async_sessionmaker

from app import schemas
from app.api import depsAsync
from app.config.integration import crud, models
from app.config.settings import settings
from app.core import security
from app.core.exceptions import LoginFail, UserInactive

router = APIRouter()


@router.post("/login/access-token", response_model=schemas.Token)
async def login_access_token(
    asyncSection: async_sessionmaker[AsyncSession] = Depends(depsAsync.get_asyncSection),
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = await crud.user.authenticate(asyncSection, email=form_data.username, password=form_data.password)
    if not user:
        raise LoginFail()
    elif not crud.user.is_active(user):
        raise UserInactive()
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": security.create_access_token(user.id, expires_delta=access_token_expires),
        "token_type": "bearer",
    }


@router.post("/login/test-token", response_model=schemas.User)
async def test_token(
    current_user: models.User = Depends(depsAsync.get_current_user),
) -> Any:
    """
    Test access token
    """
    return current_user
