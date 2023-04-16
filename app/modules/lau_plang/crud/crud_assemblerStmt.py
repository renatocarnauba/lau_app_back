from app.crud.baseAsync import CRUDBaseMultiAsync
from app.modules.lau_plang.models.sql.assemblerStmt import (
    AssemblerStmtCreate,
    AssemblerStmtOrm,
    AssemblerStmtUpdate,
)


class CRUDAssemblerStmt(CRUDBaseMultiAsync[AssemblerStmtOrm, AssemblerStmtCreate, AssemblerStmtUpdate]):
    ...


assemblerStmt = CRUDAssemblerStmt(AssemblerStmtOrm)
