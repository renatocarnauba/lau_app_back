from typing import Any, Optional, Type

from fastapi.encoders import jsonable_encoder
from lau_utils.mongo import Mongo

from app.modules.lau_commons.core.security import get_password_hash, verify_password
from app.modules.lau_commons.crud.baseAsync import Base, CRUDBaseAsync
from app.modules.lau_commons.models.user import User, UserCreate, UserUpdate


class CRUDUser(CRUDBaseAsync[User, UserCreate, UserUpdate]):
    def __init__(self, model: Type[Base], *args, **kwargs):
        self.mongo = Mongo(asyncConn=True)
        self.model = model
        super().__init__(model, *args, **kwargs)

    @property
    async def coll(self):
        return await self.mongo.async_get_collection(self.model.__tablename__)

    async def get_by_email(self, email: str) -> Optional[User]:
        coll = await self.coll
        dictFounded = await coll.find_one({"email": email})
        if dictFounded:
            return self.model(**dictFounded)
        else:
            return None

    async def create(self, *, obj_in: UserCreate) -> User:
        tempObj = dict(obj_in)
        del tempObj["password"]
        db_obj = self.model(
            **dict(tempObj),
            hashed_password=get_password_hash(obj_in.password),
        )

        coll = await self.coll
        inserted = await coll.insert_one(jsonable_encoder(db_obj))
        coll = await self.coll
        dictFounded = await coll.find_one({"_id": inserted.inserted_id})
        if dictFounded:
            return self.model(**dictFounded)
        else:
            return None

    async def update(self, *, db_obj: User, obj_in: UserUpdate | dict[str, Any]) -> User:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        if update_data["password"]:
            hashed_password = get_password_hash(update_data["password"])
            del update_data["password"]
            update_data["hashed_password"] = hashed_password
        return await super().update(db_obj=db_obj, obj_in=update_data)

    async def authenticate(self, *, email: str, password: str) -> Optional[User]:
        user = await self.get_by_email(email=email)
        if not user:
            return None
        if not verify_password(password, str(user.hashed_password)):
            return None
        return user

    def is_active(self, user: User) -> bool:
        return bool(user.is_active)

    def is_superuser(self, user: User) -> bool:
        return bool(user.is_superuser)


user = CRUDUser(User)
