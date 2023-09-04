import typing as t

import logging
import time
from uuid import uuid4

from sqlalchemy.engine.result import Result
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

    async_engine: t.Optional[AsyncEngine] = None
    AsyncSessionLocal: t.Optional[async_sessionmaker[AsyncSession]] = None
    log: logging.Logger = logging.getLogger(__name__)

    @classmethod
    def get_async_db_engine(cls) -> AsyncEngine:
        """Create async db engine.

        :return: _description_
        :rtype: AsyncEngine
        """
        if cls.async_engine is None:
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
        return cls.async_engine

    @classmethod
    async def close_db_engine(cls) -> None:
        """Dispose of the connection pool used by this _asyncio.AsyncEngine."""
        await cls.async_engine.dispose()

    @classmethod
    async def _get_session(cls) -> t.AsyncIterator[async_sessionmaker]:
        """Helper."""
        try:
            yield cls.AsyncSessionLocal
        except SQLAlchemyError as e:
            cls.log.exception(e)

    @classmethod
    async def get_session(cls) -> async_sessionmaker:
        """Get async db session.

        :return: _description_
        :rtype: async_sessionmaker
        """
        return await anext(cls._get_session())

    @classmethod
    async def iter_cursor(
        cls,
        query: str,
        params: t.Dict[str, t.Any],
        batch_size: int = 1_000,
        cur_name_: str | None = None,
    ) -> t.AsyncIterator[t.Sequence[Row]]:
        """Server side db cursor."""
        cur_name = f"cur_{cur_name_ or uuid4().hex}_{time.time_ns()}"
        query_cursor = f"DECLARE {cur_name} CURSOR FOR {query}"
        query_next_page = f"FETCH %(batch_size)s FROM {cur_name}"
        params_next_page = {"batch_size": batch_size}

        async with cls.async_engine.begin() as conn:
            await conn.execute(query_cursor, params)

            while True:
                res: Result = await conn.execute(query_next_page, params_next_page)
                batch = await res.fetchall()
                if not len(batch):
                    return
                yield batch
