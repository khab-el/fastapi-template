from __future__ import annotations

import typing as t

from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.app.entity.base import Base
from src.app.entity.mixin import TimestampMixin, IDMixin

if t.TYPE_CHECKING:
    from src.app.entity.service import Service


class Category(TimestampMixin, IDMixin, Base):

    category_title: Mapped[str] = mapped_column(sa.String(255), nullable=True)
    category_description: Mapped[str] = mapped_column(sa.String(255), nullable=True)

    parent_category_id: Mapped[list[UUID]] = mapped_column(sa.ForeignKey("category.id"), nullable=True)
    parent_category: Mapped["t.Self"] = relationship(
        "Category",
        remote_side="category.id",
    )
    service: Mapped["Service"] = relationship(
        "Service",
        secondary="category_x_service",
        back_populates="category",
    )
