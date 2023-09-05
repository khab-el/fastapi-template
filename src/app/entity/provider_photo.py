from __future__ import annotations

import typing as t

from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, relationship

from src.app.entity.base import Base

if t.TYPE_CHECKING:
    from src.app.entity.provider_contact import ProviderContact


class ProviderPhoto(Base):

    picture_path: Mapped[str] = sa.Column(sa.String(255), nullable=True)

    provider_contact_id: Mapped[list[UUID]] = sa.Column(sa.UUID, sa.ForeignKey("providercontact.id"), nullable=True)

    provider_contact: Mapped[list[ProviderContact]] = relationship(
        "ProviderContact",
        back_populates="provider_photo",
        order_by="ProviderContact.id",
        # cascade="save-update, merge, refresh-expire, expunge, delete, delete-orphan",
    )
