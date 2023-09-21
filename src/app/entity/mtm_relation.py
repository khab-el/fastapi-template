from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from src.app.entity.base import Base


class CategoryXService(Base):

    __tablename__ = "category_x_service"  # type: ignore

    category_id: Mapped[UUID] = mapped_column(
        sa.ForeignKey("category.id"),
        primary_key=True,
    )
    service_id: Mapped[UUID] = mapped_column(
        sa.ForeignKey("service.id"),
        primary_key=True,
    )
