"""Application implementation - ASGI."""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqladmin import Admin

from src.app.admin import UserAdmin
from src.app.exceptions import HTTPException, http_exception_handler
from src.app.middleware import MetricsMiddleware
from src.app.modules import AiohttpClient, ThreadClient, AsyncDBClient, init_sentry
from src.app.controller.http import api_router
from src.config import settings

log = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
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
    )
    log.debug("Add application routes.")
    app.include_router(api_router, prefix="/api")
    log.debug("Register global exception handler for custom HTTPException.")
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_middleware(MetricsMiddleware)

    log.debug("Add admin part.")
    admin = Admin(app, AsyncDBClient.get_async_db_engine())
    admin.add_view(UserAdmin)

    return app
