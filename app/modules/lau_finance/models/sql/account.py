from typing import TYPE_CHECKING, Optional

from lau_commons.sqlalchemy_base_class import ModelTemplate
from pydantic import BaseModel
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, relationship

if TYPE_CHECKING:
    from app.models.sql.user import User  # noqa: F401 # pragma: no cover


class AccountOrm(ModelTemplate):
    __tablename__ = "fin_account"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    owner_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"))
    owner: Mapped["User"] = relationship("User", back_populates="accounts")


# Properties to receive on item creation


class AccountModel(BaseModel):
    id: int
    name: str
    owner_id: int

    class Config:
        orm_mode = True


class AccountView(AccountModel):
    pass


class AccountUpdate(BaseModel):
    name: Optional[str] = None


class AccountCreate(BaseModel):
    name: str
