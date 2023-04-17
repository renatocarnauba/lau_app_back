from app.modules.lau_commons.crud.baseAsync import CRUDBaseMultiAsync
from app.modules.lau_finance.models.category import (
    CategoryCreate,
    CategoryOrm,
    CategoryUpdate,
)


class CRUDCategory(CRUDBaseMultiAsync[CategoryOrm, CategoryCreate, CategoryUpdate]):
    ...


category = CRUDCategory(CategoryOrm)
