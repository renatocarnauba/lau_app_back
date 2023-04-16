from __future__ import annotations

from typing import TYPE_CHECKING, List

from lau_commons.sqlalchemy_base_class import ModelTemplate
from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import Mapped, relationship

if TYPE_CHECKING:  # noqa: F401 # pragma: no cover
    from app.modules.lau_finance.models.sql.account import AccountOrm
    from app.modules.lau_plang.models.sql.subset import SubsetOrm


class User(ModelTemplate):
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    is_test = Column(Boolean, default=False)
    accounts: Mapped[List["AccountOrm"]] = relationship(
        "AccountOrm", cascade="all, delete", back_populates="owner", passive_deletes=True
    )
    subsets: Mapped[List["SubsetOrm"]] = relationship(
        "SubsetOrm", cascade="all, delete", back_populates="owner", passive_deletes=True
    )
