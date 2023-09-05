from __future__ import annotations

import typing as t

from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql as psql
from sqlalchemy.orm import Mapped, relationship

from src.app.entity.base import Base
from src.app.entity.mixin import TimestampMixin

if t.TYPE_CHECKING:
    from src.app.entity.service import Service


class Category(TimestampMixin, Base):

    id = sa.Column(  # noqa: A003
        psql.UUID(as_uuid=True),
        server_default=sa.text("gen_random_uuid()"),
        primary_key=True,
        index=True,
    )
    category_title: Mapped[str] = sa.Column(sa.String(255), nullable=True)
    category_description: Mapped[str] = sa.Column(sa.String(255), nullable=True)

    parent_category_id: Mapped[list[UUID]] = sa.Column(sa.UUID, sa.ForeignKey("category.id"), nullable=True)
    parent_category: Mapped[t.Self] = relationship(
        "Category",
        remote_side=[id],
    )
    service: Mapped[Service] = relationship(
        "Service",
        secondary="category_x_service",
        back_populates="category",
    )
