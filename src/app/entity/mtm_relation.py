import sqlalchemy as sa
from sqlalchemy.orm import Mapped

from src.app.entity.base import Base
from src.app.entity.category import Category
from src.app.entity.service import Service


class CategoryXService(Base):

    __name__ = "category_x_service"

    category: Mapped[Category] = sa.Column(
        sa.Integer,
        sa.ForeignKey("category.id"),
        primary_key=True,
    )
    service: Mapped[Service] = sa.Column(
        sa.Integer,
        sa.ForeignKey("service.id"),
        primary_key=True,
    )
