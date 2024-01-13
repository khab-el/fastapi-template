import typing as t

from datetime import datetime
from uuid import UUID

import sqlalchemy as sa
from multimethod import multimethod as overload
from sqlalchemy.dialects import postgresql as psql
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, declarative_mixin, mapped_column

from src.app.entity.base import Base


@declarative_mixin
class IDMixin:

    __mapper_args__ = {'always_refresh': True, "eager_defaults": True}

    id: Mapped[UUID] = mapped_column(  # noqa: A003
        psql.UUID(as_uuid=True),
        server_default=sa.text("gen_random_uuid()"),
        primary_key=True,
        index=True,
    )

    @classmethod
    def get_pk(cls, object_instance: "Base") -> t.Dict[str, t.Any] | t.Any:
        """Get pk."""
        server_default_pks = (pk for pk in cls.__mapper__.primary_key if pk.server_default is not None)  # type: ignore
        pks = {
            pk.name: attr for pk in server_default_pks if (attr := getattr(object_instance, pk.name)) is not None
        }  # noqa, type: ignore

        if len(pks) == 1:
            return next(iter(pks.values()))

        if len(pks) > 1:
            return pks

        return None

    @classmethod
    def has_pk(cls, object_instance: "Base") -> bool:
        """Model has pk."""
        return bool(cls.get_pk(object_instance))

    @classmethod
    def merge(cls, object_instance: "Base", **attrs: t.Any) -> "Base":
        """Merge model instance."""
        for attr_key, attr_value in attrs.items():
            setattr(object_instance, attr_key, attr_value)

        return object_instance

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

    # @classmethod
    @overload
    async def pre_save(cls, async_session: AsyncSession, instance: "Base", **kwargs: t.Any) -> "Base":  # noqa
        if cls.has_pk(instance):
            return await async_session.merge(instance, **kwargs)

        async_session.add(instance, **kwargs)
        await async_session.flush([instance])
        return instance

    @classmethod
    @pre_save.register
    async def _(cls, async_session: AsyncSession, instances: t.Sequence["Base"]) -> t.Sequence["Base"]:  # noqa
        async_session.add_all(instances)
        await async_session.flush(instances)
        return instances

    # @classmethod
    @overload
    async def save(cls, async_session: AsyncSession, instance: "Base", **kwargs: t.Any) -> "Base":  # noqa
        instance = await cls.pre_save(async_session, instance, **kwargs)
        await async_session.commit()
        return instance

    @classmethod
    @save.register
    async def _(cls, async_session: AsyncSession, instances: t.Sequence["Base"]) -> t.Sequence["Base"]:  # noqa
        instances = await cls.pre_save(async_session, instances)
        await async_session.commit()
        return instances


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
