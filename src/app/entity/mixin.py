import typing as t

from datetime import datetime
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql as psql
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, declarative_mixin, mapped_column

from src.app.entity.base import Base


@declarative_mixin
class IDMixin:

    id: Mapped[UUID] = mapped_column(  # noqa: A003
        psql.UUID(as_uuid=True),
        server_default=sa.text("gen_random_uuid()"),
        primary_key=True,
        index=True,
    )

    @classmethod
    async def find_one(cls, async_session: AsyncSession, object_id: UUID) -> t.Optional["Base"]:
        """Select from db single model by pk - id."""
        stmt = sa.select(cls).where(cls.id == object_id)
        return await async_session.scalar(stmt)

    @classmethod
    async def find_one_or_fail(cls, async_session: AsyncSession, object_id: UUID) -> "Base":
        """Find single model by pk - id."""
        object_instance = await cls.find_one(async_session, object_id)
        if object_instance is None:
            raise NoResultFound(f"{cls.__name__} not found")
        return object_instance

    @classmethod
    async def delete(cls, async_session: AsyncSession, object_id: UUID) -> None:
        """Hard delete model instance."""
        stmt = sa.delete(cls).where(cls.id == object_id)
        await async_session.execute(stmt)
        await async_session.commit()


@declarative_mixin
class TimestampMixin:
    """Nested IDMixin (not need use IDMixin in orm model)."""

    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime,
        default=sa.func.now(),
        server_default=sa.FetchedValue(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        sa.DateTime,
        onupdate=sa.func.now(),
        server_default=sa.FetchedValue(),
        server_onupdate=sa.FetchedValue(),
    )
    deleted_at: Mapped[datetime] = mapped_column(sa.DateTime, server_default=sa.FetchedValue(), nullable=True)

    @classmethod
    async def find_one(cls, async_session: AsyncSession, object_id: UUID) -> t.Optional["Base"]:
        """Select from db single model by pk - id."""
        stmt = sa.select(cls).where(
            cls.id == object_id,
            cls.deleted_at.is_(None),
        )
        return await async_session.scalar(stmt)

    @classmethod
    async def delete(cls, async_session: AsyncSession, object_id: UUID) -> None:
        """Soft delete model from db."""
        object_instance = await cls.find_one_or_fail(async_session, object_id)
        cls.merge(object_instance, deleted_at=sa.func.now())
        await cls.save(async_session, object_instance)
