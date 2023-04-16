from typing import TYPE_CHECKING, Optional

from lau_commons.sqlalchemy_base_class import ModelTemplate
from pydantic import BaseModel
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, relationship

if TYPE_CHECKING:
    from app.modules.lau_plang.models.sql.subset import SubsetOrm  # noqa: F401 # pragma: no cover


class SourceCodeOrm(ModelTemplate):
    __tablename__ = "plang_source_code"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    path = Column(String)
    pathList = Column(String)
    type = Column(String, index=True)
    subset_id = Column(Integer, ForeignKey("plang_subset.id", ondelete="CASCADE"))
    subset: Mapped["SubsetOrm"] = relationship("SubsetOrm", back_populates="sourceCodes")


class SourceCodeModel(BaseModel):
    id: int
    name: str
    subset_id: int
    path: str
    pathList: str
    type: str

    class Config:
        orm_mode = True


class SourceCodeView(SourceCodeModel):
    pass


class SourceCodeUpdate(BaseModel):
    id: int
    name: Optional[str] = None
    subset_id: int
    path: Optional[str]
    pathList: Optional[str]
    type: str


# Properties to receive on item creation


class SourceCodeCreate(BaseModel):
    name: str
    subset_id: int
    path: Optional[str]
    pathList: Optional[str]
    type: str
