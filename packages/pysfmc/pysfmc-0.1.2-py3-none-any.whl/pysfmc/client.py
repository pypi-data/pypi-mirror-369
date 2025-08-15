"""HTTP client implementations for SFMC API."""

from abc import ABC, abstractmethod
from typing import Any
from urllib.parse import urljoin

import httpx
from pydantic import BaseModel

from .auth import AsyncSFMCAuthenticator, SFMCAuthenticator, SFMCSettings
from .exceptions import SFMCConnectionError, map_http_error


class BaseClient(ABC):
    """Abstract base class for SFMC API clients."""

    def __init__(self, settings: SFMCSettings | None = None):
        self.settings = settings or SFMCSettings()

    @abstractmethod
    def get(self, endpoint: str, **kwargs) -> dict[str, Any]:
        """Make a GET request."""
        pass

    @abstractmethod
    def post(self, endpoint: str, **kwargs) -> dict[str, Any]:
        """Make a POST request."""
        pass

    @abstractmethod
    def put(self, endpoint: str, **kwargs) -> dict[str, Any]:
        """Make a PUT request."""
        pass

    @abstractmethod
    def patch(self, endpoint: str, **kwargs) -> dict[str, Any]:
        """Make a PATCH request."""
        pass

    @abstractmethod
    def delete(self, endpoint: str, **kwargs) -> dict[str, Any]:
        """Make a DELETE request."""
        pass

    @abstractmethod
    def close(self) -> None:
        """Close the client and cleanup resources."""
        pass


class SFMCClient(BaseClient):
    """Synchronous SFMC API client."""

    def __init__(
        self,
        settings: SFMCSettings | None = None,
        http_client: httpx.Client | None = None,
        timeout: float = 30.0,
    ):
        super().__init__(settings)
        self._http_client = http_client or httpx.Client(timeout=timeout)
        self._authenticator = SFMCAuthenticator(self.settings, self._http_client)
        self._assets = None

    def _make_request(
        self,
        method: str,
        endpoint: str,
        json: dict[str, Any] | BaseModel | None = None,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        **kwargs,
    ) -> dict[str, Any]:
        """Make an authenticated HTTP request."""
        # Get base URL and auth headers
        base_url = self._authenticator.get_rest_base_url()
        auth_headers = self._authenticator.get_auth_header()

        # Build full URL
        url = urljoin(base_url, endpoint.lstrip("/"))

        # Prepare headers
        request_headers = {"Content-Type": "application/json"}
        request_headers.update(auth_headers)
        if headers:
            request_headers.update(headers)

        # Prepare JSON payload
        json_data = None
        if json is not None:
            if isinstance(json, BaseModel):
                json_data = json.model_dump(exclude_none=True, by_alias=True)
            else:
                json_data = json

        try:
            response = self._http_client.request(
                method=method,
                url=url,
                json=json_data,
                params=params,
                headers=request_headers,
                **kwargs,
            )

            # Handle HTTP errors
            if not response.is_success:
                raise map_http_error(response)

            # Return JSON response or empty dict for no content
            if response.status_code == 204:  # No Content
                return {}

            return response.json()

        except httpx.RequestError as e:
            raise SFMCConnectionError(f"Connection error: {e}") from e

    def get(
        self, endpoint: str, params: dict[str, Any] | None = None, **kwargs
    ) -> dict[str, Any]:
        """Make a GET request."""
        return self._make_request("GET", endpoint, params=params, **kwargs)

    def post(
        self,
        endpoint: str,
        json: dict[str, Any] | BaseModel | None = None,
        **kwargs,
    ) -> dict[str, Any]:
        """Make a POST request."""
        return self._make_request("POST", endpoint, json=json, **kwargs)

    def put(
        self,
        endpoint: str,
        json: dict[str, Any] | BaseModel | None = None,
        **kwargs,
    ) -> dict[str, Any]:
        """Make a PUT request."""
        return self._make_request("PUT", endpoint, json=json, **kwargs)

    def patch(
        self,
        endpoint: str,
        json: dict[str, Any] | BaseModel | None = None,
        **kwargs,
    ) -> dict[str, Any]:
        """Make a PATCH request."""
        return self._make_request("PATCH", endpoint, json=json, **kwargs)

    def delete(self, endpoint: str, **kwargs) -> dict[str, Any]:
        """Make a DELETE request."""
        return self._make_request("DELETE", endpoint, **kwargs)

    @property
    def assets(self):
        """Access to Assets (Content Builder) API operations."""
        if self._assets is None:
            from .assets import AssetsClient  # noqa: PLC0415

            self._assets = AssetsClient(self)
        return self._assets

    def close(self) -> None:
        """Close the client and cleanup resources."""
        self._authenticator.close()
        self._http_client.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class AsyncSFMCClient(BaseClient):
    """Asynchronous SFMC API client."""

    def __init__(
        self,
        settings: SFMCSettings | None = None,
        http_client: httpx.AsyncClient | None = None,
        timeout: float = 30.0,
    ):
        super().__init__(settings)
        self._http_client = http_client or httpx.AsyncClient(timeout=timeout)
        self._authenticator = AsyncSFMCAuthenticator(self.settings, self._http_client)
        self._assets = None

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        json: dict[str, Any] | BaseModel | None = None,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        **kwargs,
    ) -> dict[str, Any]:
        """Make an authenticated HTTP request."""
        # Get base URL and auth headers
        base_url = await self._authenticator.get_rest_base_url()
        auth_headers = await self._authenticator.get_auth_header()

        # Build full URL
        url = urljoin(base_url, endpoint.lstrip("/"))

        # Prepare headers
        request_headers = {"Content-Type": "application/json"}
        request_headers.update(auth_headers)
        if headers:
            request_headers.update(headers)

        # Prepare JSON payload
        json_data = None
        if json is not None:
            if isinstance(json, BaseModel):
                json_data = json.model_dump(exclude_none=True, by_alias=True)
            else:
                json_data = json

        try:
            response = await self._http_client.request(
                method=method,
                url=url,
                json=json_data,
                params=params,
                headers=request_headers,
                **kwargs,
            )

            # Handle HTTP errors
            if not response.is_success:
                raise map_http_error(response)

            # Return JSON response or empty dict for no content
            if response.status_code == 204:  # No Content
                return {}

            return response.json()

        except httpx.RequestError as e:
            raise SFMCConnectionError(f"Connection error: {e}") from e

    async def get(
        self, endpoint: str, params: dict[str, Any] | None = None, **kwargs
    ) -> dict[str, Any]:
        """Make a GET request."""
        return await self._make_request("GET", endpoint, params=params, **kwargs)

    async def post(
        self,
        endpoint: str,
        json: dict[str, Any] | BaseModel | None = None,
        **kwargs,
    ) -> dict[str, Any]:
        """Make a POST request."""
        return await self._make_request("POST", endpoint, json=json, **kwargs)

    async def put(
        self,
        endpoint: str,
        json: dict[str, Any] | BaseModel | None = None,
        **kwargs,
    ) -> dict[str, Any]:
        """Make a PUT request."""
        return await self._make_request("PUT", endpoint, json=json, **kwargs)

    async def patch(
        self,
        endpoint: str,
        json: dict[str, Any] | BaseModel | None = None,
        **kwargs,
    ) -> dict[str, Any]:
        """Make a PATCH request."""
        return await self._make_request("PATCH", endpoint, json=json, **kwargs)

    async def delete(self, endpoint: str, **kwargs) -> dict[str, Any]:
        """Make a DELETE request."""
        return await self._make_request("DELETE", endpoint, **kwargs)

    @property
    def assets(self):
        """Access to Assets (Content Builder) API operations."""
        if self._assets is None:
            from .assets import AsyncAssetsClient  # noqa: PLC0415

            self._assets = AsyncAssetsClient(self)
        return self._assets

    async def close(self) -> None:
        """Close the client and cleanup resources."""
        await self._authenticator.close()
        await self._http_client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
