import typing as t

from uuid import UUID

import sqlalchemy as sa
from multimethod import multimethod as overload
from sqlalchemy import MetaData
from sqlalchemy.dialects import postgresql as psql
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.declarative import as_declarative, declared_attr

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


@as_declarative()
class Base:

    __name__: str
    metadata: MetaData(naming_convention=convention)

    id = sa.Column(  # noqa: A003
        psql.UUID(as_uuid=True),
        server_default=sa.text("gen_random_uuid()"),
        primary_key=True,
        index=True,
    )

    def __repr__(self) -> str:  # noqa: D105
        columns = ", ".join(
            [f"{k}={repr(v)}" for k, v in self.__dict__.items() if not k.startswith("_")],
        )
        return f"<{self.__class__.__name__}({columns})>"

    @classmethod
    @declared_attr
    def __tablename__(cls) -> str:  # noqa: N805 D105
        return cls.__name__.lower()

    @classmethod
    def get_pk(cls, object_instance: t.Self) -> t.Dict[str, t.Any] | t.Any:
        """Get pk."""
        server_default_pks = (pk for pk in cls.__mapper__.primary_key if pk.server_default is not None)
        pks = {pk.name: attr for pk in server_default_pks if (attr := getattr(object_instance, pk.name)) is not None}

        if len(pks) == 1:
            return next(iter(pks.values()))
        elif len(pks) > 1:
            return pks

    @classmethod
    def has_pk(cls, object_instance: t.Self) -> bool:
        """Model has pk."""
        return bool(cls.get_pk(object_instance))

    @classmethod
    def merge(cls, object_instance: t.Self, **attrs) -> t.Self:
        """Merge model instance."""
        for attr_key, attr_value in attrs.items():
            setattr(object_instance, attr_key, attr_value)

        return object_instance

    @classmethod
    async def find_one(cls, async_session: AsyncSession, object_id: UUID) -> t.Self | None:
        """Select from db single model by pk - id."""
        stmt = sa.select(cls).where(cls.id == object_id)
        return await async_session.scalar(stmt)

    @classmethod
    async def find_one_or_fail(cls, async_session: AsyncSession, object_id: UUID) -> t.Self:
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

    @classmethod
    @overload
    async def pre_save(cls, async_session: AsyncSession, instance: t.Self, **kwargs) -> t.Self:
        if cls.has_pk(instance):
            return await async_session.merge(instance, **kwargs)

        async_session.add(instance, **kwargs)
        await async_session.flush([instance])
        return instance

    @classmethod
    @overload
    async def pre_save(cls, async_session: AsyncSession, instances: t.Sequence[t.Self]) -> t.Sequence[t.Self]:  # noqa
        async_session.add_all(instances)
        await async_session.flush(instances)
        return instances

    @classmethod
    @overload
    async def save(cls, async_session: AsyncSession, instance: t.Self, **kwargs) -> t.Self:
        instance = await cls.pre_save(async_session, instance, **kwargs)
        await async_session.commit()
        return instance

    @classmethod
    @overload
    async def save(cls, async_session: AsyncSession, instances: t.Sequence[t.Self]) -> t.Sequence[t.Self]:  # noqa
        instances = await cls.pre_save(async_session, instances)
        await async_session.commit()
        return instances
