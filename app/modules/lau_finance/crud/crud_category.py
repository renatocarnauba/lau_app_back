from app.crud.baseAsyncMongo import CRUDBaseMultiAsync
from app.modules.lau_finance.models.nosql.category import (
    CategoryCreate,
    CategoryOrm,
    CategoryUpdate,
)


class CRUDCategory(CRUDBaseMultiAsync[CategoryOrm, CategoryCreate, CategoryUpdate]):
    ...


category = CRUDCategory(CategoryOrm)
