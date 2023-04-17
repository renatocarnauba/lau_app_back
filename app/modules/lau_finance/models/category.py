from typing import ForwardRef, Optional

from pydantic import BaseModel

from app.modules.lau_commons.core.pydanticObjectId import PydanticObjectId
from app.modules.lau_commons.models.baseModel import ModelTemplate

CategoryOrm = ForwardRef("CategoryOrm")


class CategoryOrm(ModelTemplate):
    name: str
    owner_id: int
    parent_id: Optional[int]

CategoryOrm.update_forward_refs()

# Union[ForwardRef('CategoryOrm'), None].update_forward_refs()
# Properties shared by models stored in DB


class CategoryModel(BaseModel):
    id: PydanticObjectId()
    name: str
    owner_id: int
    parent_id: Optional[int]


# Properties to return to client
class CategoryView(CategoryModel):
    pass


# Properties to receive on item update
class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    parent_id: Optional[int]


# Properties to receive on item creation


class CategoryCreate(BaseModel):
    name: str
    parent_id: Optional[int] = None
