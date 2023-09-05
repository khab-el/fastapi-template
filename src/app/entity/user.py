import sqlalchemy as sa

from src.app.entity.base import Base
from src.app.entity.mixin import TimestampMixin


class User(TimestampMixin, Base):

    __table_args__ = (
        sa.UniqueConstraint("username"),
        sa.UniqueConstraint("email"),
    )

    username = sa.Column(sa.String(255), nullable=False)
    phone = sa.Column(sa.String(255), nullable=True)
    email = sa.Column(sa.String(255), index=True, nullable=False)
