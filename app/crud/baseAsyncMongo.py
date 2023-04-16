import json
from typing import Any, Generic, Optional, Sequence, Type, TypeVar

from fastapi.encoders import jsonable_encoder
from odmantic import AIOEngine, Model
from pydantic import BaseModel

ModelType = TypeVar("Model", bound=Model)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBaseAsync(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        """
        CRUD object with default methods to Create, Read, Update, Delete (CRUD).

        **Parameters**

        * `model`: A Odmantic model class
        * `schema`: A Pydantic model (schema) class
        """
        self.model = model

    async def get(self, asyncSectionMongo: AIOEngine, id: Any) -> Optional[ModelType]:
        return await asyncSectionMongo.find_one(self.model, self.model.id == id)

    async def get_multi(
        self, asyncSectionMongo: AIOEngine, *, skip: int = 0, limit: int = 100
    ) -> Sequence[ModelType]:
        async with asyncSectionMongo() as s:
            return await asyncSectionMongo.find(self.model, self.model.id == id,skip=skip,limit=limit)

    # async def create(self, asyncSectionMongo: AIOEngine, *, obj_in: CreateSchemaType) -> ModelType:
    #     obj_in_data = jsonable_encoder(obj_in)
    #     db_obj = self.model(**obj_in_data)
    #     async with asyncSectionMongo() as s:
    #         s.add(db_obj)
    #         await s.commit()
    #         await s.refresh(db_obj)
    #         return db_obj

    async def update(
        self,
        asyncSectionMongo: AIOEngine,
        *,
        db_obj: ModelType,
        obj_in: UpdateSchemaType | dict[str, Any],
    ) -> ModelType:

        obj_data = db_obj.dict()
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        for field in obj_data:
            if field == 'id':
                continue
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        return await asyncSectionMongo.save(db_obj)

    async def remove(self, asyncSectionMongo: AIOEngine, *, id: int) -> Optional[ModelType]:
        objFind=await asyncSectionMongo.find_one(self.model, self.model.id == id)
        await asyncSectionMongo.delete(objFind)
        return objFind


class CRUDBaseMultiAsync(CRUDBaseAsync[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        """
        CRUD object with default methods to Create, Read, Update, Delete (CRUD).

        **Parameters**

        * `model`: A SQLAlchemy model class
        * `schema`: A Pydantic model (schema) class
        """
        self.model = model

    async def create_with_owner(
        self, asyncSectionMongo: AIOEngine, *, obj_in: CreateSchemaType, owner_id: int
    ) -> ModelType:
        print('entrou crud',obj_in)
        obj_in_data = obj_in.dict()
        obj_in_data["owner_id"] = owner_id
        print('no crud',obj_in_data)

        print(self.model)
        db_obj = self.model(**obj_in_data)
        print(db_obj)
        await asyncSectionMongo.save(db_obj)
        return db_obj

    # async def get_multi_by_owner(
    #     self, asyncSectionMongo: AIOEngine, *, owner_id: int, skip: int = 0, limit: int = 100
    # ) -> Sequence[ModelType]:
    #     async with asyncSectionMongo() as s:
    #         query = await s.execute(
    #             select(self.model).where(getattr(self.model, "owner_id") == owner_id).offset(skip).limit(limit)
    #         )
    #         return query.scalars().all()  # pragma: no cover  errorinCover: true
