"""HTTP-обёртка поверх httpx."""

from __future__ import annotations

import asyncio
import logging
from typing import Any

import httpx

from netschool_cap.exceptions import ServerUnavailable

log = logging.getLogger(__name__)

_DEFAULT_TIMEOUT = 30


class HttpSession:
    """Тонкая обёртка вокруг httpx.AsyncClient."""

    def __init__(
        self,
        base_url: str,
        *,
        timeout: int | None = None,
        proxy: str | None = None,
    ):
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout or _DEFAULT_TIMEOUT

        self._client = self._create_async_client(
            base_url=f"{self._base_url}/webapi",
            headers={
                "user-agent": "NetSchoolPy/1.0",
                "referer": self._base_url,
            },
            timeout=self._timeout,
            trust_env=False,
            follow_redirects=True,
            proxy=proxy,
            event_hooks={"response": [self._check_status]},
        )

    @staticmethod
    def _create_async_client(**kwargs: Any) -> httpx.AsyncClient:
        try:
            return httpx.AsyncClient(**kwargs)
        except TypeError as exc:
            proxy = kwargs.get("proxy")

            if proxy is None or "proxy" not in str(exc):
                raise

            legacy_kwargs = dict(kwargs)
            legacy_kwargs.pop("proxy", None)
            legacy_kwargs["proxies"] = proxy

            return httpx.AsyncClient(**legacy_kwargs)

    @property
    def base_url(self) -> str:
        return self._base_url

    @property
    def client(self) -> httpx.AsyncClient:
        return self._client

    def set_header(self, key: str, value: str) -> None:
        self._client.headers[key] = value

    def remove_header(self, key: str) -> None:
        self._client.headers.pop(key, None)

    def set_cookie(self, name: str, value: str) -> None:
        self._client.cookies.set(name, value)

    async def get(
        self,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        timeout: int | None = None,
        follow_redirects: bool = False,
        raw: bool = False,
    ) -> httpx.Response:

        if raw:
            path = f"/{path.lstrip('/')}"

        return await self._send(
            "GET",
            path,
            params=params,
            timeout=timeout,
            follow_redirects=follow_redirects,
        )

    async def post(
        self,
        path: str,
        *,
        data: Any | None = None,
        json: Any | None = None,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        timeout: int | None = None,
        raw: bool = False,
    ) -> httpx.Response:

        if raw:
            path = f"/{path.lstrip('/')}"

        return await self._send(
            "POST",
            path,
            data=data,
            json=json,
            params=params,
            headers=headers,
            timeout=timeout,
        )

    async def close(self) -> None:
        await self._client.aclose()

    async def _send(
        self,
        method: str,
        path: str,
        *,
        timeout: int | None = None,
        follow_redirects: bool = False,
        **kwargs: Any,
    ) -> httpx.Response:

        request_timeout = timeout or self._timeout
        retries = 3

        async def _do_request() -> httpx.Response:
            for attempt in range(retries):
                try:
                    request = self._client.build_request(
                        method,
                        path,
                        **{
                            k: v
                            for k, v in kwargs.items()
                            if v is not None
                        },
                    )

                    return await self._client.send(
                        request,
                        follow_redirects=follow_redirects,
                    )

                except httpx.ReadTimeout:
                    if attempt == retries - 1:
                        raise

                    await asyncio.sleep(0.25)

                except httpx.ConnectTimeout:
                    if attempt == retries - 1:
                        raise

                    await asyncio.sleep(0.5)

                except httpx.ConnectError:
                    if attempt == retries - 1:
                        raise

                    await asyncio.sleep(0.5)

                except httpx.HTTPStatusError as exc:
                    status = exc.response.status_code

                    if (
                        500 <= status < 600
                        and attempt < retries - 1
                    ):
                        await asyncio.sleep(0.5)
                        continue

                    raise

            raise ServerUnavailable("Не удалось выполнить запрос")

        try:
            return await asyncio.wait_for(
                _do_request(),
                timeout=request_timeout,
            )

        except asyncio.TimeoutError:
            raise ServerUnavailable(
                f"Сервер не ответил за {request_timeout} секунд"
            ) from None

        except (
            httpx.ConnectError,
            httpx.ConnectTimeout,
            httpx.ReadTimeout,
        ) as exc:
            raise ServerUnavailable(
                f"Ошибка соединения: {exc}"
            ) from exc

    @staticmethod
    async def _check_status(response: httpx.Response) -> None:
        if response.is_redirect:
            return

        if 500 <= response.status_code < 600:
            log.warning(
                "Server error %d for %s",
                response.status_code,
                response.url,
            )

        response.raise_for_status()