from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr

from app.modules.lau_commons.models.baseModel import ModelTemplate


# Shared properties
class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = True
    is_superuser: bool = False
    full_name: Optional[str] = None
    is_test: bool = False


# Properties to receive via API on creation
class UserCreate(UserBase):
    email: EmailStr
    password: str


# Properties to receive via API on update
class UserUpdate(UserBase):
    password: Optional[str] = None


class UserView(ModelTemplate, UserBase):
    ...


# Additional properties to return via API


class User(ModelTemplate, UserBase):
    hashed_password: str
    model_config = ConfigDict(from_attributes=True)
