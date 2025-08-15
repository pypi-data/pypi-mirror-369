"""Exception classes for SFMC API client."""

import contextlib

import httpx


class SFMCError(Exception):
    """Base exception for all SFMC API errors."""

    def __init__(self, message: str, response: httpx.Response | None = None):
        super().__init__(message)
        self.response = response
        self.status_code = response.status_code if response else None


class SFMCAuthenticationError(SFMCError):
    """Authentication-related errors."""

    pass


class SFMCAuthorizationError(SFMCError):
    """Authorization/permission-related errors."""

    pass


class SFMCValidationError(SFMCError):
    """Request validation errors."""

    pass


class SFMCNotFoundError(SFMCError):
    """Resource not found errors."""

    pass


class SFMCRateLimitError(SFMCError):
    """Rate limiting errors."""

    def __init__(
        self,
        message: str,
        response: httpx.Response | None = None,
        retry_after: int | None = None,
    ):
        super().__init__(message, response)
        self.retry_after = retry_after


class SFMCServerError(SFMCError):
    """Server-side errors."""

    pass


class SFMCConnectionError(SFMCError):
    """Network/connection errors."""

    pass


def map_http_error(response: httpx.Response) -> SFMCError:
    """Map HTTP status codes to appropriate SFMC exceptions."""
    status_code = response.status_code

    try:
        error_data = response.json()
        message = error_data.get("message", f"HTTP {status_code} error")
    except Exception:
        message = f"HTTP {status_code} error: {response.text}"

    if status_code == 401:
        return SFMCAuthenticationError(message, response)
    elif status_code == 403:
        return SFMCAuthorizationError(message, response)
    elif status_code == 404:
        return SFMCNotFoundError(message, response)
    elif status_code == 422:
        return SFMCValidationError(message, response)
    elif status_code == 429:
        retry_after = None
        if "retry-after" in response.headers:
            with contextlib.suppress(ValueError):
                retry_after = int(response.headers["retry-after"])
        return SFMCRateLimitError(message, response, retry_after)
    elif 500 <= status_code < 600:
        return SFMCServerError(message, response)
    else:
        return SFMCError(message, response)
