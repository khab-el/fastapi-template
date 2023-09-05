import typing as t

from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import declarative_mixin


@declarative_mixin
class TimestampMixin:

    created_at = sa.Column(
        sa.DateTime,
        default=sa.func.now(),
        server_default=sa.FetchedValue(),
    )
    updated_at = sa.Column(
        sa.DateTime,
        onupdate=sa.func.now(),
        server_default=sa.FetchedValue(),
        server_onupdate=sa.FetchedValue(),
    )
    deleted_at = sa.Column(sa.DateTime, server_default=sa.FetchedValue())

    @classmethod
    async def find_one(cls, async_session: AsyncSession, object_id: UUID) -> t.Self | None:
        """Select from db single model by pk - id."""
        stmt = sa.select(cls).where(
            cls.id == object_id,
            cls.deleted_at.is_(None),
        )
        return await async_session.scalar(stmt)

    @classmethod
    async def delete(cls, async_session: AsyncSession, object_id: UUID) -> None:
        """Soft delete model from db."""
        object_instance = await cls.find_one_or_fail(object_id)
        cls.merge(object_instance, deleted_at=sa.func.now())
        await cls.save(async_session, object_instance)
