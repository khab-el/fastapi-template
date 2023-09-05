from __future__ import annotations

import typing as t

import sqlalchemy as sa
from sqlalchemy.orm import Mapped

from src.app.entity.base import Base

if t.TYPE_CHECKING:
    from src.app.entity.category import Category
    from src.app.entity.service import Service


class CategoryXService(Base):

    __tablename__ = "category_x_service"

    category_id: Mapped[Category] = sa.Column(
        sa.UUID,
        sa.ForeignKey("category.id"),
        primary_key=True,
    )
    service_id: Mapped[Service] = sa.Column(
        sa.UUID,
        sa.ForeignKey("service.id"),
        primary_key=True,
    )
