from enum import Enum
from typing import Optional

from pydantic import UUID4, BaseModel, ConfigDict, HttpUrl
from pydantic_extra_types.color import Color

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
    conciliateId: Optional[UUID4] = None
    is_active: bool = True
    type: InstitutionType = InstitutionType.PERSONAL_BANK
    primaryColor: Optional[Color] = None
    imageUrl: HttpUrl | None = None
    country: CountryCode = CountryCode.BRAZIL
    model_config = ConfigDict(from_attributes=True)


class InstitutionView(Institution):
    pass


class InstitutionUpdate(BaseModel):
    name: Optional[str] = None


class InstitutionCreate(BaseModel):
    name: str
    is_test: bool = False
