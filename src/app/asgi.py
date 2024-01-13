"""Application implementation - ASGI."""
import typing as t

import logging
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Request
from sqladmin import Admin
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.admin import UserAdmin
from src.app.controller.http import api_router, srv_router
from src.app.exceptions import HTTPException, http_exception_handler
from src.app.middleware import MetricsMiddleware
from src.app.modules import AiohttpClient, AsyncDBClient, ThreadClient, init_sentry
from src.config import settings

log = logging.getLogger(__name__)

DBSessionDep = t.Annotated[AsyncSession, Depends(AsyncDBClient.get_db_session)]


async def get_db_session(request: Request, db_session: DBSessionDep) -> None:
    """Provide session into each request."""
    request.state.db_session = db_session


@asynccontextmanager
async def lifespan(app: FastAPI) -> t.AsyncGenerator[None, t.Any]:
    """Define FastAPI startup shutdown event handler.

    Resources:
        1. https://fastapi.tiangolo.com/advanced/events/#startup-event
    """
    log.debug("Execute FastAPI startup event handler.")
    init_sentry()
    AiohttpClient.get_aiohttp_client()
    ThreadClient.get_thread_pool_client()
    AsyncDBClient.get_async_db_engine()
    yield
    await AiohttpClient.close_aiohttp_client()
    await ThreadClient.close_thread_pool_executor()
    await AsyncDBClient.close_db_engine()


def get_application() -> FastAPI:
    """Initialize FastAPI application.

    Returns:
       FastAPI: Application object instance.

    """
    log.debug("Initialize FastAPI application node.")
    app = FastAPI(
        title=settings.PROJECT_NAME,
        debug=settings.DEBUG,
        version=settings.VERSION,
        docs_url=settings.DOCS_URL,
        lifespan=lifespan,
        dependencies=[Depends(get_db_session)],
    )
    log.debug("Add helth check routes.")
    app.include_router(srv_router)
    log.debug("Add application routes.")
    app.include_router(api_router, prefix="/api")
    log.debug("Register global exception handler for custom HTTPException.")
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_middleware(MetricsMiddleware)

    log.debug("Add admin part.")
    admin = Admin(app, AsyncDBClient.get_async_db_engine())
    admin.add_view(UserAdmin)

    return app


app = get_application()
