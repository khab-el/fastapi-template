from __future__ import annotations

import typing as t

from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, relationship

from src.app.entity.base import Base
from src.app.entity.mixin import TimestampMixin

if t.TYPE_CHECKING:
    from src.app.entity.provider_contact import ProviderContact
    from src.app.entity.service import Service


class ProviderEnity(TimestampMixin, Base):

    address: Mapped[str] = sa.Column(sa.String(255), nullable=True)
    primary_phone: Mapped[str] = sa.Column(sa.String(255), nullable=True)
    secondary_phone: Mapped[str] = sa.Column(sa.String(255), nullable=True)
    lat: Mapped[float] = sa.Column(sa.Numeric(8, 6), nullable=True)
    lon: Mapped[float] = sa.Column(sa.Numeric(8, 6), nullable=True)

    provider_contact_id: Mapped[list[UUID]] = sa.Column(sa.UUID, sa.ForeignKey("providercontact.id"), nullable=True)

    provider_contact: Mapped[list[ProviderContact]] = relationship(
        "ProviderContact",
        back_populates="provider_entity",
        order_by="ProviderContact.id",
        # cascade="save-update, merge, refresh-expire, expunge, delete, delete-orphan",
    )
    service: Mapped[list[Service]] = relationship(
        "Service",
        back_populates="provider_entity",
        order_by="Service.id",
        # cascade="save-update, merge, refresh-expire, expunge, delete, delete-orphan",
    )
