# Import all the models, so that Base has them before being
# imported by Alembic
from lau_commons.sqlalchemy_base_class import ModelTemplate  # noqa

from app.models.sql.user import User  # noqa
from app.modules.lau_finance.models.sql.account import AccountOrm  # noqa
from app.modules.lau_plang.models.sql.assemblerStmt import AssemblerStmtCreate  # noqa
from app.modules.lau_plang.models.sql.sourceCode import SourceCodeOrm  # noqa
from app.modules.lau_plang.models.sql.subset import SubsetOrm  # noqa
