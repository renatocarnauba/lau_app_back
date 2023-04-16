from typing import Any, Generic, Optional, Sequence, Type, TypeVar

from fastapi.encoders import jsonable_encoder
from lau_commons.sqlalchemy_base_class import ModelTemplate
from pydantic import BaseModel
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio.session import async_sessionmaker
from sqlalchemy.future import select

ModelType = TypeVar("ModelType", bound=ModelTemplate)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBaseAsync(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        """
        CRUD object with default methods to Create, Read, Update, Delete (CRUD).

        **Parameters**

        * `model`: A SQLAlchemy model class
        * `schema`: A Pydantic model (schema) class
        """
        self.model = model

    async def get(self, asyncSection: async_sessionmaker[AsyncSession], id: Any) -> Optional[ModelType]:
        async with asyncSection() as s:
            query = await s.execute(select(self.model).where(self.model.id == id))
            result = query.scalars().first()
            return result

    async def get_multi(
        self, asyncSection: async_sessionmaker[AsyncSession], *, skip: int = 0, limit: int = 100
    ) -> Sequence[ModelType]:
        async with asyncSection() as s:
            query = await s.execute(select(self.model).offset(skip).limit(limit))
            return query.scalars().all()  # pragma: no cover  errorinCover: true

    # async def create(self, asyncSection: async_sessionmaker[AsyncSession], *, obj_in: CreateSchemaType) -> ModelType:
    #     obj_in_data = jsonable_encoder(obj_in)
    #     db_obj = self.model(**obj_in_data)
    #     async with asyncSection() as s:
    #         s.add(db_obj)
    #         await s.commit()
    #         await s.refresh(db_obj)
    #         return db_obj

    async def update(
        self,
        asyncSection: async_sessionmaker[AsyncSession],
        *,
        db_obj: ModelType,
        obj_in: UpdateSchemaType | dict[str, Any],
    ) -> ModelType:
        obj_data = jsonable_encoder(db_obj)
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        async with asyncSection() as s:
            s.add(db_obj)
            await s.commit()
            await s.refresh(db_obj)
        return db_obj

    async def remove(self, asyncSection: async_sessionmaker[AsyncSession], *, id: int) -> Optional[ModelType]:
        async with asyncSection() as s:
            query = await s.execute(select(self.model).where(self.model.id == id))
            result = query.scalars().first()
            await s.execute(delete(self.model).where(self.model.id == id))
            await s.commit()
            return result


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
        self, asyncSection: async_sessionmaker[AsyncSession], *, obj_in: CreateSchemaType, owner_id: int
    ) -> ModelType:
        obj_in_data = jsonable_encoder(obj_in)
        obj_in_data["owner_id"] = owner_id
        db_obj = self.model(**obj_in_data)
        async with asyncSection() as s:
            s.add(db_obj)
            await s.commit()
            await s.refresh(db_obj)
            return db_obj

    async def get_multi_by_owner(
        self, asyncSection: async_sessionmaker[AsyncSession], *, owner_id: int, skip: int = 0, limit: int = 100
    ) -> Sequence[ModelType]:
        async with asyncSection() as s:
            query = await s.execute(
                select(self.model).where(getattr(self.model, "owner_id") == owner_id).offset(skip).limit(limit)
            )
            return query.scalars().all()  # pragma: no cover  errorinCover: true
