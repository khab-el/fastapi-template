import logging
import time

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

from src.app.metrics import metrics

log = logging.getLogger(__name__)


class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        """Handle unexpected error and count prometheus metrics.

        :param request: _description_
        :type request: Request
        :param call_next: _description_
        :type call_next: RequestResponseEndpoint
        :return: _description_
        :rtype: Response
        """
        ts_start = time.monotonic()
        method = request.scope["method"]
        path = request.url.path
        metrics.requests.labels(path, method).inc()

        response = await call_next(request)

        elapsed = time.monotonic() - ts_start
        metrics.timings.labels(path, method).observe(elapsed)

        metrics.responses.labels(path, method, response.status_code).inc()
        return response
