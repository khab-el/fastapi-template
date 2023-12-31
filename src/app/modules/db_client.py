import typing as t

import logging
import time
from uuid import uuid4

from sqlalchemy import text
from sqlalchemy.engine.row import Row
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.config import settings


class AsyncDBClient:

    _connection_flg: bool = False
    async_engine: AsyncEngine
    AsyncSessionLocal: async_sessionmaker[AsyncSession]
    log: logging.Logger = logging.getLogger(__name__)

    @classmethod
    def get_async_db_engine(cls) -> AsyncEngine:
        """Create async db engine.

        :return: _description_
        :rtype: AsyncEngine
        """
        if not cls._connection_flg:
            cls.log.debug("Initialize AsyncEngine.")
            cls.async_engine = create_async_engine(
                settings.DB_URI,
                pool_pre_ping=True,
                echo=settings.ECHO_SQL,
            )
            cls.AsyncSessionLocal = async_sessionmaker(
                bind=cls.async_engine,
                expire_on_commit=False,
                autoflush=False,
                future=True,
            )
            cls._connection_flg = True
        return cls.async_engine

    @classmethod
    async def close_db_engine(cls) -> None:
        """Dispose of the connection pool used by this _asyncio.AsyncEngine."""
        if cls._connection_flg:
            await cls.async_engine.dispose()
            cls._connection_flg = False

    @classmethod
    async def _get_session(cls) -> t.AsyncIterator[async_sessionmaker[AsyncSession]]:
        """Helper."""
        try:
            yield cls.AsyncSessionLocal
        except SQLAlchemyError as e:
            cls.log.exception(e)

    @classmethod
    async def get_session(cls) -> async_sessionmaker[AsyncSession]:
        """Get async db session.

        :return: _description_
        :rtype: async_sessionmaker
        """
        return await anext(cls._get_session())

    @classmethod
    async def iter_cursor(
        cls,
        query: str,
        params: t.Mapping[str, t.Any],
        batch_size: int = 1_000,
        cur_name_: str | None = None,
    ) -> t.AsyncIterator[t.Sequence[Row[t.Any]]]:
        """Server side db cursor."""
        cur_name = f"cur_{cur_name_ or uuid4().hex}_{time.time_ns()}"
        query_cursor = f"DECLARE {cur_name} CURSOR FOR {query}"
        query_next_page = f"FETCH %(batch_size)s FROM {cur_name}"
        params_next_page = {"batch_size": batch_size}

        async with cls.async_engine.begin() as conn:
            await conn.execute(text(query_cursor), params)

            while True:
                res = await conn.execute(text(query_next_page), params_next_page)
                batch = res.fetchall()
                if not len(batch):
                    return
                yield batch
