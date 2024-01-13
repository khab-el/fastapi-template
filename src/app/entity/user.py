import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from src.app.entity.base import Base
from src.app.entity.mixin import IDMixin, TimestampMixin


class User(IDMixin, TimestampMixin, Base):

    __table_args__ = (
        sa.UniqueConstraint("username"),
        sa.UniqueConstraint("email"),
    )

    username: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    phone: Mapped[str] = mapped_column(sa.String(255), nullable=True)
    email: Mapped[str] = mapped_column(sa.String(255), index=True, nullable=False)
