from enum import Enum
from typing import Optional

from pydantic import UUID4, BaseModel, HttpUrl
from pydantic.color import Color

from app.modules.lau_commons.models.baseModel import ModelTemplate


class InstitutionType(str, Enum):
    PERSONAL_BANK = "PERSONAL_BANK"
    INVESTMENT = "INVESTMENT"
    BUSINESS_BANK = "BUSINESS_BANK"


class CountryCode(str, Enum):
    BRAZIL = "BR"


class Institution(ModelTemplate):
    __tablename__ = "fin_institution"
    name: str
    owner_id: str
    conciliateId: Optional[UUID4]
    is_active: bool = True
    type: InstitutionType
    primaryColor: Color
    imageUrl: HttpUrl
    country: CountryCode

    class Config:
        orm_mode = True


class InstitutionView(Institution):
    pass


class InstitutionUpdate(BaseModel):
    name: Optional[str] = None


class InstitutionCreate(BaseModel):
    name: str
    is_test: bool = False
