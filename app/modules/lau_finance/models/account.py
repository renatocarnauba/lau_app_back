from typing import Optional

from pydantic import UUID4, BaseModel

from app.modules.lau_commons.models.baseModel import ModelTemplate


class AccountOrm(ModelTemplate):
    __tablename__ = "fin_account"

    owner_id: int


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
