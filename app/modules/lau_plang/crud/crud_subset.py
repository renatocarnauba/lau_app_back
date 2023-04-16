from app.crud.baseAsync import CRUDBaseMultiAsync
from app.modules.lau_plang.models.sql.subset import (
    SubsetCreate,
    SubsetOrm,
    SubsetUpdate,
)


class CRUDSubset(CRUDBaseMultiAsync[SubsetOrm, SubsetCreate, SubsetUpdate]):
    ...


subset = CRUDSubset(SubsetOrm)
