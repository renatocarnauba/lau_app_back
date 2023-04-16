from typing import TYPE_CHECKING, Optional

from lau_commons.sqlalchemy_base_class import ModelTemplate
from pydantic import BaseModel
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, relationship

from app.modules.lau_plang.models.sql.sourceCode import SourceCodeOrm

if TYPE_CHECKING:
    from app.models.sql.user import User  # noqa: F401 # pragma: no cover


class SubsetOrm(ModelTemplate):
    __tablename__ = "plang_subset"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    parent_id = Column(Integer, ForeignKey("plang_subset.id", ondelete="CASCADE"))
    parent: Mapped["SubsetOrm"] = relationship("SubsetOrm", remote_side=[id])
    owner_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"))
    owner: Mapped["User"] = relationship("User", back_populates="subsets")
    sourceCodes: Mapped[list["SourceCodeOrm"]] = relationship(
        "SourceCodeOrm", cascade="all, delete", back_populates="subset", passive_deletes=True
    )


# Properties shared by models stored in DB
class SubsetModel(BaseModel):
    id: int
    name: str
    owner_id: int
    parent_id: int

    class Config:
        orm_mode = True


# Properties to return to client
class SubsetView(SubsetModel):
    pass


# Properties to receive on item update
class SubsetUpdate(BaseModel):
    id: int
    name: Optional[str] = None
    parent_id: Optional[int]


# Properties to receive on item creation


class SubsetCreate(BaseModel):
    name: str
    parent_id: Optional[int]
