import typing as t

import logging

from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

from src.app.exceptions import ApiExceptionResponse, ApiInvalidResponse, ApiError
from src.app.modules import AlreadyExistError, leaf_generator

log = logging.getLogger(__name__)


def pyd2hr(exc: RequestValidationError) -> list[dict[str, t.Any]]:
    """Pydantic error format."""
    unique_errors = {
        (".".join(map(str, err["loc"])), err["msg"])
        for err in exc.errors()
        if err["type"] != "type_error.dict"  # https://github.com/samuelcolvin/pydantic/issues/2973
    }
    return [{"field": e[0], "message": e[1]} for e in unique_errors]


async def log_exception(request: Request, exception: t.Type[Exception] | None) -> None:
    """Log exception."""
    if not exception:
        return

    method = request.scope["method"]
    path = request.url.path
    req_params = request.query_params

    log.exception(
        """method - %(method)s
        path - %(path)s
        req params - %(req_params)s
        status_code - 400
        error - %(exc)s""",
        {
            "method": method,
            "path": path,
            "req_params": req_params,
            "exc": str(exception),
        },
        exc_info=True,
    )


def prepare_bad_response(errors: list[ApiError], status: int, validation_error: bool = False) -> JSONResponse:
    """Prepare bad response.

    :param errors: _description_
    :type errors: list[ApiError]
    :param status: _description_
    :type status: int
    :return: _description_
    :rtype: JSONResponse
    """
    if validation_error:
        data = ApiInvalidResponse(errors=errors)
    else:
        data = ApiExceptionResponse(errors=errors)
    return JSONResponse(
        status_code=status,
        content=data.model_dump(),
    )


def prepare_exception_group_errors(eg: ExceptionGroup) -> tuple[list[dict[str, t.Any]], Exception]:
    """Parse catched exception group error.

    :param eg: _description_
    :type eg: ExceptionGroup
    :return: _description_
    :rtype: list[dict[str, t.Any]]
    """
    errors = []
    for (_, (exc, _)) in enumerate(leaf_generator(eg)):
        if isinstance(exc, AlreadyExistError):
            errors.append({"message": str(exc)})
    return errors, exc


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
        exc = None
        try:
            response = await call_next(request)
        except RequestValidationError as exc:
            errors = pyd2hr(exc)
            response = prepare_bad_response(errors=errors, status=status.HTTP_400_BAD_REQUEST, validation_error=True)
        except ExceptionGroup as eg:
            errors, exc = prepare_exception_group_errors(eg=eg)
            response = prepare_bad_response(errors=errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as exc:
            errors = [{"message": f"{exc.__class__} - {str(exc)}"}]
            response = prepare_bad_response(errors=errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        await log_exception(request, exc)

        return response
