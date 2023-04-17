import asyncio
from typing import Any, Generic, Optional, Sequence, Type, TypeVar
from uuid import UUID
from lau_utils.mongo import Mongo

from pydantic import BaseModel

from fastapi.encoders import jsonable_encoder
ModelMongoType = TypeVar("BaseModel", bound=BaseModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBaseAsync(Generic[ModelMongoType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelMongoType]):
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

    async def get(self,  id: Any) -> Optional[ModelMongoType]:
        if  isinstance(id,UUID):
            id = str(id)
        coll=await self.coll
        dictFounded = await coll.find_one({"id": id})
        if dictFounded:
            return self.model(**dictFounded)
        else:
            return None

    async def get_multi(
        self,  *, skip: int = 0, limit: int = 100
    ) -> Sequence[ModelMongoType]:
        coll=await self.coll
        return await coll.find({},limit=limit,skip=skip)

    async def create(self,  *, obj_in: CreateSchemaType):
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)
        coll=await self.coll
        inserted = await coll.insert_one(jsonable_encoder(db_obj))
        coll=await self.coll
        dictFounded = await coll.find_one({"_id": inserted.inserted_id})
        if dictFounded:
            return self.model(**dictFounded)
        else:
            return None

    async def update(
        self,
        *,
        db_obj: ModelMongoType,
        obj_in: UpdateSchemaType | dict[str, Any],
    ) -> ModelMongoType:

        obj_data = db_obj.dict()
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)

        coll=await self.coll
        await coll.update_one({"id": str(obj_data['id'])}, {'$set':update_data})
        return await self.get(obj_data['id'])

    async def remove(self,  *, id: int) -> Optional[ModelMongoType]:
        if  isinstance(id,UUID):
            id = str(id)        
        objFind=await self.get(id)
        coll=await self.coll
        coll.delete_one({'id',id})
        return objFind


class CRUDBaseMultiAsync(CRUDBaseAsync[ModelMongoType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelMongoType]):
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

    async def create_with_owner(
        self,  *, obj_in: CreateSchemaType, owner_id: int
    ) -> ModelMongoType:
        obj_in_data = obj_in.dict()
        
        if  isinstance(owner_id,UUID):
            owner_id = str(owner_id)         
                   
        obj_in_data["owner_id"] = owner_id

        db_obj = self.model(**obj_in_data)
        coll=await self.coll
        inserted = await coll.insert_one(jsonable_encoder(db_obj))
        dictFounded = await coll.find_one({"_id": inserted.inserted_id})
        if dictFounded:
            return self.model(**dictFounded)
        else:
            return None

async def get_multi_by_owner(
    self,  *, owner_id: int, skip: int = 0, limit: int = 100
):
    if  isinstance(owner_id,UUID):
        owner_id = str(owner_id)
    coll=await self.coll
    return await coll.find({"owner_id":owner_id},limit=limit,skip=skip)

