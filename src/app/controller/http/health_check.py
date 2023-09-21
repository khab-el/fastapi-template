import logging

import prometheus_client as pc
from fastapi import APIRouter, Request, status
from fastapi.responses import PlainTextResponse
from sqlalchemy import text

from src.app.dto import ErrorResponse, ReadyResponse
from src.app.exceptions import HTTPException
from src.app.modules import AsyncDBClient

log = logging.getLogger(__name__)

srv_router = APIRouter(
    tags=["helth_check"],
    # include_in_schema=False,
)


@srv_router.get(
    "/ping",
    response_model=ReadyResponse,
    summary="Simple health check.",
    status_code=200,
    responses={502: {"model": ErrorResponse}},
)
async def ping(request: Request) -> ReadyResponse:
    """ping."""
    try:
        async with AsyncDBClient.async_engine.begin() as conn:
            res = await conn.execute(text("SELECT 1;"))
            return ReadyResponse(status=f"ok: true; db: {bool(res.scalar())}")
    except Exception as exc:
        log.exception("ping db fail")
        raise HTTPException(
            status.HTTP_502_BAD_GATEWAY,
            content=ErrorResponse(
                code=status.HTTP_502_BAD_GATEWAY,
                message="Could not connect to PostgreSQL",
            ).model_dump(exclude_none=True),
        ) from exc


@srv_router.get("/metrics")
async def metrics() -> PlainTextResponse:
    """Prometheus metrics."""
    return PlainTextResponse(pc.generate_latest())
