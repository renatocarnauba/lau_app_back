from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Conta(Base):
    __tablename__ = "conta"

    id = Column(Integer, primary_key=True)
    nome = Column(String)

    def __repr__(self):
        return f"Conta({self.nome})"
