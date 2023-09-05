import typing as t

import asyncio
import concurrent.futures
import logging


class ThreadClient:
    """Thread pool executer utility.

    Attributes:
        n_workers (int, optional): The maximum number of threads that can be used to
        execute the given calls.
        thread_executor (concurrent.futures.ThreadPoolExecutor, optional): ThreadPoolExecutor instance.

    """

    n_workers: int = 2
    thread_executor: t.Optional[concurrent.futures.ThreadPoolExecutor] = None
    loop: t.Optional[asyncio.AbstractEventLoop] = None
    log: logging.Logger = logging.getLogger(__name__)

    @classmethod
    def get_thread_pool_client(cls) -> concurrent.futures.ThreadPoolExecutor:
        """Create Thread pool."""
        if cls.thread_executor is None:
            cls.thread_executor = concurrent.futures.ThreadPoolExecutor(cls.n_workers)
            cls.loop = asyncio.get_running_loop()

        return cls.thread_executor

    @classmethod
    async def close_thread_pool_executor(cls) -> None:
        """Close tread pool."""
        cls.thread_executor.shutdown(wait=True)

    @classmethod
    async def execute(cls, func: t.Callable, *args: t.Any) -> t.Any:
        """Exec func in treads."""
        thread_executor = cls.get_thread_pool_client()

        cls.log.debug(f"Started execute func {func.__name__}")
        result = await cls.loop.run_in_executor(thread_executor, func, *args)
        return result
