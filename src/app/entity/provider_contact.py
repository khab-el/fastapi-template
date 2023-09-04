import sqlalchemy as sa
from sqlalchemy.orm import Mapped

from src.app.entity.base import Base
from src.app.entity.mixin import TimestampMixin


class ProviderContact(TimestampMixin, Base):

    name: Mapped[str] = sa.Column(sa.String(255), nullable=False)
    phone: Mapped[str] = sa.Column(sa.String(255), nullable=True)
    email: Mapped[str] = sa.Column(sa.String(255), nullable=True)
    additional_info: Mapped[str] = sa.Column(sa.Text(255), nullable=True)
