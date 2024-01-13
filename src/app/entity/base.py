import typing as t

import sqlalchemy as sa
from multimethod import multimethod as overload
from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import DeclarativeBase

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):

    __abstract__ = True
    metadata = MetaData(naming_convention=convention)  # type: ignore

    def __repr__(self) -> str:  # noqa: D105
        columns = ", ".join(
            [f"{k}={repr(v)}" for k, v in self.__dict__.items() if not k.startswith("_")],
        )
        return f"<{self.__class__.__name__}({columns})>"

    @declared_attr.directive
    def __tablename__(cls) -> str:  # noqa: N805 D105
        return cls.__name__.lower()

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
    async def get_all(cls, async_session: AsyncSession) -> t.List[t.Optional["Base"]]:  # type: ignore
        """Select from db single model by pk - id."""
        stmt = sa.select(cls)
        async_result = await async_session.execute(statement=stmt)
        objects_all = async_result.fetchall()
        return objects_all

    @overload
    async def pre_save(cls, async_session: AsyncSession, instance: "Base", **kwargs: t.Any) -> "Base":  # noqa
        if cls.has_pk(instance):
            return await async_session.merge(instance, **kwargs)

        async_session.add(instance, **kwargs)
        await async_session.flush([instance])
        return instance

    @classmethod
    @pre_save.register
    async def _(cls, async_session: AsyncSession, instances: t.Sequence["Base"]) -> t.Sequence["Base"]:
        async_session.add_all(instances)
        await async_session.flush(instances)
        return instances

    @overload
    async def save(cls, async_session: AsyncSession, instance: "Base", **kwargs: t.Any) -> "Base":  # noqa
        instance = await cls.pre_save(async_session, instance, **kwargs)
        await async_session.commit()
        return instance

    @classmethod
    @save.register
    async def _(cls, async_session: AsyncSession, instances: t.Sequence["Base"]) -> t.Sequence["Base"]:
        instances = await cls.pre_save(async_session, instances)
        await async_session.commit()
        return instances

    @classmethod
    def merge(cls, object_instance: "Base", **attrs: t.Any) -> "Base":
        """Merge model instance."""
        for attr_key, attr_value in attrs.items():
            setattr(object_instance, attr_key, attr_value)

        return object_instance
