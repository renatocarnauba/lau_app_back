from typing import Any, Generic, Optional, Sequence, Type, TypeVar
from uuid import UUID
from lau_utils.mongo import Mongo

from pydantic import BaseModel

from fastapi.encoders import jsonable_encoder
Base = BaseModel
Base = TypeVar("Base", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBaseAsync(Generic[Base, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[Base]):
        """
        CRUD object with default methods to Create, Read, Update, Delete (CRUD).

        **Parameters**

        * `model`: A Pydantic to PyMongo model class
        * `schema`: A Pydantic model (schema) class
        """
        self.mongo = Mongo(asyncConn=True)
        self.model = model

    @property
    async def coll(self):
        return await self.mongo.async_get_collection(self.model.__tablename__)

    async def get(self, id: Any) -> Optional[Base]:
        if isinstance(id, UUID):
            id = str(id)
        coll = await self.coll
        dictFounded = await coll.find_one({"id": id})
        if dictFounded:
            return self.model(**dictFounded)
        else:
            return None

    async def get_multi(self, *, skip: int = 0, limit: int = 100) -> Sequence[Base]:
        mongo=Mongo(asyncConn=True)
        coll = await mongo.async_get_collection(self.model.__tablename__)
        cursor = coll.find({}, limit=limit, skip=skip)
        listData = await cursor.to_list(length=100)
        tbObj=[self.model(**data)for data in listData]
        return tbObj

    async def create(self, *, obj_in: CreateSchemaType):
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)
        coll = await self.coll
        inserted = await coll.insert_one(jsonable_encoder(db_obj))
        dictFounded = await coll.find_one({"_id": inserted.inserted_id})
        if dictFounded:
            return self.model(**dictFounded)
        else:
            return None

    async def update(
        self,
        *,
        db_obj: Base,
        obj_in: UpdateSchemaType | dict[str, Any],
    ) -> Base:
        obj_data = db_obj.dict()
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)

        coll = await self.coll
        update_data=jsonable_encoder(update_data)
        
        await coll.update_one({"id": str(obj_data["id"])}, {"$set": update_data})
        return await self.get(obj_data["id"])

    async def remove(self, *, id: str) -> Optional[Base]:
        if isinstance(id, UUID):
            id = str(id)
        objFind = await self.get(id)
        coll = await self.coll
        filterDel = {"id": id}
        await coll.delete_one(filterDel)
        return objFind


class CRUDBaseMultiAsync(CRUDBaseAsync[Base, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[Base]):
        """
        CRUD object with default methods to Create, Read, Update, Delete (CRUD).

        **Parameters**

        * `model`: A SQLAlchemy model class
        * `schema`: A Pydantic model (schema) class
        """
        self.mongo = Mongo(asyncConn=True)
        self.model = model

    @property
    async def coll(self):
        return await self.mongo.async_get_collection(self.model.__tablename__)

    async def create_with_owner(self, *, obj_in: CreateSchemaType, owner_id: str) -> Base:
        obj_in_data = jsonable_encoder(obj_in)

        if isinstance(owner_id, UUID):
            owner_id = str(owner_id)

        obj_in_data["owner_id"] = owner_id

        db_obj = self.model(**obj_in_data)
        coll = await self.coll
        inserted = await coll.insert_one(jsonable_encoder(db_obj))
        dictFounded = await coll.find_one({"_id": inserted.inserted_id})
        if dictFounded:
            return self.model(**dictFounded)
        else:
            return None


    async def get_multi_by_owner(self, *, owner_id: str, skip: int = 0, limit: int = 100):
        if isinstance(owner_id, UUID):
            owner_id = str(owner_id)
        coll = await self.coll
        cursor = coll.find({"owner_id": owner_id}, limit=limit, skip=skip)
        listData = await cursor.to_list(length=100)
        tbObj=[self.model(**data)for data in listData]
        return tbObj
