import sqlalchemy as sa
from sqlalchemy.orm import Mapped, relationship

from src.app.entity.base import Base
from src.app.entity.mixin import TimestampMixin
from src.app.entity.provider_contact import ProviderContact


class ProviderEnity(TimestampMixin, Base):

    provider_contact: Mapped[list[ProviderContact]] = relationship(
        "ProviderContact",
        back_populates="provider_entity",
        order_by="ProviderContact.id",
        # cascade="save-update, merge, refresh-expire, expunge, delete, delete-orphan",
    )
    address: Mapped[str] = sa.Column(sa.String(255), nullable=True)
    primary_phone: Mapped[str] = sa.Column(sa.String(255), nullable=True)
    secondary_phone: Mapped[str] = sa.Column(sa.String(255), nullable=True)
    lat: Mapped[float] = sa.Column(sa.Numeric(8, 6), nullable=True)
    lon: Mapped[float] = sa.Column(sa.Numeric(8, 6), nullable=True)
