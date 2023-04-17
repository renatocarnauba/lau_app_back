from typing import Optional

from pydantic import UUID4, BaseModel

from app.modules.lau_commons.models.baseModel import ModelTemplate


class Category(ModelTemplate):
    __tablename__ = "fin_category"
    name: str
    owner_id: str
    parent_id: Optional[UUID4]


# Properties to return to client
class CategoryView(Category):
    pass


# Properties to receive on item update
class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    parent_id: Optional[UUID4]


# Properties to receive on item creation


class CategoryCreate(BaseModel):
    name: str
    parent_id: Optional[UUID4] = None
    is_test: bool = False
