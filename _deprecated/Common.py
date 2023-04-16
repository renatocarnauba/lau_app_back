from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy.orm import declarative_base

Base = declarative_base()


class TipoIcone(str, Enum):
    NOME_DO_ICONE = "nome_do_icone"
    IMAGEM_LOCAL = "imagem_local"
    LINK = "link"


class Icone(Base):

    referencia: Optional[str] = "info"
    tipo: Optional[TipoIcone] = "nome_do_icone"
    data_inclusao: datetime = datetime.now()
    data_manutencao: datetime = datetime.now()
