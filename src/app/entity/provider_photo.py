import sqlalchemy as sa
from sqlalchemy.orm import Mapped, relationship

from src.app.entity.base import Base
from src.app.entity.provider_contact import ProviderContact


class ProviderPhoto(Base):

    provider_contact: Mapped[list[ProviderContact]] = relationship(
        "ProviderContact",
        back_populates="provider_entity",
        order_by="ProviderContact.id",
        # cascade="save-update, merge, refresh-expire, expunge, delete, delete-orphan",
    )
    picture_path: Mapped[str] = sa.Column(sa.Text(255), nullable=True)
