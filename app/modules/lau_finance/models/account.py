from typing import Optional

from pydantic import UUID4, BaseModel

from app.modules.lau_commons.models.baseModel import ModelTemplate


class Account(ModelTemplate):
    name: str
    owner_id: str

    class Config:
        orm_mode = True


class AccountView(Account):
    pass


class AccountUpdate(BaseModel):
    name: Optional[str] = None


class AccountCreate(BaseModel):
    name: str
