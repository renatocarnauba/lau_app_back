from typing import Optional

from lau_commons.sqlalchemy_base_class import ModelTemplate
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String


class AssemblerStmtOrm(ModelTemplate):
    __tablename__ = "plang_assembler_stmt"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, unique=True, nullable=False)
    type = Column(String)
    cc = Column(String)
    pf_ipq = Column(String)


class AssemblerStmtModel(BaseModel):
    id: int
    name: str
    type: Optional[str]
    cc: Optional[str]
    pf_ipq: Optional[str]

    class Config:
        orm_mode = True


class AssemblerStmtView(AssemblerStmtModel):
    pass


class AssemblerStmtUpdate(BaseModel):
    name: Optional[str] = None


class AssemblerStmtCreate(BaseModel):
    name: str
    type: Optional[str]
    cc: Optional[str]
    pf_ipq: Optional[str]
