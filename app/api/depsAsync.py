from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from jose.exceptions import JWTError
from pydantic import ValidationError

from app.config.integration import crud, models, schemas
from app.config.settings import settings
from app.modules.lau_commons.core import security
from app.modules.lau_commons.core.exceptions import (
    InvalidCredential,
    UserInactive,
    UserNotFound,
    UserWithoutPrivileges,
)

reusable_oauth2 = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/login/access-token")


async def get_current_user(
    token: str = Depends(reusable_oauth2),
) -> models.User:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[security.ALGORITHM])
        token_data = schemas.TokenPayload(**payload)
    except (JWTError, ValidationError):
        raise InvalidCredential()
    user = await crud.user.get(id=token_data.sub)
    if not user:
        raise UserNotFound()
    return user


def get_current_active_user(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    if not crud.user.is_active(current_user):
        raise UserInactive()
    return current_user


def get_current_active_superuser(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    if not crud.user.is_superuser(current_user):
        raise UserWithoutPrivileges()
    return current_user
