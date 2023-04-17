from typing import Optional, TypeVar
from uuid import UUID

from pydantic import BaseModel

from app.modules.lau_commons.crud.baseAsync import CRUDBaseMultiAsync
from app.modules.lau_finance.models.category import (
    Category,
    CategoryCreate,
    CategoryUpdate,
)

Base = BaseModel
Base = TypeVar("Base", bound=Base)


class CRUDCategory(CRUDBaseMultiAsync[Category, CategoryCreate, CategoryUpdate]):
    async def remove(self, *, id: str) -> Optional[Base]:
        if isinstance(id, UUID):
            id = str(id)
        objFind = await self.get(id)
        coll = await self.coll
        filterDel = {"id": id}
        await coll.delete_one(filterDel)
        filterDel = {"parent_id": id}
        await coll.delete_many(filterDel)
        return objFind


category = CRUDCategory(Category)
