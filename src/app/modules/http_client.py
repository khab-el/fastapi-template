import typing as t

import asyncio
import logging
from socket import AF_INET

import aiohttp
import backoff
from aiohttp.helpers import BasicAuth
from aiohttp.typedefs import LooseHeaders, StrOrURL

from src.app.metrics import metrics
from src.config import settings

SIZE_POOL_AIOHTTP = 100


class AiohttpClient:
    """Aiohttp session client utility.

    Utility class for handling HTTP async request for whole FastAPI application
    scope.
    Used aiohttp instead httpx module based on benchmark:
    https://gist.github.com/imbolc/15cab07811c32e7d50cc12f380f7f62f
    """

    _client_flg: bool = False
    sem: asyncio.Semaphore = asyncio.Semaphore(10)
    aiohttp_client: aiohttp.ClientSession
    log: logging.Logger = logging.getLogger(__name__)

    @classmethod
    def get_aiohttp_client(cls) -> aiohttp.ClientSession:
        """Create httpx client session object instance.

        Returns:
            AsyncClient: AsyncClient object instance.

        """
        if not cls._client_flg:
            cls.log.debug("Initialize AiohttpClient session.")
            timeout = aiohttp.ClientTimeout(total=2)
            connector = aiohttp.TCPConnector(
                family=AF_INET,
                limit_per_host=SIZE_POOL_AIOHTTP,
            )
            cls.aiohttp_client = aiohttp.ClientSession(
                timeout=timeout,
                connector=connector,
            )
            cls._client_flg = True

        return cls.aiohttp_client

    @classmethod
    async def close_aiohttp_client(cls) -> None:
        """Close aiohttp client session."""
        if cls._client_flg:
            cls.log.debug("Close AiohttpClient session.")
            await cls.aiohttp_client.close()
            cls._client_flg = False

    @classmethod
    @backoff.on_exception(
        backoff.expo,
        aiohttp.ClientError,
        max_tries=settings.MAX_TRIES,
    )
    @metrics.observe_request
    async def _request(
        cls,
        method: str,
        url: StrOrURL,
        params: t.Optional[t.Mapping[str, str]] = None,
        headers: t.Optional[LooseHeaders] = None,
        data: t.Any = None,
        json: t.Any = None,
        auth: t.Optional[BasicAuth] = None,
    ) -> aiohttp.ClientResponse:
        """Support func for making request.

        :param method: _description_
        :type method: str
        :param url: _description_
        :type url: StrOrURL
        :param params: _description_, defaults to None
        :type params: t.Optional[t.Mapping[str, str]], optional
        :param headers: _description_, defaults to None
        :type headers: t.Optional[LooseHeaders], optional
        :param data: _description_, defaults to None
        :type data: t.Any, optional
        :param json: _description_, defaults to None
        :type json: t.Any, optional
        :param auth: _description_, defaults to None
        :type auth: t.Optional[BasicAuth], optional
        :return: _description_
        :rtype: aiohttp.ClientResponse
        """
        async with cls.sem:
            resp = await cls.get_aiohttp_client().request(
                method=method,
                url=url,
                params=params,
                data=data,
                json=json,
                headers=headers,
                auth=auth,
            )
            if resp.status >= 500:
                resp.raise_for_status()
            return resp

    @classmethod
    async def get(
        cls,
        url: StrOrURL,
        params: t.Optional[t.Mapping[str, str]] = None,
        headers: t.Optional[LooseHeaders] = None,
        auth: t.Optional[BasicAuth] = None,
    ) -> aiohttp.ClientResponse:
        """Execute HTTP GET request.

        :param url: _description_
        :type url: StrOrURL
        :param params: _description_, defaults to None
        :type params: t.Optional[t.Mapping[str, str]], optional
        :param headers: _description_, defaults to None
        :type headers: t.Optional[LooseHeaders], optional
        :param auth: _description_, defaults to None
        :type auth: t.Optional[BasicAuth], optional
        :return: _description_
        :rtype: aiohttp.ClientResponse
        """
        return await cls._request(
            method="GET",
            url=url,
            params=params,
            headers=headers,
            auth=auth,
        )

    @classmethod
    async def post(
        cls,
        url: StrOrURL,
        params: t.Optional[t.Mapping[str, str]] = None,
        headers: t.Optional[LooseHeaders] = None,
        data: t.Any = None,
        json: t.Any = None,
        auth: t.Optional[BasicAuth] = None,
    ) -> aiohttp.ClientResponse:
        """Execute HTTP POST request.

        :param url: _description_
        :type url: StrOrURL
        :param params: _description_, defaults to None
        :type params: t.Optional[t.Mapping[str, str]], optional
        :param headers: _description_, defaults to None
        :type headers: t.Optional[LooseHeaders], optional
        :param data: _description_, defaults to None
        :type data: t.Any, optional
        :param json: _description_, defaults to None
        :type json: t.Any, optional
        :param auth: _description_, defaults to None
        :type auth: t.Optional[BasicAuth], optional
        :return: _description_
        :rtype: aiohttp.ClientResponse
        """
        return await cls._request(
            method="POST",
            url=url,
            data=data,
            json=json,
            params=params,
            headers=headers,
            auth=auth,
        )
