from typing import Any, Optional

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio.session import async_sessionmaker
from sqlalchemy.future import select

from app.core.security import get_password_hash, verify_password
from app.crud.baseAsync import CRUDBaseAsync
from app.models.sql.user import User
from app.schemas.user import UserCreate, UserUpdate


class CRUDUser(CRUDBaseAsync[User, UserCreate, UserUpdate]):
    async def get_by_email(self, asyncSection: async_sessionmaker[AsyncSession], *, email: str) -> Optional[User]:
        async with asyncSection() as s:
            query = await s.execute(select(User).where(User.email == email))
            result = query.scalars().first()
            return result

    async def create(self, asyncSection: async_sessionmaker[AsyncSession], *, obj_in: UserCreate) -> User:
        tempObj = dict(obj_in)
        del tempObj["password"]
        db_obj = User(
            **dict(tempObj),
            hashed_password=get_password_hash(obj_in.password),
        )
        async with asyncSection() as s:
            s.add(db_obj)
            await s.commit()
            await s.refresh(db_obj)
            return db_obj

    async def update(
        self, asyncSection: async_sessionmaker[AsyncSession], *, db_obj: User, obj_in: UserUpdate | dict[str, Any]
    ) -> User:
        if isinstance(obj_in, dict):
            update_data = obj_in  # pragma: no cover
        else:
            update_data = obj_in.dict(exclude_unset=True)
        if update_data["password"]:
            hashed_password = get_password_hash(update_data["password"])
            del update_data["password"]
            update_data["hashed_password"] = hashed_password
        return await super().update(asyncSection, db_obj=db_obj, obj_in=update_data)

    async def authenticate(
        self, asyncSection: async_sessionmaker[AsyncSession], *, email: str, password: str
    ) -> Optional[User]:
        user = await self.get_by_email(asyncSection, email=email)
        if not user:
            return None
        if not verify_password(password, str(user.hashed_password)):
            return None  # pragma: no cover
        return user

    async def remove_test(self, asyncSection: async_sessionmaker[AsyncSession]) -> None:  # pragma: no cover
        async with asyncSection() as s:
            await s.execute(delete(self.model).where(self.model.is_test == True))  # noqa: E712
            await s.commit()
            return None

    def is_active(self, user: User) -> bool:
        return bool(user.is_active)

    def is_superuser(self, user: User) -> bool:
        return bool(user.is_superuser)


user = CRUDUser(User)
