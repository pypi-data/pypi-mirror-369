import hashlib
import hmac
import time
from typing import Any, Dict, Optional
from urllib.parse import urlparse

import aiohttp
import requests


class ApolloClient:

    def __init__(self, server_url: str, app_id: str, secret: Optional[str] = None):
        self._server_url = server_url
        self._app_id = app_id
        self._secret = secret

    def fetch_config(self, cluster: str = "default", namespace: str = "application") -> Dict[str, str]:
        url = f"{self._server_url}/configs/{self._app_id}/{cluster}/{namespace}"
        result = self._http_get(url=url)
        return result["configurations"]

    async def async_fetch_config(self, cluster: str = "default", namespace: str = "application") -> Dict[str, str]:
        url = f"{self._server_url}/configs/{self._app_id}/{cluster}/{namespace}"
        result = await self._async_http_get(url=url)
        return result["configurations"]

    def _http_get(self, url: str) -> Dict[str, Any]:
        headers = self._build_auth_headers(url, self._app_id, self._secret) if self._secret else None
        resp = requests.get(url=url, headers=headers)
        resp.raise_for_status()
        return resp.json()

    async def _async_http_get(self, url: str) -> Dict[str, Any]:
        headers = self._build_auth_headers(url, self._app_id, self._secret) if self._secret else None
        async with aiohttp.ClientSession() as session:
            async with session.get(url=url, headers=headers) as resp:
                resp.raise_for_status()
                return await resp.json()

    @staticmethod
    def _build_auth_headers(
            url: str,
            app_id: str,
            secret: str
    ) -> Dict[str, str]:
        timestamp = str(int(time.time() * 1000))

        parsed = urlparse(url)
        path_with_query = parsed.path
        if parsed.query:
            path_with_query += "?" + parsed.query

        string_to_sign = f"{timestamp}\n{path_with_query}"

        signature = hmac.new(
            secret.encode("utf-8"),
            string_to_sign.encode("utf-8"),
            hashlib.sha1
        ).hexdigest()

        return {
            "Authorization": f"{app_id}:{signature}",
            "Timestamp": timestamp,
        }
