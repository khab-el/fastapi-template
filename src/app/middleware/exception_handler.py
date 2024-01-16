import typing as t

import logging

from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

from src.app.exceptions import ApiExceptionResponse, ApiInvalidResponse

Exc = t.TypeVar("Exc", bound=Exception)

log = logging.getLogger(__name__)


def pyd2hr(exc: RequestValidationError) -> list[dict[str, t.Any]]:
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


class ExceptionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        """Handle unexpected error and count prometheus metrics.

        :param request: _description_
        :type request: Request
        :param call_next: _description_
        :type call_next: RequestResponseEndpoint
        :return: _description_
        :rtype: Response
        """
        try:
            response = await call_next(request)
        except RequestValidationError as exc:
            await log_exception(request, exc)
            errors = pyd2hr(exc)
            data = ApiInvalidResponse(errors=errors)
            response = JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=data.model_dump(),
            )
        except Exception as exc:
            await log_exception(request, exc)
            errors = [{"message": f"{exc.__class__} - {str(exc)}"}]
            data = ApiExceptionResponse(errors=errors)
            response = JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=data.model_dump(),
            )

        return response
