import typing as t

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, relationship

from src.app.entity.base import Base
from src.app.entity.mixin import TimestampMixin
from src.app.entity.service import Service


class Category(TimestampMixin, Base):

    parent_category: Mapped[t.Self] = relationship(
        "Category",
        back_populates="parent_category",
        order_by="Category.id",
        # cascade="save-update, merge, refresh-expire, expunge, delete, delete-orphan",
    )
    service: Mapped[Service] = relationship(
        "Service",
        secondary="category_x_service",
        back_populates="category",
    )
    category_title: Mapped[str] = sa.Column(sa.String(255), nullable=True)
    category_description: Mapped[str] = sa.Column(sa.String(255), nullable=True)
