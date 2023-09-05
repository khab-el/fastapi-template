from __future__ import annotations

import typing as t

from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, relationship

from src.app.entity.base import Base
from src.app.entity.mixin import TimestampMixin

if t.TYPE_CHECKING:
    from src.app.entity.category import Category
    from src.app.entity.provider_entity import ProviderEnity


class Service(TimestampMixin, Base):

    name: Mapped[str] = sa.Column(sa.String(255), nullable=False)
    url: Mapped[str] = sa.Column(sa.String(255), nullable=True)
    operating_hours: Mapped[str] = sa.Column(sa.String(255), nullable=True)

    provider_entity_id: Mapped[list[UUID]] = sa.Column(sa.UUID, sa.ForeignKey("providerenity.id"), nullable=True)

    provider_entity: Mapped[list[ProviderEnity]] = relationship(
        "ProviderEnity",
        back_populates="service",
        order_by="Service.id",
        # cascade="save-update, merge, refresh-expire, expunge, delete, delete-orphan",
    )
    category: Mapped[list[Category]] = relationship(
        "Category",
        secondary="category_x_service",
        back_populates="service",
    )
