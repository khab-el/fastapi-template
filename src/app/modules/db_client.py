import logging

import pandas as pd
import cx_Oracle_async
from cx_Oracle_async.pools import AsyncPoolWrapper

from src.config import settings


class AsyncDBClient:

    _connection_flg: bool = False
    async_engine: AsyncPoolWrapper
    log: logging.Logger = logging.getLogger(__name__)

    @classmethod
    def get_async_db_engine(cls) -> AsyncPoolWrapper:
        """Create async db engine.

        :return: _description_py
        :rtype: AsyncEngine
        """
        if not cls._connection_flg:
            cls.log.debug("Initialize AsyncEngine.")
            cls.async_engine = await cx_Oracle_async.create_pool(  # type: ignore
                host=settings.ORACLE_HOST,
                port=settings.ORACLE_PORT,
                user=settings.ORACLE_USER,
                password=settings.ORACLE_PASSWORD,
                service_name=settings.ORACLE_SERVICE_NAME,
                min = 2,
                max = 4,
            )
            cls._connection_flg = True
        return cls.async_engine

    @classmethod
    async def close_db_engine(cls) -> None:
        """Dispose of the connection pool used by this _asyncio.AsyncEngine."""
        if cls._connection_flg:
            await cls.async_engine.close()
            cls._connection_flg = False

    @staticmethod
    async def sql_exec(sql: str, async_engine: AsyncPoolWrapper) -> pd.DataFrame:
        async with async_engine.acquire() as connection:
            async with connection.cursor() as cursor:
                await cursor.execute(sql)
                result = await cursor.fetchall()
                columns = [desc[0] for desc in cursor._cursor.description]
                return pd.DataFrame(result, columns=columns)
