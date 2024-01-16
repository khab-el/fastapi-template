"""Application implementation - custom FastAPI HTTP exception with handler."""
from typing import Dict, TypeVar

import logging

from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel

Exc = TypeVar("Exc", bound=Exception)

log = logging.getLogger(__name__)


class ApiError(BaseModel):
    message: str


class ApiErrorResponse(BaseModel):
    success: bool = False
    errors: list[ApiError]


def pyd2hr(exc: RequestValidationError) -> list[Dict]:
    """Pydantic error format."""
    unique_errors = {
        (".".join(map(str, err["loc"])), err["msg"])
        for err in exc.errors()
        if err["type"] != "type_error.dict"  # https://github.com/samuelcolvin/pydantic/issues/2973
    }
    return [{"field": e[0], "message": e[1]} for e in unique_errors]


async def log_exception(request: Request, exception: Exc) -> None:
    """Log exception."""
    method = request.scope["method"]
    path = request.url.path
    req_params = request.query_params
    req_body = await request.body()
    log.exception(
        """method - %(method)s
        path - %(path)s
        req body - %(req_body)s
        req params - %(req_params)s
        status_code - 400
        error - %(exc)s""",
        {
            "method": method,
            "path": path,
            "req_params": req_params,
            "req_body": req_body,
            "exc": str(exception),
        },
    )


async def request_validation_exception_handler(
    request: Request,
    exception: RequestValidationError,
) -> JSONResponse:
    """Define custom RequestValidationError handler."""
    await log_exception(request, exception)
    errors = pyd2hr(exception)
    data = ApiErrorResponse(errors=errors)
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=data.model_dump(),
    )


async def global_exception_handler(
    request: Request,
    exception: Exception,
) -> JSONResponse:
    """Define custom Global Exception handler."""
    await log_exception(request, exception)
    errors = [{"message": f"{exception.__class__}: {str(exception)}"}]
    data = ApiErrorResponse(errors=errors)
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=data.model_dump(),
    )
