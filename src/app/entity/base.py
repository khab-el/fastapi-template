from sqlalchemy import MetaData
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
    metadata: MetaData(naming_convention=convention)  # type: ignore

    def __repr__(self) -> str:  # noqa: D105
        columns = ", ".join(
            [f"{k}={repr(v)}" for k, v in self.__dict__.items() if not k.startswith("_")],
        )
        return f"<{self.__class__.__name__}({columns})>"

    @declared_attr
    def __tablename__(cls) -> str:  # noqa: N805 D105
        return cls.__name__.lower()
