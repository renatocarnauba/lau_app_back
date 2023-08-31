from app.modules.lau_commons.crud.baseAsync import CRUDBaseMultiAsync
from app.modules.lau_finance.models.institution import (
    Institution,
    InstitutionCreate,
    InstitutionUpdate,
)


class CRUDInstitution(CRUDBaseMultiAsync[Institution, InstitutionCreate, InstitutionUpdate]):
    ...


institution = CRUDInstitution(Institution)
