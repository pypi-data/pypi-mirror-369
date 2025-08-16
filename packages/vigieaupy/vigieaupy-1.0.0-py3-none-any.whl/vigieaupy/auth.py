"""Class for request."""

import asyncio
import json
import logging
import socket
from typing import Any

from aiohttp import ClientError, ClientResponseError, ClientSession

_LOGGER = logging.getLogger(__name__)


class HTTPRequest:
    """Authentication for API requests."""

    TIMEOUT = 120  # Default timeout for requests in seconds

    def __init__(
        self, session: ClientSession | None = None, timeout: int = TIMEOUT
    ) -> None:
        """Initialize."""
        self.timeout = timeout
        self.session = session or ClientSession()

    async def async_request(self, path: str, method: str = "get", **kwargs: Any) -> Any:
        """Make an authenticated request to the API."""
        contents = {}
        response = None
        try:
            async with asyncio.timeout(self.timeout):
                if self.session is None:
                    raise HttpRequestError("ClientSession is not initialized.")
                _LOGGER.debug("Request: %s (%s) - %s", path, method, kwargs)
                response = await self.session.request(method, path, **kwargs)
                contents = await response.json()
                response.raise_for_status()
        except (asyncio.CancelledError, asyncio.TimeoutError) as error:
            raise TimeoutExceededError(
                "Timeout occurred while connecting to API."
            ) from error
        except ClientResponseError as error:
            if response is not None:
                message = (await response.read()).decode("utf8")
                if "application/json" in response.headers.get("Content-Type", ""):
                    msg = json.loads(message)
                    raise RequestException(msg.get("detail", msg)) from error
                raise RequestException({"message": message}) from error
            else:
                raise RequestException({"message": "No response received."}) from error
        except (ClientError, socket.gaierror) as error:
            raise HttpRequestError(
                "Error occurred while communicating with API."
            ) from error

        return contents

    async def async_close(self) -> None:
        """Close the HTTP session."""
        if self.session:
            await self.session.close()
            self.session = None


class HttpRequestError(Exception):
    """Base exception for HTTP request errors."""


class TimeoutExceededError(HttpRequestError):
    """Exception raised when a request times out."""


class RequestException(HttpRequestError):
    """Exception raised for errors in the request."""
