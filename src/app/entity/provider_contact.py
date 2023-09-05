from __future__ import annotations

import typing as t

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, relationship

from src.app.entity.base import Base
from src.app.entity.mixin import TimestampMixin

if t.TYPE_CHECKING:
    from src.app.entity.provider_entity import ProviderEnity
    from src.app.entity.provider_photo import ProviderPhoto


class ProviderContact(TimestampMixin, Base):

    name: Mapped[str] = sa.Column(sa.String(255), nullable=False)
    phone: Mapped[str] = sa.Column(sa.String(255), nullable=True)
    email: Mapped[str] = sa.Column(sa.String(255), nullable=True)
    additional_info: Mapped[str] = sa.Column(sa.String(255), nullable=True)

    provider_entity: Mapped[list[ProviderEnity]] = relationship(
        "ProviderEnity",
        back_populates="provider_contact",
        order_by="ProviderEnity.id",
        # cascade="save-update, merge, refresh-expire, expunge, delete, delete-orphan",
    )
    provider_photo: Mapped[list[ProviderPhoto]] = relationship(
        "ProviderPhoto",
        back_populates="provider_contact",
        order_by="ProviderPhoto.id",
        # cascade="save-update, merge, refresh-expire, expunge, delete, delete-orphan",
    )
