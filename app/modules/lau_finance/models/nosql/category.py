from typing import ForwardRef, Optional, Union

from pydantic import BaseModel

from app.core.pydanticObjectId import PydanticObjectId


CategoryOrm = ForwardRef('CategoryOrm')

class CategoryOrm(BaseModel):
    name: str
    owner_id: int
    parent_id: Optional[PydanticObjectId]

    class Config:
        collection = "fin_category"

CategoryOrm.update_forward_refs()

# Union[ForwardRef('CategoryOrm'), None].update_forward_refs()
# Properties shared by models stored in DB


class CategoryModel(BaseModel):
    id: PydanticObjectId()
    name: str
    owner_id: int
    parent_id: Optional[PydanticObjectId]


# Properties to return to client
class CategoryView(CategoryModel):
    pass


# Properties to receive on item update
class CategoryUpdate(Model):
    name: Optional[str] = None
    parent_id: Optional[ObjectId]


# Properties to receive on item creation


class CategoryCreate(BaseModel):
    name: str
    parent_id: Optional[ObjectId] = None
