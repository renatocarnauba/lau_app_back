from datetime import datetime
from typing import Optional
from uuid import uuid4

from lau_utils.classproperty import classproperty
from pydantic import UUID4, BaseModel, Field


# Shared properties
class ModelTemplate(BaseModel):
    id: UUID4 = Field(default_factory=uuid4)
    created_at: Optional[datetime] = datetime.now()
    updated_at: Optional[datetime] = datetime.now()
    is_test: bool = False

    @classmethod
    @classproperty
    def __tablename__(cls) -> str:
        return cls.__name__.lower()
