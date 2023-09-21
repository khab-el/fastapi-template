from __future__ import annotations

import typing as t

from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.app.entity.base import Base
from src.app.entity.mixin import IDMixin

if t.TYPE_CHECKING:
    from src.app.entity.provider_contact import ProviderContact


class ProviderPhoto(IDMixin, Base):

    picture_path: Mapped[str] = mapped_column(sa.String(255), nullable=True)

    provider_contact_id: Mapped[list[UUID]] = mapped_column(sa.ForeignKey("providercontact.id"), nullable=True)

    provider_contact: Mapped[list["ProviderContact"]] = relationship(
        "ProviderContact",
        back_populates="provider_photo",
        order_by="ProviderContact.id",
        # cascade="save-update, merge, refresh-expire, expunge, delete, delete-orphan",
    )
