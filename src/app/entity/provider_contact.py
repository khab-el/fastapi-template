from __future__ import annotations

import typing as t

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.app.entity.base import Base
from src.app.entity.mixin import TimestampMixin

if t.TYPE_CHECKING:
    from src.app.entity.provider_entity import ProviderEntity
    from src.app.entity.provider_photo import ProviderPhoto


class ProviderContact(TimestampMixin, Base):

    name: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    phone: Mapped[str] = mapped_column(sa.String(255), nullable=True)
    email: Mapped[str] = mapped_column(sa.String(255), nullable=True)
    additional_info: Mapped[str] = mapped_column(sa.String(255), nullable=True)

    provider_entity: Mapped[list["ProviderEntity"]] = relationship(
        "ProviderEntity",
        back_populates="provider_contact",
        order_by="ProviderEntity.id",
        # cascade="save-update, merge, refresh-expire, expunge, delete, delete-orphan",
    )
    provider_photo: Mapped[list["ProviderPhoto"]] = relationship(
        "ProviderPhoto",
        back_populates="provider_contact",
        order_by="ProviderPhoto.id",
        # cascade="save-update, merge, refresh-expire, expunge, delete, delete-orphan",
    )
