import typing as t

import time
from urllib.parse import urlparse

import prometheus_client as pc
from httpx import Response

from src.config import settings

T = t.TypeVar("T")
P = t.ParamSpec("P")


requests = pc.Counter(
    documentation="api requests total",
    name="requests_total",
    namespace=settings.PROJECT_NAME,
    labelnames=["path", "method"],
)

responses = pc.Counter(
    documentation="api response status codes",
    name="responses_total",
    namespace=settings.PROJECT_NAME,
    labelnames=["path", "method", "status"],
)

# fmt: off
timings = pc.Histogram(
    documentation="api successfull responsees",
    name="response_duration",
    unit="seconds",
    namespace=settings.PROJECT_NAME,
    labelnames=["path", "method"],
    buckets=(
        0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0,
        1.25, 1.5, 1.75, 2.0, 2.5, 3.0, 3.5, 4.0, 5.0, 10.0,
        pc.utils.INF,
    ),
)
# fmt: on

request_timings = pc.Histogram(
    documentation="request time",
    name="request_duration",
    unit="seconds",
    namespace=settings.PROJECT_NAME,
    labelnames=["entity"],
)


def observe_request(func: t.Callable[P, T]) -> t.Callable[P, T]:
    """Observe request to service.

    :param func: _description_
    :type func: t.Callable[P, T]
    :return: _description_
    :rtype: t.Callable[P, T]
    """

    async def _wrap(*args: P.args, **kwargs: P.kwargs) -> Response:
        ts_start = time.monotonic()
        try:
            resp: Response = await func(*args, **kwargs)
            elapsed = time.monotonic() - ts_start

            entity = urlparse(resp.url).netloc

            request_timings.labels(entity).observe(elapsed)

            return resp
        except Exception as e:
            raise e

    return _wrap
